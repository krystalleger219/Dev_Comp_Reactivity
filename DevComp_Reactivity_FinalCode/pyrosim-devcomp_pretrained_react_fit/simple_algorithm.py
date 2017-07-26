import sys
import pickle
import numpy as np
from replicators import Population


SEED = int(sys.argv[1])

POP_SIZE = 30
GENS = 1000
NUM_ENV = 4
EVAL_TIME = 1000
FIT_STAT = np.min
SPEED = 0.1


for development_type in [0, 1, 2]:

    pop = Population(POP_SIZE, num_env=NUM_ENV, development_type=development_type, fitness_stat=FIT_STAT, speed=SPEED)

    for gen in range(GENS):
        pop.create_children_through_mutation(fill_pop_from_non_dom=False)  # pop.create_children_through_mutation()
        # pop.add_random_inds(1)
        pop.increment_ages()
        pop.evaluate()
        pop.reduce(keep_non_dom_only=False)  # pop.reduce()
        # pop.print_non_dominated()
        pop.gen += 1

    f = open('data/Simple_Dev_{0}_Run_{1}.p'.format(development_type, SEED), 'w')
    pickle.dump(pop, f)
    f.close()




