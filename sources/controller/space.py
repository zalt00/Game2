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
        self.add(self.ground_body, self.ground_shape)
        
        self.objects = {}
        
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
        
        body.width = width
        
        shape.elasticity = 0
        self.add(body, shape)
        
        self.objects[name] = (body, shape)
        
    def add_structure(self, pos, polys, segments, name):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        
        shapes = []
        for points in polys:
            s = pymunk.Poly(body, points, radius=1)
            shapes.append(s)
            s.friction = 0
            s.is_structure = True
        for a, b in segments:
            s = pymunk.Segment(body, a, b, 1)
            shapes.append(s)
            s.friction = 1
            s.is_solid_ground = True
            
        self.add(body, shapes)
        
        self.objects[name] = (body, shapes)
    
