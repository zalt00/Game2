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


class PlayerPhysicStateUpdater(BasePhysicStateUpdater):
    def __init__(self, body, landing_callback, save_position_callback, space, states_durations):
        super(PlayerPhysicStateUpdater, self).__init__(states_durations)
        
        self.body = body
        self.space = space

        self.on_ground = True
        self.collide = False
        self.collide_for_one_tick = False
        self.dashing_for_one_tick = False
        self.collide_with_slippery_slope = False

        self.land = landing_callback
        self.save_position = save_position_callback
        self.a = 11

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
        player_wall_collision_handler.separate = self.separate
        player_slippery_slope_collision_handler.separate = self.separate_from_slippery_slope

        player_ground_collision_handler.begin = self.check_actions_on_touch
        player_wall_collision_handler.begin = self.check_actions_on_touch
        player_slippery_slope_collision_handler.begin = self.check_actions_on_touch

        self.stable_ground = False
        self.collide_with_dynamic_ground = None

        self.previous_collision_data = None

        self.actions = []

    def check_actions_on_touch(self, arbiter, *_, **__):
        shapes = arbiter.shapes
        for s in shapes:
            if s.action_on_touch is not None:
                self.actions.append(s.action_on_touch)
        return True

    def separate_from_ground(self, *_, **__):
        self.separate()
        self.on_ground = False
        self.landing_strength = 0
        self.collide_with_dynamic_ground = None

    def separate(self, *_, **__):
        self.collide = False

    def separate_from_slippery_slope(self, *_, **__):
        self.collide_with_slippery_slope = False
        self.separate()

    def collision_with_structure_wall(self, arbiter, *_, **__):
        self.collide = True
        self.xb = arbiter.contact_point_set.points[0].point_a.x

        self.collision_with_structure(arbiter)

    def collision_with_ground(self, arbiter, *_, **__):

        points = arbiter.contact_point_set.points
        self.xb = points[0].point_a.x
        self.collide = True
        if len(points) == 2:
            self.x1, self.x2 = points[0].point_a.x, points[1].point_a.x
        for contact_point in points:
            py = round(self.body.position.y)

            on_dynamic_ground = self.collide_with_dynamic_ground is not None

            if (((py - 8 <= round(contact_point.point_a.y) <= py + 8)
                    and (py - 8 <= round(contact_point.point_b.y) <= py + 8))
                and (round(contact_point.point_a.y) == py - 1 or
                     round(contact_point.point_b.y) == py - 1)) or on_dynamic_ground:

                if (self.current_state_name != 'jump' or self.body.velocity.y < 1
                        or on_dynamic_ground or self.current_state_name == 'dash'):

                    self.on_ground = True
                    self.collide_with_slippery_slope = False

                    body = arbiter.shapes[1].body
                    self.stable_ground = body.body_type == pymunk.Body.STATIC
                    if not self.stable_ground:
                        self.collide_with_dynamic_ground = body
                    return True
        return self.collide_with_dynamic_ground is not None or self.current_state_name == 'dash'

    def collision_with_ground_post_solve(self, arbiter, *_, **__):
        self.landing_strength = max(self.landing_strength, arbiter.total_impulse.y)
        self.collision_with_structure(arbiter)

    def collision_with_slippery_slope(self, arbiter, *_, **__):
        self.collision_with_structure_wall(arbiter)
        self.collide_with_slippery_slope = True

    def collision_with_structure(self, arbiter, *_, **__):

        # unstuck mechanism (the player can get stuck between two structures without being able to do anything,
        # this code detects this kind of situation and unsticks the player)
        if self.previous_collision_data is None:
            self.previous_collision_data = (arbiter.contact_point_set,
                                            arbiter.shapes[1].body.body_type == pymunk.Body.DYNAMIC,
                                            arbiter.shapes[1])

        else:
            if arbiter.shapes[1].body != self.previous_collision_data[2].body:
                if self.previous_collision_data[1] or arbiter.shapes[1].body.body_type == pymunk.Body.DYNAMIC:
                    if round(arbiter.contact_point_set.normal.x * 1000) == -round(
                            self.previous_collision_data[0].normal.x * 1000):
                        if round(abs(arbiter.contact_point_set.normal.x)) > 0:

                            arbiter.shapes[0].body.apply_impulse_at_local_point((0, 2000), (0, 0))
                            logger.warning('unstuck mechanism applied')

                    elif 27 < (abs(arbiter.contact_point_set.points[0].point_a.x) -
                               abs(self.previous_collision_data[0].points[0].point_a.x)) < 33:
                        if ((abs(round(arbiter.contact_point_set.normal.x)) == 1 and abs(round(
                                self.previous_collision_data[0].normal.x * 1000)) == 819) or
                            (abs(round(arbiter.contact_point_set.normal.x * 1000)) == 819 and abs(round(
                                  self.previous_collision_data[0].normal.x)) == 1)):

                            arbiter.shapes[0].body.apply_impulse_at_local_point((0, 2000), (0, 0))
                            logger.warning('unstuck mechanism applied')

            self.previous_collision_data = None

        if arbiter.shapes[1].body.body_type == pymunk.Body.DYNAMIC:
            if arbiter.total_impulse.length > 10000 and self.current_state_name != 'dash':
                self.actions.append(('die', []))

    def update_(self, entity, n=1):
        if not entity.dead and not entity.sleeping:
            for _ in range(len(self.actions)):
                action_name, action_args = self.actions.pop()
                getattr(entity, action_name, lambda *_, **__: None)(*action_args)
            if not entity.dead:
                for _ in range(n):
                    entity.can_air_control = True

                    # bug fix (prevents the player to keep his/her speed during the dash if he or she hits the ground)
                    if (self.on_ground or self.collide_with_dynamic_ground is not None) and entity.state == 'dash':
                        self.body.velocity /= 10
                        entity.state = 'fall'

                    if not self.collide_with_slippery_slope:
                        # bug fix (prevents the player to force his/her way through walls when dashing)
                        if self.collide and entity.state == 'dash':
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
                    if self.body.velocity.length > 250 and not self.on_ground and entity.state != 'dash':
                        ax = (0.8 * self.body.velocity.x * abs(self.body.velocity.x)) / 150_000
                        ay = (0.8 * self.body.velocity.y * abs(self.body.velocity.y)) / 150_000
                        self.body.velocity -= (ax, ay)

                    # the player should not be able to air control against a wall because the wall can get him/her stuck
                    # this code tests if the direction of the player is in the same direction as the direction of the
                    # object he/she is colliding with
                    if self.collide and ((entity.direction == 1 and self.xb > self.body.position.x)
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

                    # fixes weird behaviours when walking on a dynamic structure
                    entity.collide_with_dynamic_ground = self.collide_with_dynamic_ground

                    self.body.angle = 0
                    self.body.angular_velocity = 0
                    self.body.space.reindex_shapes_for_body(self.body)

                    if not entity.is_on_ground and entity.state in ('walk', 'run'):
                        entity.state = 'fall'

                    landed = (not entity.is_on_ground) and on_ground
                    can_dash = entity.is_on_ground and not on_ground
                    entity.is_on_ground = on_ground
                    if landed:
                        self.land(self.landing_strength)
                    if can_dash:
                        pass
        else:
            self.body.velocity = (0, 0)
            self.body.angle = 0
            self.body.space.reindex_shapes_for_body(self.body)

