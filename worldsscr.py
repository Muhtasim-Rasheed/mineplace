import utils
import pygame
from keybindsscr import KEYBINDS

def play_click_sound():
    utils.SoundManager.playsound(utils.resource_path("assets/sounds/click.ogg"))

class WorldsScreen:
    def __init__(self, screen, options_per_page=10):
        self.screen = screen
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 24)
        self.worlds = utils.WorldManager.all_world_files()
        self.current = 0
        self.options_per_page = options_per_page

    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.screen.fill((0, 0, 0))

            # Calculate the current page and the range of options to display
            total_pages = (len(self.worlds) + self.options_per_page - 1) // self.options_per_page
            current_page = self.current // self.options_per_page
            start_index = current_page * self.options_per_page
            end_index = min(start_index + self.options_per_page, len(self.worlds))

            # Display options for the current page
            for i, world in enumerate(self.worlds[start_index:end_index]):
                actual_index = start_index + i
                color = (255, 255, 255) if actual_index == self.current else (100, 100, 100)
                prefix = "> " if actual_index == self.current else ""
                suffix = " <" if actual_index == self.current else ""
                optiontext = Text(f"{prefix}{world} v{utils.WorldManager.get_world_ver(world)}{suffix}", self.font, color)
                optiontext.draw(self.screen, 200, 200 + i * 30)

            # Display page info at the bottom
            page_text = Text(f"Page {current_page + 1} of {total_pages}", self.font, (150, 150, 150))
            page_text.draw(self.screen, 200, 200 + self.options_per_page * 30)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == KEYBINDS.close_menus):
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    play_click_sound()
                    if event.key == KEYBINDS.menu_up:
                        self.current = max(0, self.current - 1)  # Prevent going below 0
                    if event.key == KEYBINDS.menu_down:
                        self.current = min(len(self.worlds) - 1, self.current + 1)  # Prevent overflow
                    if event.key == KEYBINDS.menu_left:
                        self.current = max(0, self.current - self.options_per_page)  # Move to previous page
                    if event.key == KEYBINDS.menu_right:
                        self.current = min(len(self.worlds) - 1, self.current + self.options_per_page)  # Move to next page
                    if event.key == KEYBINDS.delete_world:
                        utils.WorldManager.delete_world(self.worlds[self.current])
                        self.current = max(0, self.current - 1)  # Move to previous world
                        self.worlds = utils.WorldManager.all_world_files()
                    if event.key == KEYBINDS.key_return:
                        return self.worlds[self.current]


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
