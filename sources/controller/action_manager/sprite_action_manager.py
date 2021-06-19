# -*- coding:Utf-8 -*-


from utils.logger import logger
import numpy as np


class BaseEntityActionManager:

    def __init__(self, entity):
        self.entity = entity

    def do(self, action_name, *args, **kwargs):
        if hasattr(self, 'action_' + action_name):
            getattr(self, 'action_' + action_name)(*args, **kwargs)
        else:
            logger.warning(f'no action named "{action_name}"" for action manager of type {type(self).__name__}')

    def stop(self, action_name, *args, **kwargs):
        if hasattr(self, 'stop_' + action_name):
            getattr(self, 'stop_' + action_name)(*args, **kwargs)

    def action_set_state(self, state):
        self.entity.state = state

    def action_end_of_state(self, *_, **__):
        self.entity.state = 'idle'


class PlayerActionManager(BaseEntityActionManager):
    def __init__(self, entity, on_death_callback, player_data, current_save_id, hearts):
        super(PlayerActionManager, self).__init__(entity)

        self.on_death = on_death_callback

        self.hearts = hearts

        self.current_save_id = current_save_id
        self.player_data = player_data
        self.player_lives = self.player_data.current_lives.get(self.current_save_id)

        self.on_death_trigger_id = self.player_data.on_death_trigger_id

        self.still_walking = False
        self.still_running = False

        self.next_state = 'idle'
        self.next_direction = 1

        self.already_dashed = False

        self.god = False

    @property
    def player(self):
        return self.entity

    def action_toggle_god_mod(self):
        self.god = not self.god

    def action_record(self):
        if self.player.record_position:
            logger.debug('stop recording player position, it will be saved to "record.npy"')
            self.player.stop_recording_position()
            np.save('records.npy', self.player.position_records[:self.player.last_index])
        else:
            logger.debug('start recording player position')
            self.player.start_recording_position()

    def action_land(self, landing_strength=3200):
        if landing_strength > 1800:
            if self.still_walking:
                if self.still_running:
                    self.entity.secondary_state = 'run'
                else:
                    self.entity.secondary_state = 'walk'
            self.entity.state = 'land'
            self.next_state = 'idle'
        else:
            if self.still_walking:
                if self.still_walking:
                    if self.still_running:
                        self.entity.state = 'run'
                        self.next_state = 'run'
                    else:
                        self.entity.state = 'walk'
                        self.next_state = 'walk'
            else:
                self.entity.state = 'land'
                self.next_state = 'idle'
        self.entity.is_on_ground = True
        self.already_dashed = False

    def action_jump(self):

        if not self.god:
            if self.player.state in ('walk', 'run', 'idle', 'land'):
                self.player.secondary_state = ''
                self.player.state = 'jump'
            else:
                self.next_state = 'jump'
        else:
            self.player.position_handler.body.apply_force_at_local_point(
                (0, 1_250_000), self.player.position_handler.body.center_of_gravity)

    def action_dash(self):

        if (not self.already_dashed or self.god) and not self.player.is_on_ground:
            if self.player.state == 'fall' or self.player.state == 'jump':
                self.player.state = 'dash'
                self.already_dashed = True

    def action_run(self):
        self.still_running = True
        if self.player.state == 'walk':
            self.player.state = 'run'
            self.next_state = 'run'
        elif self.next_state == 'walk':
            self.next_state = 'run'

    def stop_run(self):
        self.still_running = False
        self._stop_running()

    def _stop_running(self):
        if self.player.state == 'run':
            self.player.state = 'walk'
            self.next_state = 'walk'
        elif self.next_state == 'run' and self.still_walking:
            self.next_state = 'walk'

    def action_walk_left(self):
        self.still_walking = True

        if self.player.state == 'walk' or self.player.state == 'run':
            self.player.direction = -1
        self.next_direction = -1
        if self.player.state == 'run':
            self.next_state = 'run'
        else:
            self.next_state = 'walk'

        if self.still_running:
            self.action_run()

    def action_walk_right(self):
        self.still_walking = True

        if self.player.state == 'walk' or self.player.state == 'run':
            self.player.direction = 1
        self.next_direction = 1
        if self.player.state == 'run':
            self.next_state = 'run'
        else:
            self.next_state = 'walk'

        if self.still_running:
            self.action_run()

    def stop_walk_right(self):
        if self.player.direction == 1 or self.next_direction == 1:
            self.stop_walking()

    def stop_walk_left(self):
        if self.player.direction == -1 or self.next_direction == -1:
            self.stop_walking()

    def stop_walking(self):
        self._stop_running()
        self.still_walking = False
        if self.player.state == 'walk':
            self.player.state = 'idle'
        self.next_state = 'idle'

        if self.player.secondary_state in ('walk', 'run'):
            self.player.secondary_state = ''

    def action_end_of_state(self):
        if not self.player.dead and not self.player.sleeping:

            if not self.player.is_on_ground:
                if self.still_walking:
                    if self.still_running:
                        self.player.secondary_state = 'run'
                    else:
                        self.player.secondary_state = 'walk'
                else:
                    self.player.secondary_state = ''

            if self.player.state == 'land':
                self.player.secondary_state = ''

            if self.player.state == 'dash':
                self.player.state = 'fall'

            if not self.player.is_on_ground:
                if self.player.state in ('jump',) or self.next_state in ('walk', 'run', 'prejump'):
                    self.next_state = self.player.state
                else:
                    self.next_state = 'fall'

            if self.player.state == 'jump' and self.player.is_on_ground:
                self.next_state = 'jump'
            self.player.direction = self.next_direction
            if self.player.air_control:
                self.player.air_control = self.player.direction

            self.player.state = self.next_state

            if self.player.is_on_ground:
                if self.still_walking:
                    if self.still_running:
                        self.next_state = 'run'
                    else:
                        self.next_state = 'walk'
                else:
                    if self.player.state != 'jump':
                        self.next_state = 'idle'
                    else:
                        self.next_state = 'jump'
            else:
                if self.player.state in ('jump',):
                    self.next_state = self.player.state
                else:
                    self.next_state = 'fall'
                if self.still_walking:
                    self.player.air_control = self.player.direction

        elif self.player.dead:
            if self.player.state != 'die':
                self.player.state = 'die'
                self.next_state = 'die'
            else:
                self.player.hide()

        else:
            if self.player.state == 'hit':
                self.tp_to_stable_ground()
                self.player.state = 'idle'
                self.player.sleeping = False
            else:
                self.player.state = 'hit'

    def action_die(self):
        if not self.player.sleeping and not self.player.dead:
            if self.player_loose_one_life():
                self.player.dead = True
            else:
                self.player.sleeping = True

    def player_loose_one_life(self):
        self.player_lives -= 1

        heart = self.hearts[self.player_lives]
        heart.state = 'empty'

        if self.player_lives == 0:
            self.player_lives = self.player_data.max_lives
            self.player_death()
            self.player_data.current_lives.set(self.player_lives, self.current_save_id)

            return True
        else:
            self.player.position_handler.body.position = self.player.position_handler.body.position.x, 5000
            self.player.state = 'hit'
            self.player_data.current_lives.set(self.player_lives, self.current_save_id)

            return False

    def player_death(self):

        triggers = self.player.position_handler.triggers
        if self.on_death_trigger_id in triggers:
            triggers[self.on_death_trigger_id].enabled = True
        else:
            logger.warning(f'no trigger with id {self.on_death_trigger_id}')

        self.player.state = 'die'

        new_pos = self.on_death()
        self.player.position_handler.body.position = new_pos
        self.player.position_handler.body.velocity = (0, 0)

        self.player_data.pos_x.set(new_pos[0], self.current_save_id)
        self.player_data.pos_y.set(new_pos[1], self.current_save_id)

    def tp_to_stable_ground(self):
        x = self.player_data.pos_x.get(self.current_save_id)
        y = self.player_data.pos_y.get(self.current_save_id)
        self.player.position_handler.body.position = x, y
        self.player.physic_state_updater.space.reindex_shapes_for_body(self.player.position_handler.body)

    def action_reanimate(self):
        self.player.dead = False
        self.player.state = 'idle'
        self.player.direction = 1
        self.next_direction = 1

        for heart in self.hearts:
            heart.state = 'full'

    def action_reset_dash(self):
        self.already_dashed = False


