import utils
import pygame

def play_click_sound():
    utils.SoundManager.playsound(utils.resource_path("assets/sounds/click.ogg"))

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
