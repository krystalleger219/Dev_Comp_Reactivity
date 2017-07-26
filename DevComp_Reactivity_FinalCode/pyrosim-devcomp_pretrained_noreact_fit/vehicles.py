import numpy as np


class Vehicle:
    def __init__(self, sim, synaptic_weights, speed, eval_time, body_length, num_legs, development_type,
                 rgb=(0, 1, 0.75)):
        self.sim = sim
        self.development_type = development_type
        self.synaptic_weights = synaptic_weights
        self.speed = speed
        self.eval_time = eval_time
        self.leg_length = body_length
        self.leg_radius = body_length / 5.
        self.body_length = body_length
        self.body_height = 2 * self.leg_radius
        self.num_legs = num_legs
        self.rgb = rgb
        self.send_body_plan(sim)
        self.send_brain(sim)

    def send_body_plan(self, sim):

        pelvis_id = 0
        sim.Send_Box(objectID=pelvis_id, x=0, y=0, z=self.body_length + self.leg_radius,
                     length=self.body_length, width=self.body_length, height=self.body_height,
                     r=self.rgb[0], g=self.rgb[1], b=self.rgb[2])

        femur_id = 1
        tibia_id = 2
        hip_id = 0
        knee_id = 1
        theta = 0.
        for leg_idx in range(self.num_legs):
            sim.Send_Cylinder(objectID=femur_id,
                              x=np.cos(theta) * (self.body_length + self.leg_length) / 2.,
                              y=np.sin(theta) * (self.body_length + self.leg_length) / 2.,
                              z=self.leg_length + self.leg_radius, r1=np.cos(theta), r2=np.sin(theta), r3=0,
                              length=self.leg_length, radius=self.leg_radius,
                              r=self.rgb[0], g=self.rgb[1], b=self.rgb[2])

            sim.Send_Cylinder(objectID=tibia_id,
                              x=np.cos(theta) * (self.body_length / 2.0 + self.leg_length),
                              y=np.sin(theta) * (self.body_length / 2.0 + self.leg_length),
                              z=self.leg_length / 2.0 + self.leg_radius, r1=0, r2=0, r3=1,
                              length=self.leg_length, radius=self.leg_radius,
                              r=self.rgb[0], g=self.rgb[1], b=self.rgb[2])

            sim.Send_Joint(jointID=hip_id, firstObjectID=pelvis_id, secondObjectID=femur_id,
                           x=np.cos(theta) * self.body_length / 2.,
                           y=np.sin(theta) * self.body_length / 2.,
                           z=self.leg_length + self.leg_radius, n1=-np.sin(theta), n2=np.cos(theta), n3=0,
                           lo=-np.pi/4., hi=np.pi/4.
                           )

            sim.Send_Joint(jointID=knee_id, firstObjectID=femur_id, secondObjectID=tibia_id,
                           x=np.cos(theta) * (self.body_length / 2.0 + self.leg_length),
                           y=np.sin(theta) * (self.body_length / 2.0 + self.leg_length),
                           z=self.leg_length + self.leg_radius, n1=-np.sin(theta), n2=np.cos(theta), n3=0,
                           lo=-np.pi/4., hi=np.pi/4.
                           )

            sim.Send_Touch_Sensor(sensorID=leg_idx, objectID=tibia_id)

            theta += np.pi / (self.num_legs / 2.0)
            femur_id += 2
            tibia_id += 2
            hip_id += 2
            knee_id += 2

        # end for

        sim.Send_Light_Sensor(sensorID=self.num_legs, objectID=pelvis_id)

    def send_brain(self, sim):

        for sensor_idx in range(self.num_legs + 1):
            sim.Send_Sensor_Neuron(neuronID=sensor_idx, sensorID=sensor_idx)

        for motor_idx in range(2 * self.num_legs):
            sim.Send_Motor_Neuron(neuronID=(self.num_legs + 1) + motor_idx, jointID=motor_idx, tau=self.speed)

        for sensor_idx in range(self.num_legs + 1):
            for motor_idx in range(2 * self.num_legs):

                if self.development_type == 1:
                    transition_time = self.synaptic_weights["transition_times"][sensor_idx, motor_idx]
                    sim.Send_Changing_Synapse(sourceNeuronID=sensor_idx, targetNeuronID=(self.num_legs + 1) + motor_idx,
                                              start_weight=self.synaptic_weights["weights"][0][sensor_idx, motor_idx],
                                              end_weight=self.synaptic_weights["weights"][1][sensor_idx, motor_idx],
                                              start_time=int(transition_time), end_time=int(transition_time))

                elif self.development_type == 2:
                    sim.Send_Changing_Synapse(sourceNeuronID=sensor_idx, targetNeuronID=(self.num_legs + 1) + motor_idx,
                                              start_weight=self.synaptic_weights["weights"][0][sensor_idx, motor_idx],
                                              end_weight=self.synaptic_weights["weights"][1][sensor_idx, motor_idx],
                                              end_time=self.eval_time)

                else:  # no development
                    sim.Send_Synapse(sourceNeuronID=sensor_idx, targetNeuronID=(self.num_legs + 1) + motor_idx,
                                     weight=self.synaptic_weights["weights"][0][sensor_idx, motor_idx])

