import utils
import pygame

class KeybindsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 24)
        self.keybinds = [
            "WASD - Move (no gravity included)",
            "Arrow keys - Move the block selector",
            "Space - Place block",
            "C - Break block",
            "KL - Switch blocks",
            "Escape - Exit out of most screens"
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
