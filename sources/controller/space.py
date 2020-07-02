# -*- coding:Utf-8-*-

import pymunk


class GameSpace(pymunk.Space):
    def __init__(self, ground_height, ground_length):
        super().__init__()
        self.gravity = (0, -1000)
        self.ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.ground_shape = pymunk.Segment(self.ground_body, (0, ground_height), (ground_length, ground_height), 5)
        self.ground_shape.friction = 1
        self.ground_shape.is_solid_ground = True
        self.ground_shape.collision_type = 1
        self.add(self.ground_body, self.ground_shape)
        
        self.objects = {}

    def add_humanoid_entity(self, height, width, pos, name):
        points = ((-round(width/4), 0),
                  (round(width/4), 0),
                  (width/2, height / 5),
                  (width/2, height),
                  (-width/2, height),
                  (-width/2, height / 5))
        radius = 1
        mass = 10
        moment = pymunk.moment_for_poly(mass, points, radius=radius)
        body = pymunk.Body(mass, moment, pymunk.Body.DYNAMIC)
        body.center_of_gravity = (0, height / 4)
        body.position = pos
        shape = pymunk.Poly(body=body, vertices=points, radius=radius)
        shape.collision_type = 0
        shape.friction = 1
        
        body.width = width
        
        shape.elasticity = 0
        self.add(body, shape)
        
        self.objects[name] = (body, shape)
        
    def add_structure(self, pos, walls, segments, name):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        
        shapes = []
        for a, b in walls:
            s = pymunk.Segment(body, a, b, 1)
            shapes.append(s)
            s.friction = 0
            s.is_solid_ground = False
            s.collision_type = 2

        for a, b in segments:
            s = pymunk.Segment(body, a, b, 1)
            shapes.append(s)
            s.friction = 1
            s.is_solid_ground = True
            s.collision_type = 1
            
        self.add(body, shapes)
        
        self.objects[name] = (body, shapes)

