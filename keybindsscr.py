import utils
import pygame
import os
import json


def play_click_sound():
    utils.SoundManager.playsound(utils.resource_path("assets/sounds/click.ogg"))


class Keybinds:
    def __init__(self):
        self.keybinds_file = ""
        if os.name == "nt":
            self.keybinds_file = os.getenv("APPDATA")
        else:
            self.keybinds_file = os.path.expanduser("~")

        self.keybinds_file = os.path.join(self.keybinds_file, "mineplace", "keybinds.json")
        if not os.path.exists(self.keybinds_file):
            os.makedirs(os.path.dirname(self.keybinds_file), exist_ok=True)
            with open(self.keybinds_file, "x") as f:
                json.dump({}, f)
            set_default_config = True
        else:
            set_default_config = False

        if set_default_config:
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
            self.key_return = pygame.K_RETURN
            self.prt_sc = pygame.K_PRINTSCREEN
            self.backspace = pygame.K_BACKSPACE
            self.export_keybinds_to_file()
        else:
            with open(self.keybinds_file, "r") as f:
                keybinds = json.load(f)
            self.move_up = keybinds["move_up"]
            self.move_down = keybinds["move_down"]
            self.move_left = keybinds["move_left"]
            self.move_right = keybinds["move_right"]
            self.move_blockselector_up = keybinds["move_blockselector_up"]
            self.move_blockselector_down = keybinds["move_blockselector_down"]
            self.move_blockselector_left = keybinds["move_blockselector_left"]
            self.move_blockselector_right = keybinds["move_blockselector_right"]
            self.place_block = keybinds["place_block"]
            self.break_block = keybinds["break_block"]
            self.switch_block_left = keybinds["switch_block_left"]
            self.switch_block_right = keybinds["switch_block_right"]
            self.close_menus = keybinds["close_menus"]
            self.menu_up = keybinds["menu_up"]
            self.menu_down = keybinds["menu_down"]
            self.menu_left = keybinds["menu_left"]
            self.menu_right = keybinds["menu_right"]
            self.delete_world = keybinds["delete_world"]
            self.key_return = keybinds["key_return"]
            self.prt_sc = keybinds["prt_sc"]
            self.backspace = keybinds["backspace"]

    def export_keybinds_to_file(self):
        with open(self.keybinds_file, "r") as f:
            keybinds = json.load(f)
        keybinds = {
            "move_up": self.move_up,
            "move_down": self.move_down,
            "move_left": self.move_left,
            "move_right": self.move_right,
            "move_blockselector_up": self.move_blockselector_up,
            "move_blockselector_down": self.move_blockselector_down,
            "move_blockselector_left": self.move_blockselector_left,
            "move_blockselector_right": self.move_blockselector_right,
            "place_block": self.place_block,
            "break_block": self.break_block,
            "switch_block_left": self.switch_block_left,
            "switch_block_right": self.switch_block_right,
            "close_menus": self.close_menus,
            "menu_up": self.menu_up,
            "menu_down": self.menu_down,
            "menu_left": self.menu_left,
            "menu_right": self.menu_right,
            "delete_world": self.delete_world,
            "key_return": self.key_return,
            "prt_sc": self.prt_sc,
            "backspace": self.backspace
        }
        with open(self.keybinds_file, "w") as f:
            json.dump(keybinds, f)


KEYBINDS = Keybinds()


class KeybindsScreen:
    def __init__(self, screen):
        # This new keybind screen lets the user change the keybinds
        self.screen = screen
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 24)
        
        # Key translations (pygame key to string) (All keys on a keyboard)
        self.translations = {}
        for key in dir(pygame):
            if key.startswith("K_"):
                self.translations[getattr(pygame, key)] = key[2:].capitalize()
        
        # Keybinds
        self.action_translations = {
            "move_up": "Move up",
            "move_down": "Move down",
            "move_left": "Move left",
            "move_right": "Move right",
            "move_blockselector_up": "Move block selector up",
            "move_blockselector_down": "Move block selector down",
            "move_blockselector_left": "Move block selector left",
            "move_blockselector_right": "Move block selector right",
            "place_block": "Place block",
            "break_block": "Break block",
            "switch_block_left": "Switch block left",
            "switch_block_right": "Switch block right",
            "close_menus": "Close menus",
            "menu_up": "Menu up",
            "menu_down": "Menu down",
            "menu_left": "Menu left",
            "menu_right": "Menu right",
            "delete_world": "Delete world",
            "key_return": "Select",
            "prt_sc": "Print screen",
            "backspace": "Backspace"
        }

        self.options = list(self.action_translations.keys())

        self.current = 0

        self.is_changing = False

    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.screen.fill((0, 0, 0))
            for i, action in enumerate(self.action_translations):
                color = (255, 255, 255) if i == self.current else (100, 100, 100)
                if not i == self.current:
                    actiontext = Text(f"{self.action_translations[action]}: {self.translations[getattr(KEYBINDS, action)]}", self.font, color)
                else:
                    actiontext = Text(f"> {self.action_translations[action]}: {self.translations[getattr(KEYBINDS, action)]} <", self.font, color)
                actiontext.draw(self.screen, 100, 75 + i * 30)
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == KEYBINDS.close_menus):
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    # Wait! We're changing keybinds!
                    if self.is_changing:
                        play_click_sound()
                        setattr(KEYBINDS, self.options[self.current], event.key)
                        KEYBINDS.export_keybinds_to_file()
                        self.is_changing = False

                    play_click_sound()
                    if event.key == pygame.K_UP:
                        self.current -= 1
                    if event.key == pygame.K_DOWN:
                        self.current += 1
                    if event.key == pygame.K_RETURN:
                        # return self.options[self.current % len(self.options)] # This is what we'd do if this was a normal menu, but nonono, we're changing keybinds
                        self.is_changing = True
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
