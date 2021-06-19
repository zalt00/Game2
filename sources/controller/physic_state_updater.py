# -*- coding:Utf-8 -*-

from time import perf_counter
import time
import pymunk
from utils.logger import logger


class BasePhysicStateUpdater:
    def __init__(self, states_durations):
        self.states_durations = states_durations

        self.current_state_name = 'idle'
        self.current_state_duration = 0
        self.t0 = 0
        self.current_time = 0

    def change_physic_state(self, entity, state):
        if entity.state != 'die' or not entity.dead:
            duration = self.states_durations.get(state, None)
            if duration is None:
                duration = entity.image_handler.get_state_duration(state)
            self.current_state_duration = duration
            self.current_state_name = state
            self.t0 = self.current_time
        if entity.dead and entity.state != 'die':
            entity.state = 'die'

    def update_physic_state(self, entity):
        if self.current_time - self.t0 >= self.current_state_duration:
            entity.end_of_state(self.current_state_name)

    def step(self, dt):
        self.current_time += dt

    def update_(self, entity):
        pass


class PlayerPhysicStateUpdater(BasePhysicStateUpdater):
    def __init__(self, body, landing_callback, save_position_callback, space, states_durations):
        super(PlayerPhysicStateUpdater, self).__init__(states_durations)
        
        self.body = body
        self.space = space

        self.on_ground = True
        self.collision_counter = 0
        self.ground_collision_counter = 0
        self.collide_but_ignored = set()
        self.collide_for_one_tick = False
        self.dashing_for_one_tick = False
        self.collide_with_slippery_slope = False

        self.land = landing_callback
        self.save_position = save_position_callback
        self.a = 11

        self.time_spent_on_ground_with_wrong_state = 0

        self.extended_collision = None  # hitbox extension for player during a dash to prevent clipping through walls

        self.x1 = 0
        self.x2 = 0
        self.xb = 0

        self.landing_strength = 0

        # override default collision behaviours
        player_ground_collision_handler = self.space.add_collision_handler(0, 1)
        player_wall_collision_handler = self.space.add_collision_handler(0, 2)
        player_slippery_slope_collision_handler = self.space.add_collision_handler(0, 3)

        player_ground_collision_handler.pre_solve = self.collision_with_ground
        player_ground_collision_handler.post_solve = self.collision_with_ground_post_solve
        player_wall_collision_handler.post_solve = self.collision_with_structure_wall
        player_slippery_slope_collision_handler.post_solve = self.collision_with_slippery_slope

        player_ground_collision_handler.separate = self.separate_from_ground
        player_wall_collision_handler.separate = self.separate_from_wall
        player_slippery_slope_collision_handler.separate = self.separate_from_slippery_slope

        player_ground_collision_handler.begin = self.begin_collision_with_ground
        player_wall_collision_handler.begin = self.begin_collision_with_wall
        player_slippery_slope_collision_handler.begin = self.check_actions_on_touch

        self.stable_ground = False
        self.collide_with_dynamic_ground = None

        self.previous_collision_data = None

        self.actions = {}
        self._identifier = 0

    def get_identifier(self):
        self._identifier += 1
        return self._identifier

    def begin_collision_with_ground(self, arbiter, *_, **__):
        self.ground_collision_counter += 1

        shapes = arbiter.shapes
        for shape in shapes:
            if shape.collision_type == 1:
                shape.collision_type_at_the_beginning_of_the_collision = 1

        return self.check_actions_on_touch(arbiter, shapes=shapes)

    def begin_collision_with_wall(self, arbiter, *_, **__):

        shapes = arbiter.shapes
        for shape in shapes:
            if shape.collision_type == 2:
                shape.collision_type_at_the_beginning_of_the_collision = 2

        return self.check_actions_on_touch(arbiter, shapes=shapes)

    def check_actions_on_touch(self, arbiter, *_, **kwargs):
        if 'shapes' in kwargs:
            shapes = kwargs['shapes']
        else:
            shapes = arbiter.shapes

        self.collision_counter += 1
        for s in shapes:
            if s.action_on_touch is not None:
                self.schedule_action(s.action_on_touch[0], s.action_on_touch[1], 1)
        return True

    def separate_from_ground(self, arbiter, *_, **kwargs):

        if 'do_not_check_collision_type_change' in kwargs:
            check_collision_type_change = not kwargs['do_not_check_collision_type_change']
        else:
            check_collision_type_change = True

        # detects if the collision type changed since the beginning of the collision (can happen if a dynamic block
        # rotates for example) and change the collision callback if it did, so the collision counters are still
        # accurate
        if check_collision_type_change:
            shapes = arbiter.shapes
            for shape in shapes:
                if shape.collision_type == 1:
                    if getattr(shape, 'collision_type_at_the_beginning_of_the_collision', 1) == 2:
                        logger.debug('Collision type 2 does not match with the beginning of the collision,'
                                     ' changing collision callback')
                        return self.separate_from_wall(arbiter, do_not_check_collision_type_change=True)

        self.separate()

        self.landing_strength = 0
        self.collide_with_dynamic_ground = None

        self.ground_collision_counter -= 1

        if self.ground_collision_counter <= 0:
            self.on_ground = False

    def separate_from_wall(self, arbiter, *_, **kwargs):

        if 'do_not_check_collision_type_change' in kwargs:
            check_collision_type_change = not kwargs['do_not_check_collision_type_change']
        else:
            check_collision_type_change = True

        # see above
        if check_collision_type_change:
            shapes = arbiter.shapes
            for shape in shapes:
                if shape.collision_type == 2:
                    if getattr(shape, 'collision_type_at_the_beginning_of_the_collision', 2) == 1:
                        logger.debug('Collision type 1 does not match with the beginning of the collision,'
                                     ' changing collision callback')
                        return self.separate_from_ground(arbiter, do_not_check_collision_type_change=True)

        self.separate()

    def separate(self, *_, **__):
        self.collision_counter -= 1

    def separate_from_slippery_slope(self, *_, **__):
        self.collide_with_slippery_slope = False
        self.separate()

    def collision_with_structure_wall(self, arbiter, *_, **__):
        self.xb = arbiter.contact_point_set.points[0].point_a.x

        self.collision_with_structure(arbiter)

    def collision_with_ground(self, arbiter, *_, **__):

        points = arbiter.contact_point_set.points
        self.xb = points[0].point_a.x
        if len(points) == 2:
            self.x1, self.x2 = points[0].point_a.x, points[1].point_a.x

        body = arbiter.shapes[1].body
        for contact_point in points:
            py = round(self.body.position.y)
            on_dynamic_ground = self.collide_with_dynamic_ground is not None

            if (((py - 8 <= round(contact_point.point_a.y) <= py + 8)
                    and (py - 8 <= round(contact_point.point_b.y) <= py + 8)) or on_dynamic_ground):

                if (((round(contact_point.point_a.y) == py - 1)
                     or (round(contact_point.point_b.y) == py - 1))) or self.body.velocity.length > 100:

                    self.stable_ground = body.body_type == pymunk.Body.STATIC

                    if (self.body.velocity.y < 1
                            or on_dynamic_ground or self.current_state_name == 'dash' or not self.stable_ground):

                        self.on_ground = True
                        self.collide_with_slippery_slope = False

                        if not self.stable_ground:
                            self.collide_with_dynamic_ground = body
                        return True

        if body.velocity.length > 500:
            # if the player goes too fast, ignoring the collision can cause physic bugs far worse than
            # just a weird interaction
            return True

        on_ground = bool(self.collide_with_dynamic_ground is not None or self.current_state_name == 'dash')
        if on_ground:
            if not on_dynamic_ground:
                self.collide_but_ignored.add(arbiter.shapes[1])
            if len(self.collide_but_ignored) >= self.ground_collision_counter:
                self.on_ground = False
                vec = self.body.velocity.x / 10, self.body.velocity.y - 2
                self.body.velocity = vec

        return self.on_ground

    def collision_with_ground_post_solve(self, arbiter, *_, **__):
        self.landing_strength = max(self.landing_strength, arbiter.total_impulse.y)
        self.collision_with_structure(arbiter)

    def collision_with_slippery_slope(self, arbiter, *_, **__):
        self.collision_with_structure_wall(arbiter)
        self.collide_with_slippery_slope = True

    def collision_with_structure(self, arbiter, *_, **__):

        # unstuck mechanism (the player can get stuck between two structures without being able to do anything,
        # this code detects this kind of situation and unblocks the player)
        # very buggy, can be exploited to gain insane vertical velocity

        # (obsolete)

        # if self.previous_collision_data is None:
        #     self.previous_collision_data = (arbiter.contact_point_set,
        #                                     arbiter.shapes[1].body.body_type != pymunk.Body.STATIC,
        #                                     arbiter.shapes[1])
        #
        # else:
        #     if arbiter.shapes[1].body != self.previous_collision_data[2].body:
        #         if self.previous_collision_data[1] or arbiter.shapes[1].body.body_type != pymunk.Body.STATIC:
        #             if round(arbiter.contact_point_set.normal.x * 1000) == -round(
        #                     self.previous_collision_data[0].normal.x * 1000):
        #                 if round(abs(arbiter.contact_point_set.normal.x)) > 0:
        #
        #                     arbiter.shapes[0].body.apply_impulse_at_local_point((0, 2000), (0, 0))
        #                     logger.warning('unstuck mechanism applied')
        #
        #             elif 27 < (abs(arbiter.contact_point_set.points[0].point_a.x) -
        #                        abs(self.previous_collision_data[0].points[0].point_a.x)) < 33:
        #                 if ((abs(round(arbiter.contact_point_set.normal.x)) == 1 and abs(round(
        #                         self.previous_collision_data[0].normal.x * 1000)) == 819) or
        #                     (abs(round(arbiter.contact_point_set.normal.x * 1000)) == 819 and abs(round(
        #                           self.previous_collision_data[0].normal.x)) == 1)):
        #
        #                     arbiter.shapes[0].body.apply_impulse_at_local_point((0, 2000), (0, 0))
        #                     logger.warning('unstuck mechanism applied')
        #
        #     self.previous_collision_data = None

        if arbiter.shapes[1].body.body_type != pymunk.Body.STATIC:
            if arbiter.total_impulse.length > 20000 and self.current_state_name != 'dash':
                self.schedule_action('die', [], 1)

    def schedule_action(self, action_name, action_arg, timer=0):
        self.actions[self.get_identifier()] = [action_name, action_arg, timer]

    def update_(self, entity, n=1):

        self.collide_but_ignored = set()

        if not entity.dead and not entity.sleeping:
            for key in list(self.actions):
                action_name, action_args, timer = self.actions[key]
                if timer == 0:
                    entity.call_action(action_name, action_args)
                    self.actions.pop(key)
                else:
                    self.actions[key][2] -= 1

            if not entity.dead:
                for _ in range(n):

                    entity.can_air_control = True

                    if entity.state == 'dash':
                        for shape in self.body.shapes:
                            if shape.sensor:
                                if self.extended_collision is None:
                                    self.extended_collision = shape
                                shape.sensor = False
                    else:
                        if self.extended_collision is not None:
                            if not self.extended_collision.sensor:
                                self.extended_collision.sensor = True

                    # bug fix (prevents the player to keep his/her speed during the dash if he or she hits the ground)
                    if (self.on_ground or self.collide_with_dynamic_ground is not None) and entity.state == 'dash':
                        self.body.velocity /= 10
                        entity.state = 'fall'

                    if not self.collide_with_slippery_slope:
                        # bug fix (prevents the player to force his/her way through walls when dashing)
                        if self.collision_counter and entity.state == 'dash':
                            if not self.dashing_for_one_tick:
                                entity.can_dash_velocity_be_applied = True
                                self.dashing_for_one_tick = True
                            else:
                                entity.can_dash_velocity_be_applied = False
                        else:
                            entity.can_dash_velocity_be_applied = True
                    elif entity.state == 'dash':
                        if abs(self.body.velocity.x) > 800:
                            entity.state = 'fall'
                            self.body.velocity *= 800 / abs(self.body.velocity.x)

                        self.dashing_for_one_tick = True

                    if entity.state != 'dash':
                        self.collide_for_one_tick = False
                        self.dashing_for_one_tick = False

                    # rough approximation of air resistance
                    # uses this formula: C * 1/2 * p(air) * v**2 * S * <vector>u
                    # C = 1.3, p(air) = 1.2, S = 1.5m * 0.3m = 0.5m^2
                    # divides by the mass, around 50kg, by 60 to convert seconds into time units (1/60s) and then
                    # by 50 again to convert distance units into meters (50 * 60 * 50 = 150 000)

                    # (obsolete)

                    # if self.body.velocity.length > 250 and not self.on_ground and entity.state != 'dash':
                    #     ax = (0.8 * self.body.velocity.x * abs(self.body.velocity.x)) / 150_000
                    #     ay = (0.8 * self.body.velocity.y * abs(self.body.velocity.y)) / 150_000
                    #     self.body.velocity -= (ax, ay)

                    # the player should not be able to air control against a wall because the wall can get him/her stuck
                    # this code tests if the direction of the player is in the same direction as the direction of the
                    # object he/she is colliding with
                    if self.collision_counter and ((entity.direction == 1 and self.xb > self.body.position.x)
                                                   or (entity.direction == -1 and self.xb < self.body.position.x)):
                        entity.can_air_control = False

                    # prevents saving an unstable position (at least half of the body must be on a stable structure)
                    if self.on_ground and self.stable_ground:
                        if self.body.width // 2 < round(abs(self.x1 - self.x2)):
                            if entity.state not in ('die', 'hit'):
                                self.save_position()

                    # prevents a "flicker" effect when the player leaves the ground for 1 or 2 ticks (it sometimes
                    # happens when the player simply runs on a structure after a weird landing)
                    if not self.on_ground:
                        if self.a > 1:
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

                    # useful to fix weird behaviours when walking on a dynamic structure
                    entity.collide_with_dynamic_ground = self.collide_with_dynamic_ground

                    self.body.angle = 0
                    self.body.angular_velocity = 0
                    self.body.space.reindex_shapes_for_body(self.body)

                    if not entity.is_on_ground and entity.state in ('walk', 'run'):
                        entity.state = 'fall'

                    # fix of a bug that happened once and that i can't reproduce
                    if entity.is_on_ground and entity.state in ('jump', 'fall'):
                        self.time_spent_on_ground_with_wrong_state += 1
                        if self.time_spent_on_ground_with_wrong_state > 16:
                            entity.state = 'idle'
                    else:
                        self.time_spent_on_ground_with_wrong_state = 0

                    # landing util
                    landed = (not entity.is_on_ground) and on_ground
                    entity.is_on_ground = on_ground
                    if landed:
                        self.land(self.landing_strength)

        else:
            self.body.velocity = (0, 0)
            self.body.angle = 0
            self.body.space.reindex_shapes_for_body(self.body)


class InvertedEntityStateUpdater(BasePhysicStateUpdater):
    def __init__(self, get_state_callback):
        self.get_state = get_state_callback

        super(InvertedEntityStateUpdater, self).__init__({})

    def update_(self, entity):
        state_data = self.get_state()
        entity.state = state_data.state
        entity.direction = state_data.direction

