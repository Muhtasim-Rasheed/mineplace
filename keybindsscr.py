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
