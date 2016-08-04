
from pySDC import CollocationClasses as collclass

from examples.fenics_heat1d.ProblemClass import fenics_heat
from pySDC.datatype_classes.fenics_mesh import fenics_mesh, rhs_fenics_mesh
from examples.fenics_heat1d.TransferClass import mesh_to_mesh_fenics
from pySDC.sweeper_classes.mass_matrix_imex import mass_matrix_imex
import pySDC.PFASST_blockwise as mp
# import pySDC.PFASST_stepwise as mp
from pySDC import Log
from pySDC.Stats import grep_stats, sort_stats

import dolfin as df

from collections import namedtuple
import pickle



if __name__ == "__main__":

    ID = namedtuple('ID', ['c_nvars', 'dt'])

    # set global logger (remove this if you do not want the output at all)
    # logger = Log.setup_custom_logger('root')

    num_procs = 1

    # This comes as read-in for the level class
    lparams = {}
    lparams['restol'] = 5E-09

    # This comes as read-in for the steps
    sparams = {}
    sparams['maxiter'] = 20

    # This comes as read-in for the sweeper class
    swparams = {}
    swparams['collocation_class'] = collclass.CollGaussRadau_Right
    swparams['num_nodes'] = 3

    # This comes as read-in for the transfer operations
    tparams = {}
    tparams['finter'] = False

    # This comes as read-in for the problem class
    pparams = {}
    pparams['nu'] = 0.1
    pparams['k'] = 1
    pparams['t0'] = 0.0
    pparams['family'] = 'CG'
    pparams['order'] = [4]
    pparams['refinements'] = [1,0]

    # setup parameters "in time"
    t0 = 0.0
    Tend = 2.0

    dt_list = [Tend/(2**i) for i in range(0,7,1)]
    c_nvars_list = [2**i for i in range(2,7)]
    # dt_list = [2.0]
    # c_nvars_list = [512]

    results = {}
    # results['description'] = (pparams,swparams)

    for c_nvars in c_nvars_list:

        pparams['c_nvars'] = c_nvars

        # Fill description dictionary for easy hierarchy creation
        description = {}
        description['problem_class'] = fenics_heat
        description['problem_params'] = pparams
        description['dtype_u'] = fenics_mesh
        description['dtype_f'] = rhs_fenics_mesh
        description['sweeper_class'] = mass_matrix_imex
        description['sweeper_params'] = swparams
        description['level_params'] = lparams
        description['transfer_class'] = mesh_to_mesh_fenics
        description['transfer_params'] = tparams

        # quickly generate block of steps
        MS = mp.generate_steps(num_procs, sparams, description)

        # get initial values on finest level
        P = MS[0].levels[0].prob
        uinit = P.u_exact(t0)

        # compute exact solution to compare
        uex = P.u_exact(Tend)

        for dt in dt_list:

            print('Working on: c_nvars = %s, dt = %s' %(c_nvars,dt))

            # call main function to get things done...
            uend, stats = mp.run_pfasst(MS, u0=uinit, t0=t0, dt=dt, Tend=Tend)

            err_classical_rel = abs(uex-uend)/abs(uex)
            err_fenics = df.errornorm(uex.values,uend.values)

            print('(classical/fenics) error at time %s: %s / %s' % (Tend,err_classical_rel,err_fenics))

            extract_stats = grep_stats(stats, level=-1, type='niter')
            sortedlist_stats = sort_stats(extract_stats, sortby='step')
            niter = sortedlist_stats[0][1]
            print('niter = %s' %niter)

            id = ID(c_nvars=c_nvars, dt=dt)
            results[id] = (niter,err_classical_rel,err_fenics)
            file = open('fenics_heat_unforced_mlsdc_CG4_mm.pkl', 'wb')
            pickle.dump(results, file)

    print(results)
    # file = open('fenics_heat_unforced_sdc.pkl', 'wb')
    # pickle.dump(results, file)








