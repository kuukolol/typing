import pygame
from .constants import DARK_GRAY, WHITE, GREEN, YELLOW, RED


class Brain:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.health = 100
        self.max_health = 100
        self.brain_radius = 28
        self.glow_radius = 150
        self.glow_intensity = 0.0
        self.glow_direction = 1
        self.brain_x = self.x
        self.brain_y = self.y

    def update(self, dt: float):
        self.glow_intensity += self.glow_direction * dt * 1.5
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -1
        elif self.glow_intensity <= 0.4:
            self.glow_intensity = 0.4
            self.glow_direction = 1

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(
            screen,
            (255, 180, 200),
            (int(self.brain_x), int(self.brain_y)),
            self.brain_radius,
        )
        pygame.draw.circle(
            screen,
            (255, 150, 180),
            (int(self.brain_x), int(self.brain_y)),
            self.brain_radius - 5,
        )
        pygame.draw.circle(
            screen,
            (255, 120, 160),
            (int(self.brain_x), int(self.brain_y)),
            self.brain_radius - 9,
        )

    def draw_health_bar(self, screen: pygame.Surface):
        bar_width = 140
        bar_height = 12
        bar_x = self.x - bar_width // 2
        bar_y = self.brain_y - self.brain_radius - 35

        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        health_color = (
            GREEN if self.health > 50 else YELLOW if self.health > 25 else RED
        )
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        font = pygame.font.Font(None, 24)
        txt = font.render(f"{int(self.health)}%", True, WHITE)
        screen.blit(txt, txt.get_rect(center=(self.x, bar_y - 15)))

