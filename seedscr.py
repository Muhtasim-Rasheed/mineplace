import pygame
import random
import utils

def play_click_sound():
    utils.SoundManager.playsound(utils.resource_path("assets/sounds/click.ogg"))

class SeedScreen():
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 40)
        self.seed_input = TextInput("Seed: ", self.font, 16)

    def run(self):
        clock = pygame.time.Clock()
        tick = 0
        while True:
            clock.tick(60)
            self.screen.fill((0, 0, 0))
            self.seed_input.draw(self.screen, 200, 200)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        play_click_sound()
                        if self.seed_input.text == "":
                            return str(random.randint(0, 9999999999999999))
                        return self.seed_input.text
                self.seed_input.update(event, tick)

class TextInput():
    def __init__(self, prompt, font, allowed_chars):
        self.prompt = prompt
        self.font = font
        self.text = ""
        self.rendered = self.font.render(self.prompt + self.text + "_", True, (255, 255, 255))
        self.allowed_chars = allowed_chars

    def draw(self, screen, x, y):
        screen.blit(self.rendered, (x, y))

    def update(self, event, tick):
        show_underscore = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return self.text
            elif len(self.text) < self.allowed_chars:
                self.text += event.unicode
        
        if not len(self.text) < self.allowed_chars: 
            show_underscore = False
        
        tick_limited = tick % 60

        if show_underscore and tick_limited < 30:
            self.rendered = self.font.render(self.prompt + self.text + "_", True, (255, 255, 255))
        else:
            self.rendered = self.font.render(self.prompt + self.text, True, (255, 255, 255))
