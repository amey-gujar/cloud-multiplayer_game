
import pygame
import sys
import random

from ws_client import start_network_thread, send_input, get_latest_state, send_ping
from map import GameMap
from camera import Camera
from player import Player


pygame.init()


# Screen Settings
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Cloud Arena"
)


# World Settings
WORLD_WIDTH = 3000
WORLD_HEIGHT = 2000


# Clock
clock = pygame.time.Clock()
FPS = 60


camera = Camera(
    WIDTH,
    HEIGHT,
    WORLD_WIDTH,
    WORLD_HEIGHT
)

game_map = GameMap()
local_id = f"player_{random.randint(1000, 9999)}"
start_network_thread("wss://cloud-multiplayer-game.onrender.com", local_id, "TestUser")

players_dict = {}
server_pellets = []
safe_zone = None
last_ping_time = pygame.time.get_ticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    move_x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
    move_y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
    shooting = pygame.mouse.get_pressed()[0]

    aim_x, aim_y = 0, 0
    if local_id in players_dict:
        aim_x, aim_y = players_dict[local_id].get_aim_direction(camera)
    send_input({
        "move_x": move_x,
        "move_y": move_y,
        "aim_x": aim_x,
        "aim_y": aim_y,
        "shoot": shooting,
    })

    current_time = pygame.time.get_ticks()
    if current_time - last_ping_time > 30000:
        send_ping()
        last_ping_time = current_time

    state = get_latest_state()
    print(f"Network State: {state}")
    if state is not None:
        for p_data in state.get("players", []):
            pid = p_data["id"]
            if pid not in players_dict:
                players_dict[pid] = Player(
                    pid, p_data["x"], p_data["y"], is_local=(pid == local_id)
                )
            players_dict[pid].update_from_server(p_data)
        server_pellets = state.get("pellets", [])
        safe_zone = state.get("zone", None)
        if local_id in players_dict:
            camera.target = players_dict[local_id].position

    screen.fill((0, 0, 0))
    game_map.draw(screen, camera)
    if safe_zone:
        zone_center = camera.world_to_screen((safe_zone[0], safe_zone[1]))
        pygame.draw.circle(screen, (80, 180, 255),
                           (int(zone_center[0]), int(zone_center[1])),
                           int(safe_zone[2]), 2)
    for pellet in server_pellets:
        pellet_pos = camera.world_to_screen((pellet[0], pellet[1]))
        pygame.draw.circle(screen, (255, 220, 0),
                           (int(pellet_pos[0]), int(pellet_pos[1])), 5)
    for player in players_dict.values():
        player.draw(screen, camera)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()