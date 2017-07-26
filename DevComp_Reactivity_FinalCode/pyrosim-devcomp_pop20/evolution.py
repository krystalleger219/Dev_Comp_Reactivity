import pickle
import random
import numpy as np
from replicators import Population


POP_SIZE = 20 #30
GENS = 2000 #1000
NUM_ENV = 2
EVAL_TIME = 700#1000
FIT_STAT = np.sum

r = open('data/Dev_Compress_1_Run_0.p', 'r')
final_pop = pickle.load(r)
#
sorted_inds = sorted(final_pop.individuals_dict, key=lambda k: final_pop.individuals_dict[k].fitness)
final_pop.individuals_dict[sorted_inds[-1]].start_evaluation(blind=False, eval_time=EVAL_TIME, pause=True)
#
r.close()

exit()

for run in range(0,20):

    random.seed(run)
    np.random.seed(run)

    for compress in [False, True]:

        pop = Population(POP_SIZE, num_env=NUM_ENV, development_type=1, fitness_stat=FIT_STAT,
                         compress_multiple_brains=compress)

        for gen in range(GENS):
            pop.create_children_through_mutation()
            pop.add_random_inds(1)
            pop.increment_ages()
            pop.evaluate()
            pop.reduce()
            pop.print_non_dominated()
            pop.gen += 1

        f = open('data/Dev_Compress_{0}_Run_{1}.p'.format(int(compress), run), 'w')
        pickle.dump(pop, f)
        f.close()


for n in range(0,20):
        for i in range(0,2):
            r = open('data/Dev_Compress_'+str(i)+'_Run_'+str(n)+'.p', 'r')
            final_pop = pickle.load(r)

            sorted_inds = sorted(final_pop.individuals_dict, key=lambda k: final_pop.individuals_dict[k].fitness)
            final_pop.individuals_dict[sorted_inds[-1]].start_evaluation(blind=True, eval_time=EVAL_TIME, pause=False)
            if i == 0:
                f = open('data/Control.csv', 'a')
                f.write(str(final_pop.individuals_dict[sorted_inds[-1]].fitness)+',')
                f.write(str(final_pop.individuals_dict[sorted_inds[-1]].dev_compression))
                f.write('\n')
                f.close()
            elif i == 1:
                f = open('data/ExpCompress.csv', 'a')
                f.write(str(final_pop.individuals_dict[sorted_inds[-1]].fitness)+',')
                f.write(str(final_pop.individuals_dict[sorted_inds[-1]].dev_compression))
                f.write('\n')
                f.close()
           
    #
            r.close()
exit()
r = open('data/Dev_1_Run_1.p', 'r')
final_pop = pickle.load(r)
#
sorted_inds = sorted(final_pop.individuals_dict, key=lambda k: final_pop.individuals_dict[k].fitness)
final_pop.individuals_dict[sorted_inds[-1]].start_evaluation(blind=False, eval_time=EVAL_TIME, pause=True)
#
r.close()




