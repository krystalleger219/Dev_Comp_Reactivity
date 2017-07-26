

class Environment(object):
    def __init__(self, env_id, sim, light_box_size, light_box_obj_id, dist_to_light_box=30):
        self.light_box_obj_id = light_box_obj_id
        self.dist_to_light_box = dist_to_light_box
        self.l = light_box_size
        self.w = light_box_size
        self.h = light_box_size
        self.x = 0
        self.y = 0
        self.z = self.l/2.

        if env_id == 0:
            self.place_light_source_to_the_front(sim)

        elif env_id == 1:
            self.place_light_source_to_the_back(sim)

        elif env_id == 2:
            self.place_light_source_to_the_right(sim)

        elif env_id == 3:
            self.place_light_source_to_the_left(sim)

        else:
            raise KeyError

    def place_light_source_to_the_front(self, sim):
        self.y = self.l*self.dist_to_light_box
        sim.Send_Box(objectID=self.light_box_obj_id, x=self.x, y=self.y, z=self.z,
                     length=self.l, width=self.w, height=self.h,  r=1, g=1, b=0)
        sim.Send_Light_Source(objectIndex=self.light_box_obj_id)

    def place_light_source_to_the_back(self, sim):
        self.y = -self.l*self.dist_to_light_box
        sim.Send_Box(objectID=self.light_box_obj_id, x=self.x, y=self.y, z=self.z,
                     length=self.l, width=self.w, height=self.h, r=1, g=1, b=0)
        sim.Send_Light_Source(objectIndex=self.light_box_obj_id)

    def place_light_source_to_the_left(self, sim):
        self.x = -self.l*self.dist_to_light_box
        sim.Send_Box(objectID=self.light_box_obj_id, x=self.x, y=self.y, z=self.z,
                     length=self.l, width=self.w, height=self.h, r=1, g=1, b=0)
        sim.Send_Light_Source(objectIndex=self.light_box_obj_id)

    def place_light_source_to_the_right(self, sim):
        self.x = self.l*self.dist_to_light_box
        sim.Send_Box(objectID=self.light_box_obj_id, x=self.x, y=self.y, z=self.z,
                     length=self.l, width=self.w, height=self.h, r=1, g=1, b=0)
        sim.Send_Light_Source(objectIndex=self.light_box_obj_id)

