import math
import pygame

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

GRASS = (60, 120, 60)
ROAD = (90, 90, 90)
CX, CY = WIDTH // 2, HEIGHT // 2
track = pygame.Surface((WIDTH, HEIGHT))
track.fill(GRASS)
pygame.draw.ellipse(track, ROAD, (CX - 450, CY - 300, 900, 600))
pygame.draw.ellipse(track, GRASS, (CX - 250, CY - 150, 500, 300))

def on_grass(x, y):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        return track.get_at((int(x), int(y)))[:3] == GRASS
    return True

MID_RX, MID_RY = 350, 225
def point_on_track(deg):
    r = math.radians(deg)
    return (CX + MID_RX * math.cos(r), CY + MID_RY * math.sin(r))

checkpoints = [point_on_track(0), point_on_track(90),
               point_on_track(180), point_on_track(270)]

x, y = CX, CY - 225
angle = 0
speed = 0
ACCEL = 300
BRAKE = 500
STEER = 140

next_cp = 0
laps = 0
lap_time = 0.0
best_lap = None

car_img = pygame.Surface((44, 22), pygame.SRCALPHA)
pygame.draw.rect(car_img, (220, 30, 30), (0, 0, 44, 22), border_radius=5)
pygame.draw.rect(car_img, (30, 30, 30), (26, 3, 10, 16))

running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()
