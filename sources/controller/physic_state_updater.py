# -*- coding:Utf-8 -*-

from time import perf_counter


class PhysicStateUpdater:
    def __init__(self, body, landing_callback, save_position_callback, space, state_duration):
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

        # override default collision behaviours
        player_ground_collision_handler = self.space.add_collision_handler(0, 1)
        player_wall_collision_handler = self.space.add_collision_handler(0, 2)

        player_ground_collision_handler.pre_solve = self.collision_with_ground
        player_wall_collision_handler.post_solve = self.collision_with_structure

        player_ground_collision_handler.separate = self.separate_from_ground
        player_wall_collision_handler.separate = self.separate

        player_ground_collision_handler.begin = self.check_actions_on_touch
        player_wall_collision_handler.begin = self.check_actions_on_touch

        self.state_duration = state_duration

        self.current_state_name = 'idle'
        self.current_state_duration = 0
        self.t0 = 0

        self.actions = []

    def change_physic_state(self, entity, state):
        if entity.state != 'die' or not entity.dead:
            duration = self.state_duration.get(state, None)
            if duration is None:
                duration = entity.image_handler.get_state_duration(state)
            self.current_state_duration = duration
            self.current_state_name = state
            self.t0 = perf_counter()
        if entity.dead and entity.state != 'die':
            entity.state = 'die'

    def check_actions_on_touch(self, arbiter, *_, **__):
        shapes = arbiter.shapes
        for s in shapes:
            if s.action_on_touch is not None:
                self.actions.append(s.action_on_touch)
        return True

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
            py = round(self.body.position.y)
            if (((py - 8 <= round(contact_point.point_a.y) <= py + 8)
                    and (py - 8 <= round(contact_point.point_b.y) <= py + 8))
                and (round(contact_point.point_a.y) == py - 1 or
                     round(contact_point.point_b.y) == py - 1)):

                if self.current_state_name != 'jump' or self.body.velocity.y < 1:
                    self.on_ground = True
                    return True
        return False

    def update_(self, entity, n=1):

        if not entity.dead:

            for _ in range(len(self.actions)):
                action_name, action_args = self.actions.pop()
                getattr(entity, action_name, lambda *_, **__: None)(*action_args)

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

                # prevents a "flicker" effect when the player leaves the ground for 1 or 2 ticks (it sometimes happens
                # when the player simply runs on a structure after a weird landing)
                if not self.on_ground:
                    if self.a > 3:
                        on_ground = False
                    else:
                        self.a += 1
                        on_ground = True
                else:
                    self.a = 0
                    on_ground = True

                # animation util
                if not on_ground:
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

                landed = (not entity.is_on_ground) and on_ground
                entity.is_on_ground = on_ground
                if landed:
                    self.land()

                # updates the physic state of the entity
                t1 = perf_counter()
                if t1 - self.t0 >= self.current_state_duration:
                    entity.end_of_state(self.current_state_name)
        else:
            # updates the physic state of the entity
            t1 = perf_counter()
            if t1 - self.t0 >= self.current_state_duration:
                entity.end_of_state(self.current_state_name)
