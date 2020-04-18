# -*- coding:Utf-8 -*-


class PhysicsUpdater:
    def __init__(self, body, landing_callback, save_position_callback):
        self.body = body
        self.on_ground = False
        self.collide = False
        self.land = landing_callback
        self.save_position = save_position_callback
        self.a = 11
        self.x1 = 0
        self.x2 = 0
       
    def is_on_ground(self, arbiter):
        shapes = arbiter.shapes
        for shape in shapes:
            if getattr(shape, 'is_solid_ground', False):
                self.on_ground = True
                points = arbiter.contact_point_set.points
                if len(points) == 2:
                    self.x1, self.x2 = points[0].point_a.x, points[1].point_a.x
                self.collide = True
            elif getattr(shape, 'is_structure', False):
                self.collide = True
    
    def update(self, entity, n=1):
        for _ in range(n):
            self.on_ground = False
            self.collide = False
            self.body.each_arbiter(self.is_on_ground)
                    
            if self.collide and entity.state == 'dash':
                self.body.velocity /= 20
                entity.state = 'fall'
            
            if self.on_ground:
                if self.x1 < self.body.position.x - 10 and self.x2 < self.body.position.x - 10:
                    if abs(self.body.velocity.x) < 70:
                        entity.thrust.x += 110000
                elif self.x1 > self.body.position.x + 10 and self.x2 > self.body.position.x + 10:
                    if abs(self.body.velocity.x) < 70:
                        entity.thrust.x += -110000
                elif self.body.width // 2 < round(abs(self.x1 - self.x2)):
                    self.save_position()
                        
            else:
                if self.body.velocity.y < 0:
                    if entity.state == 'jump':
                        entity.state = 'fall'
                else:
                    if entity.state == 'fall':
                        entity.state = 'jump'
            self.body.angle = 0
            self.body.angular_velocity = 0
            self.body.space.reindex_shapes_for_body(self.body)
            
            if not entity.is_on_ground and entity.state in ('walk', 'run'):
                entity.state = 'fall'
            
            if not self.on_ground:
                if self.a > 2:
                    on_ground = False
                else:
                    self.a += 1
                    on_ground = True
            else:
                self.a = 0
                on_ground = True
            
            landed = (not entity.is_on_ground) and on_ground
            entity.is_on_ground = on_ground
            if landed:
                self.land()

