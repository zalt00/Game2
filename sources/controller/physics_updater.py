# -*- coding:Utf-8 -*-


class PhysicsUpdater:
    def __init__(self, body, landing_callback, save_position_callback, space):
        self.body = body
        self.space = space
        self.on_ground = False
        self.collide = False
        self.land = landing_callback
        self.save_position = save_position_callback
        self.a = 11
        self.x1 = 0
        self.x2 = 0
        self.xb = 0

        self.space.add_collision_handler(0, 1).pre_solve = self.collision_with_ground
        self.space.add_collision_handler(0, 2).post_solve = self.collision_with_structure
        self.space.add_collision_handler(0, 1).separate = self.separate_from_ground
        self.space.add_collision_handler(0, 2).separate = self.separate

    def separate_from_ground(self, *_, **__):
        self.separate()
        self.on_ground = False

    def separate(self, *_, **__):
        self.collide = False

    def collision_with_structure(self, arbiter, *_, **__):
        self.collide = True
        self.xb = arbiter.contact_point_set.points[0].point_a.x

    def collision_with_ground(self, arbiter, *_, **__):
        points = arbiter.contact_point_set.points
        self.xb = points[0].point_a.x
        self.collide = True
        if len(points) == 2:
            self.x1, self.x2 = points[0].point_a.x, points[1].point_a.x

        for contact_point in points:
            if (round(contact_point.point_a.y) == round(self.body.position.y - 1)
                    or round(contact_point.point_b.y) == round(self.body.position.y - 1)):
                self.on_ground = True
                return True
        self.on_ground = False
        return False
    
    def update(self, entity, n=1):
        for _ in range(n):
            entity.can_air_control = True

            # bug fix (prevents the player to keep his/her speed during the dash if he or she hits a structure)
            if self.collide and entity.state == 'dash':
                self.body.velocity /= 20
                entity.state = 'fall'

            # the player should not be able to air control against a wall because the wall can get him/her stuck
            # this code tests if the direction of the player is in the same direction as the direction of the object
            # he/she is colliding with
            if self.collide and ((entity.direction == 1 and self.xb > self.body.position.x)
                                 or (entity.direction == -1 and self.xb < self.body.position.x)):
                entity.can_air_control = False

            # prevents saving an unstable position (at least half of the body must be on a stable structure)
            if self.on_ground:
                if self.body.width // 2 < round(abs(self.x1 - self.x2)):
                    self.save_position()

            # animation util
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

            # prevents a "flicker" effect when the player leaves the ground for 1 or 2 ticks (it sometimes happens
            # when the player simply runs on a structure after a weird landing)
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

