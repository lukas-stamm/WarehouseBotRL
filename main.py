import pygame, sys
from pygame.locals import QUIT

from Classes.dropzone import Dropzone
from Classes.map import Map
from Classes.robot import Robot
from Classes.item import Item
from Classes.dropzone import Dropzone
from helper import get_non_overlapping_spawn

pygame.init()
screen = pygame.display.set_mode((1024, 1024))
clock = pygame.time.Clock()

# Create sprite group and load map
sprite_group = pygame.sprite.LayeredUpdates()

game_map = Map('Assets/Map.tmx', sprite_group)

dropzone_a = Dropzone(pos=(96,928), groups=sprite_group, accepted_types='a')
dropzone_b = Dropzone(pos=(800,928), groups=sprite_group, accepted_types='b')

a = Item(pos=(176,176), groups=sprite_group, type='a')
sprite_group.change_layer(a, 1)
b = Item(pos=(848,176), groups=sprite_group, type='b')
sprite_group.change_layer(b, 1)

a_respawn_time = None
b_respawn_time = None

robots = []

for id in range(1, 2):
    spawn = get_non_overlapping_spawn(robots, 528, 176, 48, 48, 32)
    robot = Robot(id=f'bot{id}', pos=spawn, groups=sprite_group, collision_group=game_map.collision_group)
    robots.append(robot) # 1 = outline only
    sprite_group.change_layer(robot, 2)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    current_time = pygame.time.get_ticks()

    for robot in robots:
        colliding_entities = pygame.sprite.spritecollide(robot, sprite_group, False, collided=pygame.sprite.collide_rect)
        robot.update()
        for entity in colliding_entities:
            if isinstance(entity, Item):
                robot.pickup_item(entity)
            elif current_time - robot.last_delivery_time > robot.delivery_cooldown:
                if isinstance(entity, Dropzone):
                    robot.deliver_item(entity)
                    robot.last_delivery_time = current_time

        #respawn item
        # Handle item A
        if a and not a.alive():
            if a_respawn_time is None:
                a_respawn_time = current_time  # start the timer
            elif current_time - a_respawn_time >= 3000:
                a = Item(pos=(176, 176), groups=sprite_group, type='a')
                sprite_group.change_layer(a, 1)
                a_respawn_time = None  # reset

        # Handle item B
        if b and not b.alive():
            if b_respawn_time is None:
                b_respawn_time = current_time
            elif current_time - b_respawn_time >= 3000:
                b = Item(pos=(848, 176), groups=sprite_group, type='b')
                sprite_group.change_layer(b, 1)
                b_respawn_time = None

        # if not b.alive():
            # b = Item(pos=(848, 176), groups=sprite_group, type='b')

    screen.fill((0, 0, 0))
    screen.fill((0, 0, 0))
    sprite_group.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()