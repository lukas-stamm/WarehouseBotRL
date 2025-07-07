import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from Classes import item as i
from Classes import robot as r


class WarehouseEnv(gym.Env):
    """
    Gym-compatible environment for RL training of warehouse delivery agent.
    """

    metadata = {"render_modes": ["human"]}

    def __init__( self, map_obj, robot_start_pos, pickup_item_types, tile_size=32, max_steps=500):
        super().__init__()

        # Store environment configuration
        self.map = map_obj
        self.robot_start_pos = robot_start_pos
        self.pickup_item_types = pickup_item_types
        self.tile_size = tile_size
        self.max_steps = max_steps

        # Pygame sprite group to hold items
        self.item_group = pygame.sprite.Group()
        # Robot instance (initialized in reset)
        self.robot = None
        # Step counter
        self.steps = 0

        # Track deliveries
        self.deliveries_done = 0
        self.max_deliveries = 3

        # Track item respawn timers
        self.respawn_timers = {item_type: 0 for item_type in self.pickup_item_types}
        self.respawn_delay_steps = 10  # e.g. delay of 10 steps after pickup

        # Defines Action Space
        self.action_space = spaces.Discrete(4)  # LEFT, RIGHT, UP, DOWN

        # -- Define Observation Space --
        # E.g.:
        # [robot_x, robot_y, held_item_onehot(2), pickups (2*len)]
        obs_dim = 2 + 2 + 2 * len(self.pickup_item_types)
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(obs_dim,),
            dtype=np.float32
        )

        self.screen = None

    def reset(self, seed=None, options=None):
        """
        Gym API method to reset the environment at the start of an episode.
        """
        super().reset(seed=seed)
        self.steps = 0

        # Reset delivery counter and timers
        self.deliveries_done = 0
        self.respawn_timers = {item_type: 0 for item_type in self.pickup_item_types}

        # -- Reset robot --
        if self.robot:
            self.robot.kill()
        self.robot = r.Robot(
            bot_id=1,
            grid_pos=self.robot_start_pos,
            groups=(self.map.all_sprites_group,),
            grid_size=(self.map.width, self.map.height),
            tile_size=self.tile_size
        )

        # -- Reset items --
        for sprite in self.item_group:
            sprite.kill()
        self.item_group.empty()

        for item_type in self.pickup_item_types:
            pickup_pos = self.map.get_pickup_location(item_type)
            if pickup_pos:
                i.Item(
                    grid_pos=pickup_pos,
                    tile_size=self.tile_size,
                    groups=(self.map.all_sprites_group, self.item_group),
                    item_type=item_type
                )

        return self.get_observation(), {}

    def step(self, action):
        action = int(action)
        self.steps += 1
        reward = -1.0  # step cost
        terminated = False
        info = {}

        # -- Propose move --
        new_x, new_y = self.robot.propose_move(action)
        if self.map.is_blocked(new_x, new_y):
            reward -= 5.0  # collision penalty
        else:
            self.robot.set_position(new_x, new_y)

        # -- Check pickup --
        for item in list(self.item_group):
            if (item.grid_x, item.grid_y) == (self.robot.grid_x, self.robot.grid_y):
                self.robot.pickup_item(item)
                item.kill()
                reward += 5.0

                # Start respawn timer
                self.respawn_timers[item.item_type] = self.respawn_delay_steps

                break

        # -- Check delivery --
        if self.robot.held_item_type:
            dropzone = self.map.get_delivery_zone(self.robot.held_item_type)
            if dropzone and dropzone.contains(self.robot.grid_x, self.robot.grid_y):
                delivered = self.robot.deliver_item(dropzone)
                if delivered:
                    reward += 10.0

                    # Increment deliveries
                    self.deliveries_done += 1
                    print(f"Delivery count: {self.deliveries_done}")

        # Handle respawn timers
        for item_type in self.pickup_item_types:
            if self.respawn_timers[item_type] > 0:
                self.respawn_timers[item_type] -= 1
                if self.respawn_timers[item_type] == 0:
                    # Respawn item
                    pickup_pos = self.map.get_pickup_location(item_type)
                    if pickup_pos:
                        i.Item(
                            grid_pos=pickup_pos,
                            tile_size=self.tile_size,
                            groups=(self.map.all_sprites_group, self.item_group),
                            item_type=item_type
                        )

        # -- Check episode termination --
        if self.steps >= self.max_steps:
            terminated = True

        # End episode after 3 deliveries
        if self.deliveries_done >= self.max_deliveries:
            terminated = True
            print("3 deliveries achieved. Ending episode.")

        observation = self.get_observation()
        self.render()
        return observation, reward, terminated, False, info

    def get_observation(self):
        """
        Builds observation vector.
        Example design (all normalized 0..1):
        [robot_x, robot_y, held_item_onehot, pickup positions...]
        """
        obs = []

        # Normalization helper
        def norm(v, maxv):
            return v / maxv if maxv else 0.0

        # -- Robot position --
        obs.append(norm(self.robot.grid_x, self.map.width - 1))
        obs.append(norm(self.robot.grid_y, self.map.height - 1))

        # -- Held item one-hot --
        if self.robot.held_item_type == "A":
            obs += [1.0, 0.0]
        elif self.robot.held_item_type == "B":
            obs += [0.0, 1.0]
        else:
            obs += [0.0, 0.0]

        # -- Pickup locations --
        for item_type in self.pickup_item_types:
            pos = self.map.get_pickup_location(item_type)
            if pos:
                obs.append(norm(pos[0], self.map.width - 1))
                obs.append(norm(pos[1], self.map.height - 1))
            else:
                obs += [0.0, 0.0]

        return np.array(obs, dtype=np.float32)

    def render(self, mode="human"):
        """
        Optional Pygame rendering.
        Call this after step() to update display.
        """
        if not self.screen:
            self.screen = pygame.display.set_mode(
                (self.map.width * self.tile_size, self.map.height * self.tile_size)
            )
            pygame.display.set_caption("Warehouse RL Environment")

        self.screen.fill((0, 0, 0))  # Clear

        # Draw the map
        self.map.render_layer_group.draw(self.screen)
        self.item_group.draw(self.screen)
        self.screen.blit(self.robot.image, self.robot.hitbox)

        # Optional grid
        self.map.draw_grid_debug(self.screen)

        pygame.display.flip()

    def close(self):
        if self.screen:
            pygame.quit()
            self.screen = None