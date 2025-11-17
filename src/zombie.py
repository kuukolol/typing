import pygame
import math
from dataclasses import dataclass
from .constants import GREEN, WHITE, GRAY


@dataclass
class ZombieData:
    x: float
    y: float
    word: str
    typed_chars: str
    zombie_type: int
    path_progress: float
    is_highlighted: bool = False
    is_dead: bool = False
    from_right: bool = False


class Zombie:
    ZOMBIE_Y_OFFSET = 20

    def __init__(self, zombie_data: ZombieData, zombie_images: dict):
        self.data = zombie_data
        self.images = zombie_images
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 0.2
        self.width = 256
        self.height = 256
        self.speed_multiplier = 1.0

    def update(self, dt: float, tx: int, ty: int):
        if self.data.is_dead:
            return

        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            if "walk" in self.images and len(self.images["walk"]):
                self.current_frame = (self.current_frame + 1) % len(self.images["walk"])

        speed = 30 * dt * self.speed_multiplier
        dx, dy = tx - self.data.x, ty - self.data.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 5:
            self.data.x += (dx / distance) * speed
            self.data.y += (dy / distance) * speed

    def draw(self, screen, font):
        if self.data.is_dead:
            return

        img = None
        if "walk" in self.images:
            frames = self.images["walk"]
            if frames:
                img = frames[self.current_frame]

        if img:
            if self.data.from_right:
                img = pygame.transform.flip(img, True, False)

            img = pygame.transform.scale(img, (self.width, self.height))

            screen.blit(
                img,
                (
                    self.data.x - self.width // 2,
                    self.data.y - self.height // 2 + Zombie.ZOMBIE_Y_OFFSET,
                ),
            )
        else:
            pygame.draw.rect(
                screen,
                GRAY,
                (
                    self.data.x - self.width // 2,
                    self.data.y - self.height // 2 + Zombie.ZOMBIE_Y_OFFSET,
                    self.width,
                    self.height,
                ),
            )

        word_y = self.data.y - self.height // 2 + 100

        typed = self.data.typed_chars
        remaining = self.data.word[len(typed) :]

        if typed:
            t1 = font.render(typed, True, GREEN)
            t2 = font.render(remaining, True, WHITE)

            x_center = self.data.x
            screen.blit(t1, (x_center - t1.get_width() // 2, word_y))
            screen.blit(t2, (x_center + t1.get_width() // 2, word_y))
        else:
            t = font.render(self.data.word, True, WHITE)
            screen.blit(t, t.get_rect(center=(self.data.x, word_y)))

