# -*- coding:Utf-8-*-

import pymunk


class GameSpace(pymunk.Space):
    def __init__(self, ground_height, ground_length):
        super().__init__()
        self.gravity = (0, -900)
        self.ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.ground_shape = pymunk.Segment(self.ground_body, (0, ground_height), (ground_length, ground_height), 5)
        self.ground_shape.friction = 1
        self.ground_shape.is_solid_ground = True
        self.add(self.ground_body, self.ground_shape)
        
        self.entities = {}
        
    def add_humanoid_entity(self, height, width, pos, name):
        points = ((-width/2, 0), (width/2, 0), (width/2, height), (-width/2, height))
        radius = 1
        mass = 10
        moment = pymunk.moment_for_poly(mass, points, radius=radius)
        body = pymunk.Body(mass, moment, pymunk.Body.DYNAMIC)
        body.position = pos
        body.center_of_gravity = (0, 0)
        shape = pymunk.Poly(body=body, vertices=points, radius=radius)
        shape.friction = 1

        shape.elasticity = 0
        self.add(body, shape)
        
        self.entities[name] = (body, shape)
