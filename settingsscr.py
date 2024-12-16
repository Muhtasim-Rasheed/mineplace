import utils
import pygame
import json
import os
from keybindsscr import KEYBINDS


def play_click_sound():
    utils.SoundManager.playsound(utils.resource_path("assets/sounds/click.ogg"))

class SettingsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 24)
        self.big_font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 40)
        self.selected = 0
        self.settings = {
            "volume": 100,
            "panorama_blur": 8,
        }
        # If file at ~/mineplace/settings.txt or %APPDATA%/mineplace/settings.txt exists, load settings from there
        # If not, create the file and write the default settings to it
        self.settings_file = ""
        if os.name == "nt":
            self.settings_file = os.getenv("APPDATA")
        else:
            self.settings_file = os.path.expanduser("~")
        self.settings_file = os.path.join(self.settings_file, "mineplace", "settings.json")
        if not os.path.exists(self.settings_file):
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, "w") as f:
                f.write(json.dumps(self.settings))
        else:
            with open(self.settings_file) as f:
                self.settings_file_contents = json.loads(f.read())
                for setting in self.settings_file_contents:
                    self.settings[setting] = self.settings_file_contents[setting]

    def run(self):
        clock = pygame.time.Clock()
        tick = 0
        while True:
            clock.tick(60)
            self.screen.fill((0, 0, 0))
            for i, setting in enumerate(self.settings):
                color = (255, 255, 255) if i == self.selected else (100, 100, 100)
                if not i == self.selected:
                    settingtext = Text(setting + ": " + str(self.settings[setting]), self.font, color)
                else:
                    settingtext = Text("> " + setting.upper() + ": " + str(self.settings[setting]) + " <", self.font, color)
                settingtext.draw(self.screen, 200, 200 + i * 40)

            titletext = Text("Settings", self.big_font, (255, 255, 0))
            titletext.draw(self.screen, 200, 100)
            
            utils.SettingsManager.apply_settings(self.settings)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == KEYBINDS.close_menus):
                    with open(self.settings_file, "w") as f:
                        f.write(json.dumps(self.settings))
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == KEYBINDS.menu_left:
                        play_click_sound()
                        if self.selected == 0:
                            self.settings["volume"] = max(0, self.settings["volume"] - 5)
                        elif self.selected == 1:
                            self.settings["panorama_blur"] = max(0, self.settings["panorama_blur"] - 1)
                    if event.key == KEYBINDS.menu_right:
                        play_click_sound()
                        if self.selected == 0:
                            self.settings["volume"] = min(100, self.settings["volume"] + 5)
                        elif self.selected == 1:
                            self.settings["panorama_blur"] = min(100, self.settings["panorama_blur"] + 1)
                    if event.key == KEYBINDS.menu_up:
                        play_click_sound()
                        self.selected = (self.selected - 1) % len(self.settings)
                    if event.key == KEYBINDS.menu_down:
                        play_click_sound()
                        self.selected = (self.selected + 1) % len(self.settings)

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
