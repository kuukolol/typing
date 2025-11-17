import pygame
from src.game import TypingGame

pygame.init()
pygame.mixer.init()

if __name__ == "__main__":
    TypingGame().run()
