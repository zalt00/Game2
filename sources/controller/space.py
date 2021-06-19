# -*- coding:Utf-8-*-

import pymunk
import pymunk.constraints


class GameSpace(pymunk.Space):
    def __init__(self):
        super().__init__()
        self.gravity = (0, -1000)
        
        self.objects = {}

    def add_humanoid_entity(self, height, width, pos, name):
        points = ((-round(width/4), 0),
                  (round(width/4), 0),
                  (width/3, height / 5),
                  (width/3, height),
                  (-width/3, height),
                  (-width/3, height / 5))
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

        shape2 = pymunk.Poly(body,
                             vertices=(
                                 (-width * 2 / 3, 0),
                                 (width * 2 / 3, 0),
                                 (-width * 2 / 3, height),
                                 (width * 2 / 3, height)),
                             radius=radius * 2)

        shape2.collision_type = 42
        shape2.sensor = True
        shape2.elasticity = 0.5

        body.width = width
        
        shape.elasticity = 0
        self.add(body, shape, shape2)
        
        self.objects[name] = (body, shape, shape2)

    def add_structure(self, pos, walls, segments, name, action_on_touch=None, is_slippery_slope=False,
                      is_kinematic=False):

        if is_kinematic:
            body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        else:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos

        self._add_structure(pos, walls, segments, name, action_on_touch, is_slippery_slope, body)

    def add_dynamic_structure(self, pos, walls, segments, name, mass, center_of_gravity,
                              action_on_touch=None, is_slippery_slope=False, correct_angle=False):

        points = []
        for a, b in walls:
            points.append(a)
            points.append(b)

        moment = pymunk.moment_for_poly(mass, points, radius=1)

        body = pymunk.Body(mass, moment, pymunk.Body.DYNAMIC)

        body.center_of_gravity = center_of_gravity

        body.position = pos
        self.reindex_shapes_for_body(body)

        self._add_structure(pos, walls, segments, name, action_on_touch, is_slippery_slope, body, (0.7, 1))

    def _add_structure(self, pos, walls, segments, name, action_on_touch, is_slippery_slope, body, frictions=(0.3, 1)):
        shapes = []

        points = set()
        for a, b in walls:
            assert is_slippery_slope == 0 or is_slippery_slope == 1

            points.add(tuple(a))
            points.add(tuple(b))

            s = pymunk.Segment(body, a, b, 2.5)
            shapes.append(s)
            s.friction = frictions[0]
            s.collision_type = 2 + is_slippery_slope
            s.action_on_touch = action_on_touch

        for a, b in segments:

            points.add(tuple(a))
            points.add(tuple(b))

            s = pymunk.Segment(body, a, b, 2.5)
            shapes.append(s)
            s.friction = frictions[1]
            s.collision_type = 1
            s.action_on_touch = action_on_touch

        self.add(body, *shapes)
        
        self.objects[name] = (body, shapes)

    def add_constraint(self, object_a, object_b, anchor_a, anchor_b, name):
        body_a = self.objects[object_a][0]
        body_b = self.objects[object_b][0]
        cons = pymunk.constraints.PinJoint(body_a, body_b, anchor_a, anchor_b)

        self.add(cons)
        self.objects[name] = (cons,)

