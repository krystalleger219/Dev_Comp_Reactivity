import numpy as np
from copy import deepcopy
from pyrosim import PYROSIM
from vehicles import Vehicle
from environments import Environment
from sklearn import metrics

class Individual(object):
    def __init__(self, idx, num_env, speed, eval_time, body_length, num_legs, development_type, fitness_stat,
                 compress_multiple_brains):
        self.num_env = num_env
        self.sim = [None for _ in range(num_env)]
        self.speed = speed
        self.eval_time = eval_time
        self.body_length = body_length
        self.num_legs = num_legs
        self.development_type = development_type
        self.weight_genes = np.array([np.random.random((2, num_legs+1, 2*num_legs)) * 2 - 1 for _ in range(num_env)])
        self.time_genes = np.array([np.random.randint(1, eval_time, (num_legs+1, 2*num_legs)) for _ in range(num_env)])
        self.genome = {env: {"weights": self.weight_genes[env], "transition_times": self.time_genes[env]}
                       for env in range(num_env)}
        self.id = idx
        self.env_scores = []
        self.fitness_stat = fitness_stat
        self.fitness = 0
        self.age = 0
        self.compress_multiple_brains = compress_multiple_brains
        self.dev_compression = self.calc_dev_compression()
        self.dominated_by = []
        self.pareto_level = 0
        self.already_evaluated = False
        self.reactivity_evaluated = False
        self.reactivity = 0

    def __deepcopy__(self, memo):
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(deepcopy(self.__dict__, memo))
        return new
    
 
        
    
    
    def calc_reactivity(self):
        sensor_changes = np.zeros((2,999))
        output_changes = np.zeros((2,999))
        all_outputs = np.zeros((2,999,8))
        self.reactivity = 0
        for e in range(self.num_env):        
            self.sim[e].Wait_To_Finish()
            Sensor_Data = {
                    'Touch_Sensor0': np.array(self.sim[e].Get_Sensor_Data(sensorID=0)),
                    'Touch_Sensor1': np.array(self.sim[e].Get_Sensor_Data(sensorID=1)),
                    'Touch_Sensor2': np.array(self.sim[e].Get_Sensor_Data(sensorID=2)),
                    'Touch_Sensor3': np.array(self.sim[e].Get_Sensor_Data(sensorID=3)),
                    'zLight_Sensor': np.array(self.sim[e].Get_Sensor_Data(sensorID = 4))
                    # 'z' so it appears lasted in sorted()
                    }
            Motor_Data = {
                'Joint_0': [0],
                'Joint_1': [0],
                'Joint_2': [0],
                'Joint_3': [0],
                'Joint_4': [0],
                'Joint_5': [0],
                'Joint_6': [0],
                'Joint_7': [0]
                }


            for motor in range(8):
                    for time in range(1000):
                        # Flush summed input per time step
                        summed_input = 0
                        for sensor in range(5):
                            current_sensor = Sensor_Data[sorted(Sensor_Data.keys())[sensor]]
                            summed_input += self.weight_genes[e][0][sensor][motor]*current_sensor[time]


                        current_motor = Motor_Data[sorted(Motor_Data.keys())[motor]]
                        # Following formula, motor output depends on previous value:
                        if time == 0:
                            current_motor.append(np.tanh(summed_input))
                        else:
                            current_motor.append(np.tanh(current_motor[time-1] + summed_input))
                    # Turn data into an array
                    Motor_Data[sorted(Motor_Data.keys())[motor]] = np.array(Motor_Data[sorted(Motor_Data.keys())[motor]])
                
            motor_data = Motor_Data
            
            for time_step in range(1,self.eval_time):
                
                
                data = self.sim[e].Get_Sensor_Data(sensorID= self.num_legs)
                current_value_s = data[time_step]
                prev_value_s = data[time_step - 1]
                sensor_changes[e][time_step - 1] =  np.abs(prev_value_s - current_value_s)
                
                
                for joint in range(0,8):
                    
                    prev_value_o = motor_data[sorted(motor_data.keys())[joint]][time_step-1]
                    current_value_o = motor_data[sorted(motor_data.keys())[joint]][time_step]
                    all_outputs[e][time_step - 1][joint] = np.abs(prev_value_o - current_value_o)
                    output_changes[e][time_step - 1] = np.mean(all_outputs[e][time_step - 1])

        mut_info = metrics.mutual_info_score(output_changes[0], sensor_changes[0]) + metrics.mutual_info_score(output_changes[1], sensor_changes[1])
        self.reactivity = float(mut_info)
        self.reactivity_evaluated = True
        self.sim = [None for _ in range(self.num_env)]

    def calc_dev_compression(self):

        trace = {}
        for env in range(self.num_env):
            start_weights, final_weights = self.genome[env]["weights"][0], self.genome[env]["weights"][1]
            transition_times = self.genome[env]["transition_times"]

            trace[env] = [time_step*start_weights for time_step in range(self.eval_time)]
            for time_step in range(self.eval_time):
                final_idx = np.where(transition_times <= time_step)
                trace[env][time_step][final_idx] = time_step*final_weights[final_idx]

        return np.sum(np.abs(np.array(trace[0])-np.array(trace[1])))

    def start_evaluation(self, eval_time, blind, pause):
        for e in range(self.num_env):
            self.sim[e] = PYROSIM(playPaused=pause, evalTime=eval_time, playBlind=blind)


            this_genome = self.genome[e]  # use different brain for each environment

            _robot = Vehicle(self.sim[e], this_genome, self.speed, self.eval_time, self.body_length, self.num_legs,
                             self.development_type)
            _env = Environment(e, self.sim[e], self.body_length, 1+2*self.num_legs)

            self.sim[e].Start()

    def compute_fitness(self):
        self.env_scores = []
        self.fitness = 0

        for e in range(self.num_env):
            self.sim[e].Wait_To_Finish()
            dist = self.sim[e].Get_Sensor_Data(sensorID=self.num_legs)
            self.env_scores += [dist[-1]]

        self.fitness = self.fitness_stat(self.env_scores)
        self.already_evaluated = True
        self.sim = [None for _ in range(self.num_env)]

    def mutate(self, new_id, prob=None):
        if prob is None:
            prob = 1 / float((self.num_legs+1)*2*self.num_legs*self.num_env)  # one per brain
            if not self.compress_multiple_brains:
                prob *= self.num_env

        weight_change = np.random.normal(scale=np.abs(self.weight_genes))
        new_weight_genes = np.clip(self.weight_genes + weight_change, -1, 1)
        mask = np.random.random(self.weight_genes.shape) < prob
        self.weight_genes[mask] = new_weight_genes[mask]

        time_change = np.random.randint(1, self.eval_time, (self.num_legs+1, 2*self.num_legs))
        new_time_genes = self.time_genes + time_change
        mask = np.random.random(self.time_genes.shape) < prob
        self.time_genes[mask] = new_time_genes[mask]

        # self.genome = np.concatenate([self.weight_genes, self.time_genes])
        self.genome = {env: {"weights": self.weight_genes[env], "transition_times": self.time_genes[env]}
                       for env in range(self.num_env)}
        self.id = new_id
        self.already_evaluated = False

    def dominates(self, other):

        if not self.compress_multiple_brains:  # use fitness and reactivity and age (3 objectives total)
            if self.fitness > other.fitness and self.reactivity >= other.reactivity and self.age <= other.age:
                return True

            elif self.fitness == other.fitness and self.reactivity > other.reactivity and self.age <= other.age:
                return True

            elif self.fitness == other.fitness and self.reactivity == other.reactivity and self.age < other.age:
                return True

            elif self.fitness == other.fitness and self.reactivity == other.reactivity and self.age == other.age and self.id < other.id:
                return True

            else:
                return False

        else:  # use combined env scores, developmental compression and age (3 objectives total)
            if self.fitness > other.fitness and self.age <= other.age and self.dev_compression <= other.dev_compression:
                return True

            elif self.fitness == other.fitness and self.age < other.age and self.dev_compression <= other.dev_compression:
                return True

            elif self.fitness == other.fitness and self.age == other.age and self.dev_compression < other.dev_compression:
                return True

            elif self.fitness == other.fitness and self.age == other.age and self.dev_compression == other.dev_compression and self.id < other.id:
                return True

            else:
                return False


