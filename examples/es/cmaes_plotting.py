#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import numpy

from deap import algorithms
from deap import base
from deap import benchmarks
from deap import cma
from deap import creator
from deap import tools

import matplotlib.pyplot as plt

# Problem size
N = 10
NGEN = 125

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("evaluate", benchmarks.rastrigin)

def main(verbose=True):
    # The cma module uses the numpy random number generator
    numpy.random.seed(64)

    # The CMA-ES algorithm takes a population of one individual as argument
    # The centroid is set to a vector of 5.0 see http://www.lri.fr/~hansen/cmaes_inmatlab.html
    # for more details about the rastrigin and other tests for CMA-ES    
    strategy = cma.Strategy(centroid=[5.0]*N, sigma=5.0, lambda_=20*N)
    toolbox.register("generate", strategy.generate, creator.Individual)
    toolbox.register("update", strategy.update)

    halloffame = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", tools.mean)
    stats.register("std", tools.std)
    stats.register("min", min)
    stats.register("max", max)
   
    if verbose:
        column_names = ["gen", "evals"]
        if stats is not None:
            column_names += stats.functions.keys()
        logger = tools.EvolutionLogger(column_names)
        logger.logHeader()
    
    # Objects that will compile the data
    sigma = list()
    axis_ratio = list()
    diagD = list()
    fbest = list()
    best = list()
    std = list()

    for gen in xrange(NGEN):
        # Generate a new population
        population = toolbox.generate()
        # Evaluate the individuals
        fitnesses = toolbox.map(toolbox.evaluate, population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        
        # Update the strategy with the evaluated individuals
        toolbox.update(population)
        
        # Update the hall of fame and the statistics with the
        # currently evaluated population
        halloffame.update(population)
        stats.update(population)
        
        if verbose:
            logger.logGeneration(evals=len(population), gen=gen, stats=stats)
        
        # Save more data along the evolution for latter plotting
        sigma.append(strategy.sigma)
        axis_ratio.append(max(strategy.diagD)/min(strategy.diagD))
        diagD.append(sorted(list(strategy.diagD)))
        fbest.append(halloffame[0].fitness.values)
        best.append(halloffame[0])
        std.append(numpy.std(population, axis=0))

    # The x-axis will be the number of evaluations
    x = range(0, strategy.lambda_ * NGEN, strategy.lambda_)

    plt.figure()
    plt.subplot(2, 2, 1)
    plt.semilogy(x, stats.avg[0], "--b")
    plt.semilogy(x, stats.max[0], "--b")
    plt.semilogy(x, stats.min[0], "-b")
    plt.semilogy(x, fbest, "-c")
    plt.semilogy(x, sigma, "-g")
    plt.semilogy(x, axis_ratio, "-r")
    plt.grid(True)
    plt.title("blue: f-values, green: sigma, red: axis ratio")

    plt.subplot(2, 2, 2)
    plt.plot(x, best)
    plt.grid(True)
    plt.title("Object Variables")

    plt.subplot(2, 2, 3)
    plt.semilogy(x, diagD)
    plt.grid(True)
    plt.title("Scaling (All Main Axes)")

    plt.subplot(2, 2, 4)
    plt.semilogy(x, std)
    plt.grid(True)
    plt.title("Standard Deviations in All Coordinates")
    
    plt.show()

if __name__ == "__main__":
    main()