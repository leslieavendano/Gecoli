"""
##################################################################

GECKO model optimization E. coli test

##################################################################
"""
from mewpy.model.gecko import GeckoModel
from mewpy.simulation.reframed import GeckoSimulation
from mewpy.simulation import SimulationMethod
from mewpy.simulation.simulation import SimulationResult
from mewpy.problems.gecko import GeckoRKOProblem, GeckoROUProblem
from mewpy.optimization.evaluation import BPCY, WYIELD, TargetFlux
from mewpy.optimization import EA, set_default_engine
import mewpy.utils.utilities as utl
from collections import OrderedDict
from time import time


ITERATIONS = 1
set_default_engine('inspyred')


def ec_gecko_ko(compound, display=False, filename=None):
    """ EC Gecko example
    """

    from reframed.io.sbml import load_cbmodel
    from reframed.solvers import set_default_solver
    set_default_solver('gurobi')

    modeldir = ("/home/lavendano/Documents/Leslie/Geckomodels/eciML1515_modified.xml")
    m = load_cbmodel(modeldir)
    model = GeckoModel(m, biomass_reaction_id='R_BIOMASS_Ec_iML1515_core_75p37M',
                       protein_reaction_id='R_BIOMASS_Ec_iML1515_core_75p37M',
                       carbohydrate_reaction_id='R_BIOMASS_Ec_iML1515_core_75p37M')
    model.set_objective({'R_BIOMASS_Ec_iML1515_core_75p37M': 1.0})
    # Leslie suggestion
    model.reactions['R_prot_pool_exchange'].ub = 0.26
    model.solver = 'glpk'

    envcond = OrderedDict()

    # the evaluation (objective) functions

    evaluator_1 = BPCY("R_BIOMASS_Ec_iML1515_core_75p37M", compound,
                       method=SimulationMethod.lMOMA)
    evaluator_2 = WYIELD("R_BIOMASS_Ec_iML1515_core_75p37M", compound, parsimonious=True)
    # The optimization problem
    # Notes:
    #  - A scale factor for the LP can be defined by setting the 'scalefactor' acordingly.
    #  - The scale factor is only used in the solver context and all results are scale free.
    problem = GeckoRKOProblem(model,
                              fevaluation=[evaluator_1, evaluator_2],
                              envcond=envcond,
                              prot_prefix='R_draw_prot_',
                              candidate_max_size=6)

    # A new instance of the EA optimizer
    ea = EA(problem, max_generations=ITERATIONS)
    # runs the optimization
    final_pop = ea.run()
    # optimization results
    if display:
        individual = max(final_pop)
        best = list(problem.decode(individual.candidate).keys())
        print('Best Solution: \n{0}'.format(str(best)))
    # save final population to file
    if filename:
        print("Simplifying and saving solutions to file")
        utl.population_to_csv(problem, final_pop, filename, simplify=False)


if __name__ == '__main__':

    # N_EXP = 1
    #
    # compounds = {'TYR': 'R_EX_tyr__L_e_REV',
    #              'PHE': 'R_EX_phe__L_e_REV',
    #              'TRY': 'R_EX_trp__L_e_REV'}
    #
    # for k, v in compounds.items():
    #     for _ in range(N_EXP):
    #         millis = int(round(time() * 1000))
    #         gecko_ko(v, display=False,
    #                  filename="gecko_{}_KO_{}.csv".format(k, millis))

    ec_gecko_ko('R_EX_tyr__L_e')