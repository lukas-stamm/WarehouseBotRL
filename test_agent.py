import pygame
from stable_baselines3 import PPO
from Classes import warehouse_env as whe
from Classes import map as m
from Classes import dropzone as d
import time

# Pygame init
pygame.init()
pygame.display.set_mode((1, 1))  # to satisfy pytmx loading

# Setup map just like in training
TMX_PATH = "Assets/Maps/ObstacleMap.tmx"

pickup_locations = {
    "A": (2, 3),
}

delivery_zones = {
    "A": d.Dropzone((3, 13), (6, 14), "A"),
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

robot_start_pos = (13, 3)
pickup_item_types = ["A"]
tile_size = 32
max_steps = 200

# Create environment
env = whe.WarehouseEnv(
    map_obj=game_map,
    robot_start_pos=robot_start_pos,
    pickup_item_types=pickup_item_types,
    tile_size=tile_size,
    max_steps=max_steps
)

# Load the trained model
model = PPO.load("Models/warehouse_policy_obstacle")

# Run one test episode
obs, _ = env.reset()
done = False
step_count = 0

while not done:
    # Model chooses an action based on the current observation
    action, _states = model.predict(obs, deterministic=True)

    # Environment transitions
    obs, reward, done, truncated, info = env.step(action)

    # Render to Pygame window
    env.render()

    # OPTIONAL: slow down for human eyes
    pygame.time.wait(100)  # 200ms delay between steps

    step_count += 1

print(f"Test run complete in {step_count} steps.")

# Clean up
env.close()
pygame.quit()