import math
import pygame

pygame.init()

# ----- Window and timing -----
WIDTH, HEIGHT = 1000, 700
FPS = 60
CX, CY = WIDTH // 2, HEIGHT // 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rally Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 72)

# ----- Colours -----
GRASS = (60, 120, 60)
ROAD = (90, 90, 90)
SAND = (194, 170, 110)
WHITE = (255, 255, 255)
ROCK = (125, 125, 130)
ROCK_DARK = (70, 70, 75)
ROCK_SHINE = (170, 170, 175)
CAR_BLUE = (30, 90, 200)
CRASH_RED = (255, 80, 80)

# ----- Track layout -----
ROAD_OUTER_SIZE = (900, 600)       # outer edge of the road oval
ROAD_INNER_SIZE = (500, 300)       # grass infield inside the road
LANE_RX, LANE_RY = 350, 225        # middle of the road (lane line + checkpoints)
LANE_LINE_WIDTH = 4
PARKED_RX, PARKED_RY = 480, 330    # parked cars sit just outside the road
PARKED_RADIUS = 12
PARKED_SHIFT = 10                  # distance of the 2 circles from a car's centre
CHECKPOINT_ANGLES = (0, 90, 180, 270)

# ----- Surface friction (higher = slows the car more) -----
FRICTION_ROAD = 1.0
FRICTION_GRASS = 3.0
FRICTION_SAND = 5.0

# ----- Car physics -----
START_X, START_Y = CX, CY - 262
ACCEL = 300
BRAKE = 500
STEER = 140
MAX_REVERSE_SPEED = 100
MIN_STEER_SPEED = 10               # the car must be moving to steer
CAR_RADIUS = 14

# ----- Gameplay -----
CHECKPOINT_RADIUS = 90
CRASH_MESSAGE_TIME = 1.0           # seconds the crash message stays on screen

# ----- HUD and pause screen -----
HUD_X, HUD_Y = 15, 12
HUD_LINE_HEIGHT = 28
PAUSE_HINT_OFFSET = 55


def point_on_ellipse(deg, rx, ry):
    r = math.radians(deg)
    return (CX + rx * math.cos(r), CY + ry * math.sin(r))


def make_car(braking, body=CAR_BLUE):
    """Draw a car picture. Front = right side, back = left side."""
    img = pygame.Surface((44, 22), pygame.SRCALPHA)
    pygame.draw.rect(img, body, (0, 0, 44, 22), border_radius=5)            # body
    pygame.draw.rect(img, (30, 30, 30), (24, 3, 10, 16))                    # windscreen
    # headlights (front)
    pygame.draw.rect(img, (255, 255, 160), (40, 4, 3, 4))
    pygame.draw.rect(img, (255, 255, 160), (40, 14, 3, 4))
    # brake lights (back): dark red normally, bright red when braking
    light = (255, 40, 40) if braking else (120, 0, 0)
    pygame.draw.rect(img, light, (1, 4, 3, 4))
    pygame.draw.rect(img, light, (1, 14, 3, 4))
    return img


track = pygame.Surface((WIDTH, HEIGHT))
track.fill(GRASS)

outer_sand = [(90, 90, 65), (910, 100, 60), (80, 620, 60), (915, 610, 65)]
for sx, sy, sr in outer_sand:
    pygame.draw.circle(track, SAND, (sx, sy), sr)

