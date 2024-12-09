import pygame
import random
import json
import os
import utils

class Renderer:
    def __init__(self, screen, game_width, game_height, game_block_scale):
        self.screen = screen
        self.game_width = game_width
        self.game_height = game_height
        self.game_block_scale = game_block_scale
        self.font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 40)
        self.texture_names = [
                "dirt",
                "stone", "cobblestone", "stone_bricks",
                "coal_ore", "iron_ore", "gold_ore", "diamond_ore",
                "oak_planks", "oak_log", "oak_leaves",
                "oak_stairs_ur", "oak_stairs_ul", "oak_stairs_dr", "oak_stairs_dl", "oak_slab_u", "oak_slab_d",
                "missing"
                ]
        self.textures = {}
        self.load_textures()
        self.background = Background(screen)
        self.flippable_blocks = ["stone"]
        self.flip_block_grid = [] # Grid of 0, 1, 2, 3 (0 = None, 1 = H, 2 = V, 3 = Both)
        self.calculate_flip_block()
        self.skip_shadow = False

    def load_textures(self):
        for name in self.texture_names:
            texture_path = utils.resource_path(f"assets/textures/{name}.png")
            texture = pygame.image.load(texture_path)
            self.textures[name] = texture

        # Process JSON texture files
        textures_dir = utils.resource_path("assets/textures")
        for filename in [f for f in os.listdir(textures_dir) if f.endswith(".json")]:
            file_path = os.path.join(textures_dir, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                loaded_textures = {}
                for texture_name, texture_filename in data["textures"].items():
                    texture_path = utils.resource_path(f"assets/textures/{texture_filename}")
                    texture = pygame.image.load(texture_path)
                    loaded_textures[texture_name] = texture
                self.textures[os.path.basename(filename).replace(".json", "")] = loaded_textures

    def calculate_flip_block(self):
        # Returns 0, 1, 2, 3 (0 = None, 1 = H, 2 = V, 3 = Both) in a 2D grid
        for _ in range(self.game_height):
            grid_row = []
            for _ in range(self.game_width):
                grid_row.append(random.randint(0, 3))
            self.flip_block_grid.append(grid_row)

    def calculate_block_neighbourcount(self, world, x, y):
        count = 0
        ignorelist = ["air", "oak_leaves"]
        arr = []
        for dx in range(-1, 2):
            row = []
            for dy in range(-1, 2):
                push = False
                if dx == 0 and dy == 0:
                    continue
                if y + dy < 0 or y + dy >= self.game_height or x + dx < 0 or x + dx >= self.game_width:
                    count += 1
                    push = True
                    continue
                if world[y + dy][x + dx].name not in ignorelist:  # Swap indices
                    count += 1
                    push = True
                row.append(push)
            arr.append(row)
        return count, arr

    def add_shadow(self, surface, neighbourcount, neighbors):
        shadow = pygame.Surface(surface.get_size())
        shadow.fill((0, 0, 0))
        shadow.set_alpha(neighbourcount * (255 // 8))
        # If any of the adjacent blocks are air, not the diagonal ones, then instead make the alpha neighborcount * (255 // 12)
        for y, row in enumerate(neighbors):
            for x, block in enumerate(row):
                if block:
                    continue
                if y == 0 and x == 0:
                    continue
                if y == 0 and x == 2:
                    continue
                if y == 2 and x == 0:
                    continue
                if y == 2 and x == 2:
                    continue
                shadow.set_alpha(neighbourcount * (255 // 12))
        surface.blit(shadow, (0, 0))

    def render(self, world, player, isNight=False):
        player_x, player_y = player.pos

        self.background.draw(isNight)

        special_naming_cases = ["oak_stairs", "oak_slab"]

        for y, column in enumerate(world):
            for x, block in enumerate(column):
                if block.name == "air":
                    continue

                # Determine the texture name to use without modifying block.name
                if block.name not in self.textures and block.name not in special_naming_cases:
                    print(f"Block {block.name} not found in textures")
                    texture_to_use = "missing"
                elif block.name == "oak_stairs":
                    texture_to_use = "oak_stairs_" + block.getattr("orientation")
                elif block.name == "oak_slab":
                    texture_to_use = "oak_slab_" + block.getattr("orientation")
                else:
                    texture_to_use = block.name

                if isinstance(self.textures[texture_to_use], dict):
                    # If the block has multiple layers, render them in order
                    for texture_name in self.textures[texture_to_use]:
                        texture = self.textures[texture_to_use][texture_name]
                        texture = pygame.transform.scale(texture, (self.game_block_scale, self.game_block_scale))
                        if not self.skip_shadow:
                            neighbourcount, neighbours = self.calculate_block_neighbourcount(world, x, y)
                            self.add_shadow(texture, neighbourcount, neighbours)

                        if block.name in self.flippable_blocks:
                            if x >= self.game_width or y >= self.game_height:
                                continue
                            flip = self.flip_block_grid[y][x]
                            if flip == 1:
                                texture = pygame.transform.flip(texture, True, False)
                            elif flip == 2:
                                texture = pygame.transform.flip(texture, False, True)
                            elif flip == 3:
                                texture = pygame.transform.flip(texture, True, True)

                        self.screen.blit(texture, (x * self.game_block_scale, y * self.game_block_scale))
                    continue

                texture = self.textures[texture_to_use]
                if texture_to_use == "oak_log":
                    if block.getattr("horiz") == "T":
                        texture = pygame.transform.rotate(texture, 90)
                # Resize the texture to the game block scale
                texture = pygame.transform.scale(texture, (self.game_block_scale, self.game_block_scale))
                # Add shadow
                if not self.skip_shadow:
                    neighbourcount, neighbors = self.calculate_block_neighbourcount(world, x, y)
                    self.add_shadow(texture, neighbourcount, neighbors)

                # Flip the texture
                if block.name in self.flippable_blocks:
                    if x >= self.game_width or y >= self.game_height:
                        continue
                    flip = self.flip_block_grid[y][x]
                    if flip == 1:
                        texture = pygame.transform.flip(texture, True, False)
                    elif flip == 2:
                        texture = pygame.transform.flip(texture, False, True)
                    elif flip == 3:
                        texture = pygame.transform.flip(texture, True, True)

                self.screen.blit(texture, (x * self.game_block_scale, y * self.game_block_scale))

        steve_image = pygame.image.load(utils.resource_path("assets/game/steve.png"))
        steve_image = pygame.transform.scale(steve_image, (self.game_block_scale, self.game_block_scale))
        self.screen.blit(steve_image, (player_x * self.game_block_scale, player_y * self.game_block_scale))

        blockselector_x, blockselector_y = player.blockselector
        blockselector_x += player_x
        blockselector_y += player_y

        selected_block = player.placeable_blocks[player.selected_block]
        if selected_block.name not in self.textures and selected_block.name not in special_naming_cases:
            texture_to_use = "missing"
        elif selected_block.name == "oak_stairs":
            texture_to_use = "oak_stairs_" + selected_block.getattr("orientation")
        elif selected_block.name == "oak_slab":
            texture_to_use = "oak_slab_" + selected_block.getattr("orientation")
        else:
            texture_to_use = selected_block.name

        texture = self.textures[texture_to_use]
        if isinstance(texture, dict):
            texture = pygame.Surface((self.game_block_scale, self.game_block_scale))
            for layer in self.textures[texture_to_use].values():
                layer = pygame.transform.scale(layer, (self.game_block_scale, self.game_block_scale))
                texture.blit(layer, (0, 0))
        if texture_to_use == "oak_log":
            if selected_block.getattr("horiz") == "T":
                texture = pygame.transform.rotate(texture, 90)
        texture = pygame.transform.scale(texture, (self.game_block_scale, self.game_block_scale))
        texture.set_alpha(150)
        self.screen.blit(texture, (blockselector_x * self.game_block_scale, blockselector_y * self.game_block_scale))

        pygame.draw.rect(self.screen, (255, 255, 255), 
                         (blockselector_x * self.game_block_scale, blockselector_y * self.game_block_scale, 
                          self.game_block_scale, self.game_block_scale), 1)

class Background:
    def __init__(self, screen):
        self.day = pygame.image.load(utils.resource_path("assets/game/day.png"))
        self.day = pygame.transform.scale(self.day, (screen.get_width(), screen.get_height()))
        self.night = pygame.image.load(utils.resource_path("assets/game/night.png"))
        self.night = pygame.transform.scale(self.night, (screen.get_width(), screen.get_height()))
        self.screen = screen

    def draw(self, night=False):
        self.screen.blit(self.day, (0, 0))
        if night:
            self.screen.blit(self.night, (0, 0))
