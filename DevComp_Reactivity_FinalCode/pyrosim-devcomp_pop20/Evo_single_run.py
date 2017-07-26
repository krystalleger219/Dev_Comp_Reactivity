import sys
import pickle
import random
import numpy as np
from replicators import Population


SEED = int(sys.argv[1])
COMPRESSION = False

POP_SIZE = 400
GENS = 1000
NUM_ENV = 4
EVAL_TIME = 1000
FIT_STAT = np.min


random.seed(SEED)
np.random.seed(SEED)


pop = Population(POP_SIZE, num_env=NUM_ENV, development_type=1, fitness_stat=FIT_STAT,
                 compress_multiple_brains=COMPRESSION)

for gen in range(GENS):
    pop.create_children_through_mutation()
    pop.add_random_inds(1)
    pop.increment_ages()
    pop.evaluate()
    pop.reduce()
    pop.print_non_dominated()
    pop.gen += 1

f = open('/users/s/k/skriegma/scratch/Dev_Compression/'
         'Dev_Compress_{0}_{1}_Run_{2}.p'.format(FIT_STAT.__name__, int(COMPRESSION), SEED), 'w')
pickle.dump(pop, f)
f.close()


# r = open('data/Dev_Compress_1_Run_1.p', 'r')
# final_pop = pickle.load(r)
#
# sorted_inds = sorted(final_pop.individuals_dict, key=lambda k: final_pop.individuals_dict[k].fitness)
# final_pop.individuals_dict[sorted_inds[-1]].start_evaluation(blind=False, eval_time=EVAL_TIME, pause=True)
#
# r.close()




