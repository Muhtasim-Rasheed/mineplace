import utils
import pygame
from keybindsscr import KEYBINDS


def play_click_sound():
    utils.SoundManager.playsound(utils.resource_path("assets/sounds/click.ogg"))

class CreditsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 24)
        self.big_font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 40)
        self.credits = [
            "Game Dev - YT/@MutasimosDoesProgramming",
            "Texture artist - Modrinth/user/P4ncake",
            "Windows port builder - Discord @bill_cipher345",
            "Python - python.org",
            "Pygame - pygame.org",
            "And you for playing!"
        ]

    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.screen.fill((0, 0, 0))
            for i, credit in enumerate(self.credits):
                credittext = Text(credit, self.font, (255, 255, 255))
                credittext.draw(self.screen, 200, 250 + i * 30)

            title = Text("# Mineplace", self.big_font, (255, 255, 0))
            title.draw(self.screen, 200, 200)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == KEYBINDS.close_menus):
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    play_click_sound()
                    return "exit"

class Text:
    def __init__(self, text, font, color):
        self.text = text
        self.font = font
        self.color = color
        self.rendered = self.font.render(self.text, True, self.color)

    def rerender(self):
        self.rendered = self.font.render(self.text, True, self.color)

    def update_properties(self, text=None, font=None, color=None):
        if text is not None:
            self.text = text
        if font is not None:
            self.font = font
        if color is not None:
            self.color = color
        self.rerender()

    def draw(self, screen, x, y):
        screen.blit(self.rendered, (x, y))
