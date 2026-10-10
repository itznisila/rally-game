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