class Population(object):
    def __init__(self, size, num_env=2, eval_time=1000, speed=0.1, body_length=0.1, num_legs=4, development_type=0,
                 fitness_stat=np.sum, compress_multiple_brains=False):
        self.size = size
        self.gen = 0
        self.individuals_dict = {}
        self.max_id = 0
        self.num_env = num_env
        self.eval_time = eval_time
        self.speed = speed
        self.body_length = body_length
        self.num_legs = num_legs
        self.development_type = development_type
        self.compress_multiple_brains = compress_multiple_brains
        self.fitness_stat = fitness_stat
        self.non_dominated_size = 0
        self.pareto_levels = {}
        self.add_random_inds(size)
        self.evaluate()

    def print_non_dominated(self):
        print self.gen, self.pareto_levels[0]

    def evaluate(self, blind=True, pause=False):
        for key, ind in self.individuals_dict.items():
            if not ind.already_evaluated:
                ind.start_evaluation(self.eval_time, blind, pause)

        for key, ind in self.individuals_dict.items():
            if not ind.already_evaluated:
                ind.compute_fitness()
        
    def eval_reactivity(self, blind = True, pause = False):
        for key, ind in self.individuals_dict.items():
            if not ind.reactivity_evaluated:
                ind.start_evaluation(self.eval_time, blind, pause)

        for key, ind in self.individuals_dict.items():
            if not ind.reactivity_evaluated:
                ind.calc_reactivity()

    def create_children_through_mutation(self, fill_pop_from_non_dom=True):
        if fill_pop_from_non_dom:
            while len(self.individuals_dict) < self.size:
                for key, ind in self.individuals_dict.items():
                    child = deepcopy(ind)
                    child.mutate(self.max_id)
                    child.already_evaluated = False
                    self.individuals_dict[self.max_id] = child
                    self.max_id += 1

        else:
            for key, ind in self.individuals_dict.items():
                child = deepcopy(ind)
                child.mutate(self.max_id)
                child.already_evaluated = False
                self.individuals_dict[self.max_id] = child
                self.max_id += 1

    def increment_ages(self):
        for key, ind in self.individuals_dict.items():
            ind.age += 1

    def add_random_inds(self, num_random=1):
        for _ in range(num_random):
            self.individuals_dict[self.max_id] = Individual(self.max_id, self.num_env, self.speed, self.eval_time,
                                                            self.body_length, self.num_legs, self.development_type,
                                                            self.fitness_stat, self.compress_multiple_brains)
            self.max_id += 1

    def update_dominance(self):
        for key, ind in self.individuals_dict.items():
            ind.dominated_by = []

        for key1, ind1 in self.individuals_dict.items():
            for key2, ind2 in self.individuals_dict.items():
                if key1 != key2:
                    if self.individuals_dict[key1].dominates(self.individuals_dict[key2]):
                        self.individuals_dict[key2].dominated_by += [key1]

        self.non_dominated_size = 0
        self.pareto_levels = {}
        for key, ind in self.individuals_dict.items():
            ind.pareto_level = len(ind.dominated_by)
            if ind.pareto_level in self.pareto_levels:
                self.pareto_levels[ind.pareto_level] += [(ind.id, ind.fitness, ind.age, ind.dev_compression, ind.reactivity)]
            else:
                self.pareto_levels[ind.pareto_level] = [(ind.id, ind.fitness, ind.age, ind.dev_compression, ind.reactivity)]
            if ind.pareto_level == 0:
                self.non_dominated_size += 1

    def reduce(self, keep_non_dom_only=True, pairwise=False):
        self.update_dominance()

        if keep_non_dom_only:  # completely reduce to non-dominated front (most pressure, least diversity)

            children = {}
            for idx, fit, age, compression, reactivity in self.pareto_levels[0]:
                children[idx] = self.individuals_dict[idx]
            self.individuals_dict = children

        elif pairwise:  # reduce by calculating pairwise dominance (least pressure, most diversity)

            while len(self.individuals_dict) > self.size and len(self.individuals_dict) > self.non_dominated_size:
                current_ids = [idx for idx in self.individuals_dict]
                np.random.shuffle(current_ids)
                inds_to_remove = []
                for idx in range(1, len(self.individuals_dict)):
                    this_id = current_ids[idx]
                    previous_id = current_ids[idx-1]
                    if self.individuals_dict[previous_id].dominates(self.individuals_dict[this_id]):
                        inds_to_remove += [this_id]
                for key in inds_to_remove:
                    del self.individuals_dict[key]

        else:  # add by pareto level until full

            children = {}
            for level in sorted(self.pareto_levels):
                sorted_level = sorted(self.pareto_levels[level], key=lambda x: x[1], reverse=True)
                for idx, fit, age, compression, reactivity in sorted_level:
                    if len(children) < self.size:
                        children[idx] = self.individuals_dict[idx]
            self.individuals_dict = children

