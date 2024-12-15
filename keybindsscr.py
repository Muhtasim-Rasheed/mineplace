import utils
import pygame
import os
import json


def play_click_sound():
    utils.SoundManager.playsound(utils.resource_path("assets/sounds/click.ogg"))


class Keybinds:
    def __init__(self):
        # If file at ~/mineplace/settings.txt or %APPDATA%/mineplace/settings.txt exists, load settings from there
        # If not, create the file and write the default settings to it
        # self.keybinds_file = ""
        # if os.name == "nt":
        #     self.keybinds_file = os.getenv("APPDATA")
        # else:
        #     self.keybinds_file = os.path.expanduser("~")
        #
        # self.keybinds_file = os.path.join(self.keybinds_file, "mineplace", "keybinds.json")
        # if not os.path.exists(self.keybinds_file):
        #     os.makedirs(os.path.dirname(self.keybinds_file), exist_ok=True)
        #     with open(self.keybinds_file, "w") as f:
        #         f.write(json.dumps(self.settings))
        # else:
        #     with open(self.keybinds_file) as f:
        #         self.settings_file_contents = json.loads(f.read())
        #         for setting in self.settings_file_contents:
        #             self.settings[setting] = self.settings_file_contents[setting]
        self.move_up = pygame.K_w
        self.move_down = pygame.K_s
        self.move_left = pygame.K_a
        self.move_right = pygame.K_d
        self.move_blockselector_up = pygame.K_UP
        self.move_blockselector_down = pygame.K_DOWN
        self.move_blockselector_left = pygame.K_LEFT
        self.move_blockselector_right = pygame.K_RIGHT
        self.place_block = pygame.K_SPACE
        self.break_block = pygame.K_c
        self.switch_block_left = pygame.K_k
        self.switch_block_right = pygame.K_l
        self.close_menus = pygame.K_ESCAPE
        self.menu_up = pygame.K_UP
        self.menu_down = pygame.K_DOWN
        self.menu_left = pygame.K_LEFT
        self.menu_right = pygame.K_RIGHT
        self.delete_world = pygame.K_d


class KeybindsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 24)
        self.keybinds = [
            "WASD to move",
            "Arrow keys to move block selector",
            "Space to place block",
            "C to break block",
            "KL to switch block to place",
            "Escape to exit out of almost all menus (fixing this soon)",
            "Up / Down to go through world list or any option list",
            "Left / Right to go through pages in world list or change settings value in settings menu",
            "D (in world list) to delete world",
        ]

    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.screen.fill((0, 0, 0))
            for i, keybind in enumerate(self.keybinds):
                keybindtext = Text(keybind, self.font, (255, 255, 255))
                keybindtext.draw(self.screen, 200, 200 + i * 30)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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
