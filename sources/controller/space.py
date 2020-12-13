# -*- coding:Utf-8-*-

import pymunk


class GameSpace(pymunk.Space):
    def __init__(self):
        super().__init__()
        self.gravity = (0, -1000)
        
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
        shape.action_on_touch = None
        
        body.width = width
        
        shape.elasticity = 0
        self.add(body, shape)
        
        self.objects[name] = (body, shape)
        
    def add_structure(self, pos, walls, segments, name, action_on_touch=None):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        
        shapes = []
        for a, b in walls:
            s = pymunk.Segment(body, a, b, 1)
            shapes.append(s)
            s.friction = 0
            s.collision_type = 2
            s.action_on_touch = action_on_touch

        for a, b in segments:
            s = pymunk.Segment(body, a, b, 1)
            shapes.append(s)
            s.friction = 1
            s.collision_type = 1
            s.action_on_touch = action_on_touch
            
        self.add(body, *shapes)
        
        self.objects[name] = (body, shapes)

