import pygame
import utils
import os
from PIL import Image, ImageFilter

def play_click_sound():
    utils.SoundManager.playsound(utils.resource_path("assets/sounds/click.ogg"))

class TitleScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 30)
        self.big_font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 60)
        self.options = ["new", "load", "settings", "credits", "keybinds", "exit"]
        self.translations = {
            "new": "New Game",
            "load": "Load Game",
            "settings": "Settings",
            "credits": "Credits",
            "keybinds": "Keybinds",
            "exit": "Exit"
        }
        self.current = 0
        self.splashes = []
        with open(utils.resource_path("assets/game/splashes.txt")) as f:
            for line in f:
                self.splashes.append(line.strip())
        self.current_splash = 0
        self.panorama = Panorama(screen)

        self.steve = {
            "steve": pygame.image.load(utils.resource_path("assets/game/steve.png")),
            "rotation": 0,
            "pos": [500, 200]
        }

    def run(self):
        clock = pygame.time.Clock()
        tick = 0
        while True:
            clock.tick(60)
            self.screen.fill((0, 0, 0))
            self.panorama.draw()
            self.steve["rotation"] += 1
            for i, option in enumerate(self.options):
                color = (255, 255, 255) if i == self.current else (100, 100, 100)
                if not i == self.current:
                    optiontext = Text(self.translations[option], self.font, color)
                else:
                    optiontext = Text("> " + self.translations[option] + " <", self.font, color)
                optiontext.draw(self.screen, 200, 350 + i * 40)

            titletext = Text("Mineplace", self.big_font, (255, 255, 0))
            titletext.draw(self.screen, 200, 200)

            versiontext = Text("v1.2.6", self.font, (255, 255, 255))
            versiontext.draw(self.screen, 200, 250)
            
            steve = pygame.transform.scale(self.steve["steve"], (self.steve["steve"].get_width() * 16, self.steve["steve"].get_height() * 16))
            steve = pygame.transform.rotate(steve, self.steve["rotation"])
            rect = steve.get_rect(center=(self.screen.get_width() / 2 + self.steve["pos"][0], self.screen.get_height() / 2 + self.steve["pos"][1]))
            self.screen.blit(steve, rect)

            splash = Text(self.splashes[self.current_splash], self.font, (0, 255, 255))
            if self.current_splash == 29:
                splash.update_properties(color=(0, 255, 0))
            splash.draw(self.screen, 200, 300)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    play_click_sound()
                    if event.key == pygame.K_UP:
                        self.current -= 1
                    if event.key == pygame.K_DOWN:
                        self.current += 1
                    if event.key == pygame.K_RETURN:
                        return self.options[self.current % len(self.options)]

            self.current %= len(self.options)
            if tick % (60 * 3) == 0:
                self.current_splash += 1
                self.current_splash %= len(self.splashes)
            tick += 1

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

class Panorama:
    def __init__(self, screen):
        self.screen = screen
        # IF panorama (blurred) exists, load it, otherwise load the normal panorama and blur it with PIL (radius=8)
        if os.path.exists(utils.resource_path("assets/game/panorama_blurred.png")):
            self.panorama = pygame.image.load(utils.resource_path("assets/game/panorama_blurred.png"))
        else:
            # self.panorama = pygame.image.load(utils.resource_path("assets/game/panorama.png"))
            panorama_image = Image.open(utils.resource_path("assets/game/panorama.png"))
            panorama_image = panorama_image.filter(ImageFilter.GaussianBlur(8))
            panorama_image.save(utils.resource_path("assets/game/panorama_blurred.png"))
            self.panorama = pygame.image.load(utils.resource_path("assets/game/panorama_blurred.png"))
        # Both the panorama and the screen are (64*24)x(32*24) pixels, so we need to scale the panorama by 2
        # to actually be able to scroll it
        self.panorama = pygame.transform.scale(self.panorama, (64*24 * 2, 32*24 * 2))
        self.panorama_x = 0
        self.direction = 1
        self.pos = [0, -self.screen.get_height() / 2]

    def draw(self):
        self.screen.blit(self.panorama, (self.pos[0], self.pos[1]))
        self.panorama_x -= self.direction
        self.pos[0] = self.panorama_x
        if self.panorama_x <= -64*24:
            self.direction = -1
        if self.panorama_x >= 0:
            self.direction = 1
