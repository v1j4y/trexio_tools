#!/usr/bin/env python3

import trexio
import numpy as np
from . import nucleus as trexio_nucleus
from . import basis as trexio_basis
from . import ao as trexio_ao

try:
    import qmckl
    def run(trexio_file, n_points):
        """
        Computes numerically the overlap matrix in the AO basis and compares it to
        the matrix stored in the file.
        """

        if not trexio.has_ao_1e_int_overlap(trexio_file):
          raise Exception(
            "One-electron overlap integrals are missing in the TREXIO file. Required for check-basis."
            )

        trexio_filename = trexio_file.filename
        context = qmckl.context_create()
        qmckl.trexio_read(context, trexio_filename)

        ao = trexio_ao.read(trexio_file)
        basis = ao["basis"]
        nucleus = basis["nucleus"]
        assert basis["type"] == "Gaussian"

        rmin = np.array( list([ np.min(nucleus["coord"][:,a]) for a in range(3) ]) )
        rmax = np.array( list([ np.max(nucleus["coord"][:,a]) for a in range(3) ]) )

        shift = np.array([8.,8.,8.])
        linspace = [ None for i in range(3) ]
        step = [ None for i in range(3) ]
        for a in range(3):
          linspace[a], step[a] = np.linspace(rmin[a]-shift[a], rmax[a]+shift[a], num=n_points, retstep=True)

        print("Integration steps:", step)
        dv = step[0]*step[1]*step[2]

        point = []
        for x in linspace[0]:
          #print(".",end='',flush=True)
          for y in linspace[1]:
            for z in linspace[2]:
               point += [ [x, y, z] ]
        point = np.array(point)
        point_num = len(point)
        ao_num = ao["num"]

        qmckl.set_point(context, 'N', point_num, np.reshape(point, (point_num*3)))
        chi = qmckl.get_ao_basis_ao_value(context, point_num*ao_num)
        chi = np.reshape( chi, (point_num,ao_num) )
        S = chi.T @ chi * dv
        print()

        S_ex = trexio.read_ao_1e_int_overlap(trexio_file)

        # This produces a lot of output for large molecules, maybe wrap up in ``if debug`` statement ?
        for i in range(ao_num):
          for j in range(i,ao_num):
            print("%3d %3d %15f %15f"%(i,j,S[i,j],S_ex[i,j]))
        S_diff = S - S_ex
        print("Norm of the error: %f"%(np.linalg.norm(S_diff)))




except ImportError:

    def run(trexio_file, n_points):
        """
        Computes numerically the overlap matrix in the AO basis and compares it to
        the matrix stored in the file.
        """

        if not trexio.has_ao_1e_int_overlap(trexio_file):
          raise Exception(
            "One-electron overlap integrals are missing in the TREXIO file. Required for check-basis."
            )

        ao = trexio_ao.read(trexio_file)
        basis = ao["basis"]
        nucleus = basis["nucleus"]
        assert basis["type"] == "Gaussian"

        rmin = np.array( list([ np.min(nucleus["coord"][:,a]) for a in range(3) ]) )
        rmax = np.array( list([ np.max(nucleus["coord"][:,a]) for a in range(3) ]) )

        shift = np.array([8.,8.,8.])
        linspace = [ None for i in range(3) ]
        step = [ None for i in range(3) ]
        for a in range(3):
          linspace[a], step[a] = np.linspace(rmin[a]-shift[a], rmax[a]+shift[a], num=n_points, retstep=True)

        print("Integration steps:", step)
        dv = step[0]*step[1]*step[2]

        S = np.zeros( [ ao["num"], ao["num"]] )
        for x in linspace[0]:
          #print(".",end='',flush=True)
          for y in linspace[1]:
            for z in linspace[2]:
               chi = trexio_ao.value(ao, np.array( [x,y,z] ) )
               S += np.outer(chi, chi)*dv
        print()

        S_ex = trexio.read_ao_1e_int_overlap(trexio_file)
        ao_num = ao["num"]

        # This produces a lot of output for large molecules, maybe wrap up in ``if debug`` statement ?
        for i in range(ao_num):
          for j in range(i,ao_num):
            print("%3d %3d %15f %15f"%(i,j,S[i][j],S_ex[i,j]))
        S_diff = S - S_ex
        print("Norm of the error: %f"%(np.linalg.norm(S_diff)))