road_w, road_h = ROAD_OUTER_SIZE
infield_w, infield_h = ROAD_INNER_SIZE
pygame.draw.ellipse(track, ROAD, (CX - road_w // 2, CY - road_h // 2, road_w, road_h))
pygame.draw.ellipse(track, GRASS, (CX - infield_w // 2, CY - infield_h // 2, infield_w, infield_h))

inner_sand = [(CX - 60, CY - 20, 55), (CX + 90, CY + 40, 40)]
for sx, sy, sr in inner_sand:
    pygame.draw.circle(track, SAND, (sx, sy), sr)

# dashed lane line around the middle of the road
for deg in range(0, 360, 8):
    p1 = point_on_ellipse(deg, LANE_RX, LANE_RY)
    p2 = point_on_ellipse(deg + 4, LANE_RX, LANE_RY)
    pygame.draw.line(track, WHITE, p1, p2, LANE_LINE_WIDTH)

# start / finish line
pygame.draw.line(track, WHITE, (CX, CY - road_h // 2), (CX, CY - infield_h // 2), LANE_LINE_WIDTH)

rocks = [
    (50, 50, 16), (160, 35, 12), (935, 55, 18), (840, 40, 12),
    (45, 650, 15), (150, 668, 12), (955, 645, 17), (850, 662, 13),
    (CX - 170, CY - 30, 15), (CX + 120, CY + 70, 14),
    (CX - 20, CY + 90, 12), (CX + 170, CY - 40, 13),
]

for rx, ry, rr in rocks:
    pygame.draw.circle(track, ROCK_DARK, (rx, ry), rr + 2)
    pygame.draw.circle(track, ROCK, (rx, ry), rr)
    pygame.draw.circle(track, ROCK_SHINE, (rx - rr // 3, ry - rr // 3), rr // 3)  # shine

parked_circles = []


def add_parked_car(deg, body):
    """Park a car just outside the road at this angle, pointing along the road."""
    px, py = point_on_ellipse(deg, PARKED_RX, PARKED_RY)
    t = math.radians(deg)
    heading = math.degrees(math.atan2(PARKED_RY * math.cos(t), -PARKED_RX * math.sin(t)))
    img = pygame.transform.rotate(make_car(False, body), -heading)
    track.blit(img, img.get_rect(center=(px, py)))  # paint it onto the track
    for shift in (-PARKED_SHIFT, PARKED_SHIFT):  # 2 circles = back and front of the car
        circle_x = px + math.cos(math.radians(heading)) * shift
        circle_y = py + math.sin(math.radians(heading)) * shift
        parked_circles.append((circle_x, circle_y, PARKED_RADIUS))


PARKED = [
    (20, (240, 200, 40)),  # yellow
    (75, (235, 235, 235)),  # white
    (130, (240, 130, 30)),  # orange
    (175, (90, 200, 230)),  # light blue
    (240, (210, 40, 40)),  # red
    (300, (150, 60, 180)),  # purple
    (340, (240, 120, 170)),  # pink
]
for deg, colour in PARKED:
    add_parked_car(deg, colour)

obstacles = rocks + parked_circles


def surface_friction(x, y):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return FRICTION_GRASS
    colour = track.get_at((int(x), int(y)))[:3]
    if colour == GRASS:
        return FRICTION_GRASS
    if colour == SAND:
        return FRICTION_SAND
    return FRICTION_ROAD


checkpoints = [point_on_ellipse(d, LANE_RX, LANE_RY) for d in CHECKPOINT_ANGLES]
LAST_CHECKPOINT = len(checkpoints) - 1

x, y, angle, speed = START_X, START_Y, 0, 0

car_normal = make_car(False)
car_braking = make_car(True)

next_cp = 0
laps = 0
lap_time = 0.0
best_lap = None
crash_timer = 0.0
paused = False

running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            paused = not paused

    if paused:
        # Keep the last frame on screen and show a PAUSED message.
        # Nothing moves and the lap timer stops while paused.
        msg = big_font.render("PAUSED", True, WHITE)
        screen.blit(msg, msg.get_rect(center=(CX, CY)))
        hint = font.render("Press P to resume", True, WHITE)
        screen.blit(hint, hint.get_rect(center=(CX, CY + PAUSE_HINT_OFFSET)))
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        speed += ACCEL * dt
    if keys[pygame.K_DOWN]:
        speed -= BRAKE * dt
    speed = max(speed, -MAX_REVERSE_SPEED)
    speed -= speed * surface_friction(x, y) * dt

    if abs(speed) > MIN_STEER_SPEED:
        direction = 1 if speed > 0 else -1
        if keys[pygame.K_LEFT]:
            angle -= STEER * dt * direction
        if keys[pygame.K_RIGHT]:
            angle += STEER * dt * direction

    x += math.cos(math.radians(angle)) * speed * dt
    y += math.sin(math.radians(angle)) * speed * dt
    x = max(0, min(WIDTH, x))
    y = max(0, min(HEIGHT, y))

    for ox, oy, orad in obstacles:
        if math.hypot(x - ox, y - oy) < orad + CAR_RADIUS:
            x, y, angle, speed = START_X, START_Y, 0, 0
            next_cp = 0
            lap_time = 0.0
            crash_timer = CRASH_MESSAGE_TIME
            break
    crash_timer = max(0.0, crash_timer - dt)

    lap_time += dt
    cx, cy = checkpoints[next_cp]
    if math.hypot(x - cx, y - cy) < CHECKPOINT_RADIUS:
        if next_cp == LAST_CHECKPOINT:
            laps += 1
            if best_lap is None or lap_time < best_lap:
                best_lap = lap_time
            lap_time = 0.0
            next_cp = 0
        else:
            next_cp += 1

    # --- draw ---
    screen.blit(track, (0, 0))
    car_img = car_braking if keys[pygame.K_DOWN] else car_normal
    rotated = pygame.transform.rotate(car_img, -angle)
    screen.blit(rotated, rotated.get_rect(center=(x, y)))

    hud = [
        f"Lap: {laps}",
        f"Time: {lap_time:5.1f}s",
        f"Best: {best_lap:5.1f}s" if best_lap else "Best: --",
        f"Speed: {abs(int(speed))}",
    ]
    for i, text in enumerate(hud):
        screen.blit(font.render(text, True, WHITE), (HUD_X, HUD_Y + i * HUD_LINE_HEIGHT))

    if crash_timer > 0:
        msg = big_font.render("CRASH! Restarting...", True, CRASH_RED)
        screen.blit(msg, msg.get_rect(center=(CX, CY)))

    pygame.display.flip()

pygame.quit()