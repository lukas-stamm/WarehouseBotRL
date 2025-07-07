import pygame
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from Classes import warehouse_env as whe
from Classes import map as m
from Classes import dropzone as d
import time

# Pygame init
pygame.init()
pygame.display.set_mode((1, 1))

class SlowDownCallback(BaseCallback):
    """
    Simple SB3 callback to slow down training steps with a sleep delay.
    """
    def __init__(self, delay_s=0):
        super().__init__()
        self.delay_s = delay_s

    def _on_step(self) -> bool:
        time.sleep(self.delay_s)
        return True

# Setup
TMX_PATH = "Assets/Maps/BaselineMap.tmx"

pickup_locations = {
    "A": (3, 4),
}

delivery_zones = {
    "A": d.Dropzone((6, 13), (9, 14), "A"),
}

all_sprites_group = pygame.sprite.Group()
render_layer_group = pygame.sprite.Group()

game_map = m.Map(
    tmx_path=TMX_PATH,
    all_sprites_group=all_sprites_group,
    render_layer_group=render_layer_group,
    pickup_locations=pickup_locations,
    delivery_zones=delivery_zones
)

robot_start_pos = (14, 4)
pickup_item_types = ["A"]
tile_size = 32
max_steps = 200

# Create Environment
env = whe.WarehouseEnv(
    map_obj=game_map,
    robot_start_pos=robot_start_pos,
    pickup_item_types=pickup_item_types,
    tile_size=tile_size,
    max_steps=max_steps
)

# Baseline TensorBoard log directory
log_dir = f"./tensorboard_logs/run_{int(time.time())}/"

# PPO Agent with TensorBoard logging
model = PPO(
    policy="MlpPolicy",
    env=env,
    verbose=1,
    tensorboard_log=log_dir
)

# slow_callback = SlowDownCallback(delay_s=0.02)

# Train with slowdown
TOTAL_TIMESTEPS = 100_000
model.learn(total_timesteps=TOTAL_TIMESTEPS)

# Save Model
model.save("Models/warehouse_policy_baseline")

print("Baseline training complete. Model saved as 'warehouse_policy_baseline.zip'.")

# Clean up
env.close()
pygame.quit()