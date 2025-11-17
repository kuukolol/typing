import pygame
import os
import random
import math
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, GREEN, YELLOW, RED, DARK_GRAY, GRAY
from .brain import Brain
from .zombie import Zombie, ZombieData


class TypingGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Brain Defense - Typing Game")
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = "menu"
        self.score = 0

        brain_x = SCREEN_WIDTH // 2
        brain_y = 450
        self.brain = Brain(brain_x, brain_y)

        self.zombies = []
        self.current_input = ""
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)

        self.spawn_timer = 0
        self.spawn_delay = 3
        self.min_spawn = 1.5

        self.difficulty_timer = 0.0
        self.difficulty_level = 0
        self.game_time = 0.0
        self.game_over = False

        self.background = self.load_background()
        self.zombie_images = self.load_zombies()
        self.word_list = self.load_words()

        self.dark_overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self.dark_overlay.fill((10, 10, 15))
        self.dark_overlay.set_alpha(120)

        self.background_music = self.load_sound("assets/sounds/background-music.mp3")
        self.zombie_sounds = self.load_sound("assets/sounds/Zombie sounds.mp3")
        self.eating_sound = self.load_sound("assets/sounds/zombie-eating-sound.mp3")

        self.play_menu_music()

    def reset_game(self):
        self.score = 0
        self.zombies = []
        self.current_input = ""
        self.spawn_timer = 0
        self.spawn_delay = 3
        self.difficulty_timer = 0.0
        self.difficulty_level = 0
        self.game_time = 0.0
        self.game_over = False
        brain_x = SCREEN_WIDTH // 2
        brain_y = 450
        self.brain = Brain(brain_x, brain_y)

        self.stop_menu_music()
        self.play_zombie_sounds()

    def load_sound(self, path):
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Error loading sound {path}: {e}")
        return None

    def play_menu_music(self):
        if self.background_music:
            try:
                pygame.mixer.music.load("assets/sounds/background-music.mp3")
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Error playing menu music: {e}")

    def stop_menu_music(self):
        pygame.mixer.music.stop()

    def play_zombie_sounds(self):
        if self.zombie_sounds:
            try:
                pygame.mixer.music.load("assets/sounds/Zombie sounds.mp3")
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Error playing zombie sounds: {e}")

    def play_eating_sound(self):
        if self.eating_sound:
            try:
                self.eating_sound.play()
            except Exception as e:
                print(f"Error playing eating sound: {e}")

    def load_background(self):
        path = "assets/background.png"
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            w, h = img.get_size()
            scale = max(SCREEN_WIDTH / w, SCREEN_HEIGHT / h)
            return pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        return None

    def load_words(self):
        path = "words.txt"
        words = []
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    w = line.strip().lower()
                    if w.isalpha():
                        words.append(w)
        return words

    def split_sheet(self, sheet):
        frames = []
        w, h = sheet.get_size()
        frame_w = h if w > h else w
        count = w // frame_w
        for i in range(count):
            frames.append(sheet.subsurface((i * frame_w, 0, frame_w, h)))
        return frames

    def load_zombies(self):
        data = {}
        for i in range(1, 5):
            folder = f"assets/Zombie_{i}"
            if not os.path.exists(folder):
                continue
            data[i] = {}
            walk = os.path.join(folder, "Walk.png")
            idle = os.path.join(folder, "Idle.png")
            if os.path.exists(walk):
                img = pygame.image.load(walk).convert_alpha()
                data[i]["walk"] = self.split_sheet(img)
            if os.path.exists(idle):
                img = pygame.image.load(idle).convert_alpha()
                data[i]["idle"] = self.split_sheet(img)
        return data

    def spawn_zombie(self):
        side = random.choice(["left", "right"])
        x = -70 if side == "left" else SCREEN_WIDTH + 70
        y = SCREEN_HEIGHT // 2 + random.randint(-50, 50)

        data = ZombieData(
            x=float(x),
            y=float(y),
            word=random.choice(self.word_list),
            typed_chars="",
            zombie_type=random.randint(1, 4),
            path_progress=0,
            from_right=(side == "right"),
        )

        zombie = Zombie(data, self.zombie_images.get(data.zombie_type, {}))
        zombie.speed_multiplier = 1.0 + (self.difficulty_level * 0.5)
        self.zombies.append(zombie)

    def update_typing(self, char):
        if not char:
            return

        c = char.lower()
        highlighted = [
            z for z in self.zombies if z.data.is_highlighted and not z.data.is_dead
        ]

        if highlighted:
            z = highlighted[0]
            expected = z.data.word[
                len(z.data.typed_chars) : len(z.data.typed_chars) + 1
            ]
            if c == expected:
                z.data.typed_chars += c
                if z.data.typed_chars == z.data.word:
                    points = len(z.data.word) * 5
                    self.score += points
                    z.data.is_dead = True
                    self.zombies.remove(z)
                    for zz in self.zombies:
                        zz.data.is_highlighted = False
            else:
                for z in self.zombies:
                    z.data.typed_chars = ""
                    z.data.is_highlighted = False
        else:
            matches = [
                z
                for z in self.zombies
                if z.data.word.startswith(c) and not z.data.is_dead
            ]
            for z in self.zombies:
                z.data.is_highlighted = z in matches
            if matches:
                matches[0].data.typed_chars = c

    def get_difficulty_interval(self, level):
        if level <= 3:
            return 30.0
        elif level <= 6:
            return 60.0
        else:
            return 60.0

    def get_difficulty_tag(self, level):
        if level <= 3:
            return "Easy"
        elif level <= 6:
            return "Medium"
        else:
            return "Hard"

    def get_difficulty_color(self, level):
        if level <= 3:
            return GREEN
        elif level <= 6:
            return YELLOW
        else:
            return RED

    def update(self, dt):
        if not self.game_over:
            self.game_time += dt
            self.difficulty_timer += dt

            current_interval = self.get_difficulty_interval(self.difficulty_level)

            if self.difficulty_timer >= current_interval:
                self.difficulty_timer = 0.0
                self.difficulty_level += 1
                speed_mult = 1.0 + (self.difficulty_level * 0.5)
                for zombie in self.zombies:
                    zombie.speed_multiplier = speed_mult
                for _ in range(self.difficulty_level):
                    self.spawn_zombie()

            base_spawn_delay = 3.0
            if self.difficulty_level > 0:
                base_spawn_delay = max(0.8, 3.0 - (self.difficulty_level * 0.3))

            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                if self.difficulty_level > 0:
                    self.spawn_delay = max(0.8, base_spawn_delay - 0.05)
                else:
                    self.spawn_delay = max(self.min_spawn, self.spawn_delay - 0.05)
                self.spawn_zombie()

        self.brain.update(dt)

        for z in self.zombies[:]:
            z.update(dt, self.brain.brain_x, self.brain.brain_y)
            d = math.dist(
                (z.data.x, z.data.y), (self.brain.brain_x, self.brain.brain_y)
            )
            if d < self.brain.brain_radius + 30:
                self.brain.health -= 5
                self.play_eating_sound()
                z.data.is_dead = True
                self.zombies.remove(z)
                if self.brain.health <= 0:
                    self.brain.health = 0
                    self.game_over = True

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_GRAY)

        self.screen.blit(self.dark_overlay, (0, 0))

        self.brain.draw(self.screen)

        for z in self.zombies:
            z.draw(self.screen, self.font)

        self.brain.draw_health_bar(self.screen)

        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        difficulty_tag = self.get_difficulty_tag(self.difficulty_level)
        difficulty_color = self.get_difficulty_color(self.difficulty_level)
        difficulty_text = self.small_font.render(
            f"Difficulty: {difficulty_tag} (Level {self.difficulty_level})",
            True,
            difficulty_color,
        )
        self.screen.blit(difficulty_text, (10, 35))

        time_text = self.small_font.render(
            f"Time: {int(self.game_time // 60)}:{int(self.game_time % 60):02d}",
            True,
            GRAY,
        )
        self.screen.blit(time_text, (10, 60))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            txt = self.font.render("GAME OVER", True, RED)
            sub = self.small_font.render("Press R to Restart", True, WHITE)

            self.screen.blit(
                txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            )
            self.screen.blit(
                sub, sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            )

    def draw_menu(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_GRAY)

        self.screen.blit(self.dark_overlay, (0, 0))

        title = self.title_font.render("Brain Defense", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        play_text = self.font.render("1. Play Game", True, GREEN)
        help_text = self.font.render("2. Help", True, YELLOW)
        quit_text = self.font.render("ESC. Quit", True, RED)

        y_start = 350
        spacing = 60

        self.screen.blit(
            play_text, play_text.get_rect(center=(SCREEN_WIDTH // 2, y_start))
        )
        self.screen.blit(
            help_text, help_text.get_rect(center=(SCREEN_WIDTH // 2, y_start + spacing))
        )
        self.screen.blit(
            quit_text,
            quit_text.get_rect(center=(SCREEN_WIDTH // 2, y_start + spacing * 2)),
        )

    def draw_help(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_GRAY)

        self.screen.blit(self.dark_overlay, (0, 0))

        title = self.font.render("Instructions", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        instructions = [
            "Type the first letter of a zombie's word to target it",
            "Complete the word to eliminate the zombie",
            "Each letter is worth 5 points",
            "Example: 'game' (4 letters) = 20 points",
            "Protect the brain from reaching zombies!",
            "",
            "Press ESC to return to menu",
        ]

        y_start = 250
        spacing = 35

        for i, instruction in enumerate(instructions):
            if instruction:
                text = self.small_font.render(instruction, True, WHITE)
                text_rect = text.get_rect(
                    center=(SCREEN_WIDTH // 2, y_start + i * spacing)
                )
                self.screen.blit(text, text_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.stop_menu_music()
                            self.state = "menu"
                            self.score = 0
                            self.zombies = []
                            self.current_input = ""
                            self.spawn_timer = 0
                            self.spawn_delay = 3
                            self.difficulty_timer = 0.0
                            self.difficulty_level = 0
                            self.game_time = 0.0
                            self.game_over = False
                            brain_x = SCREEN_WIDTH // 2
                            brain_y = 450
                            self.brain = Brain(brain_x, brain_y)
                            self.play_menu_music()
                        elif self.state == "help":
                            self.state = "menu"
                        else:
                            self.running = False

                    if self.state == "menu":
                        if event.key == pygame.K_1 or event.unicode == "1":
                            self.state = "playing"
                            self.reset_game()
                        elif event.key == pygame.K_2 or event.unicode == "2":
                            self.state = "help"

                    elif self.state == "playing":
                        if self.game_over and event.key == pygame.K_r:
                            self.reset_game()
                            continue

                        if event.unicode.isalpha():
                            self.update_typing(event.unicode)
                            self.current_input += event.unicode
                        elif event.key == pygame.K_BACKSPACE:
                            self.current_input = ""

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "help":
                self.draw_help()
            elif self.state == "playing":
                self.update(dt)
                self.draw()

            pygame.display.flip()

