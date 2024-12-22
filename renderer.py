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
        self.small_font = pygame.font.Font(utils.resource_path("assets/fonts/W95FA.otf"), 20)
        self.texture_names = [
                "dirt",
                "stone", "cobblestone", "stone_bricks",
                "coal_ore", "iron_ore", "gold_ore", "diamond_ore",
                "coal_block", "iron_block", "gold_block", "diamond_block",
                "bricks",
                "oak_planks", "oak_log", "oak_leaves",
                "oak_stairs_ur", "oak_stairs_ul", "oak_stairs_dr", "oak_stairs_dl", "oak_slab_u", "oak_slab_d",
                "water", "water_surface", "water_flow",
                "glass", "sand", "gravel",
                "redstone_dust_on", "redstone_dust_off", "redstone_block", "redstone_repeater_on", "redstone_repeater_off",
                "redstone_lamp_on", "redstone_lamp_off", "redstone_observer_u", "redstone_observer_d", "redstone_observer_l", "redstone_observer_r",
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
        ignorelist = ["air", "oak_leaves", "water", "water_surface", "water_flow"]
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

    def add_shadow(self, surface, neighbourcount, neighbors, block=None):
        if block != None:
            if block.name == "water":
                return
            if block.getattr("state") == "on":
                return

        # Create a shadow surface with transparency
        shadow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Fill the shadow surface with a base shadow alpha
        base_alpha = neighbourcount * (255 // 8)
        shadow.fill((0, 0, 0, base_alpha))

        # Adjust alpha for adjacent air blocks (not diagonal ones)
        for y, row in enumerate(neighbors):
            for x, block in enumerate(row):
                if block:
                    continue
                if (y, x) in [(0, 0), (0, 2), (2, 0), (2, 2)]:
                    continue
                shadow.fill((0, 0, 0, neighbourcount * (255 // 12)))

        # Create a mask from the transparency of the original surface
        mask = pygame.mask.from_surface(surface)  # Generates a mask for non-transparent pixels
        shadow_mask = mask.to_surface(setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))

        # Apply the mask to the shadow
        shadow.blit(shadow_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Blit the shadow onto the original surface
        surface.blit(shadow, (0, 0))

    def render(self, world, player, isNight=False):
        player_x, player_y = player.pos

        self.background.draw(isNight)

        special_naming_cases = ["oak_stairs", "oak_slab", "redstone_dust", "redstone_repeater", "redstone_lamp", "redstone_observer", "water"]

        for y, column in enumerate(world):
            for x, block in enumerate(column):
                if block.name == "air":
                    continue

                # Determine the texture name to use without modifying block.name
                if block.name not in self.textures and block.name not in special_naming_cases:
                    print(f"Block {block.name} not found in textures")
                    texture_to_use = "missing"
                else:
                    texture_to_use = block.name
                
                if block.name == "oak_stairs":
                    texture_to_use = "oak_stairs_" + block.getattr("orientation")
                elif block.name == "oak_slab":
                    texture_to_use = "oak_slab_" + block.getattr("orientation")
                elif block.name == "redstone_dust":
                    texture_to_use = "redstone_dust_" + block.getattr("state")
                elif block.name == "redstone_repeater":
                    texture_to_use = "redstone_repeater_" + block.getattr("state")
                elif block.name == "redstone_lamp":
                    texture_to_use = "redstone_lamp_" + block.getattr("state")
                elif block.name == "redstone_observer":
                    texture_to_use = "redstone_observer_" + block.getattr("orientation")
                elif block.name == "water":
                    # Default texture is "water"
                    texture_to_use = "water"

                    # Check if there's no water above: use "water_surface"
                    if y - 1 >= 0 and world[y - 1][x].name != "water":
                        texture_to_use = "water_surface"

                    # Check for water flow: water to the left or right
                    if (x - 1 >= 0 and world[y][x - 1].name == "water") or \
                       (x + 1 < self.game_width and world[y][x + 1].name == "water"):
                        texture_to_use = "water_flow"

                    # Reset to "water" if there's water above (priority over water_flow)
                    if y - 1 >= 0 and world[y - 1][x].name == "water":
                        texture_to_use = "water"

                    # Special case: if a block is on both sides, revert to "water"
                    if x - 1 >= 0 and x + 1 < self.game_width and \
                       world[y][x - 1].name != "air" and world[y][x + 1].name != "air":
                        texture_to_use = "water"
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
                if texture_to_use == "redstone_dust_on":
                    # Redstone dust has a power attribute, which is from 0 - 15
                    # Draw this as a number on the block
                    power = block.getattr("power")
                    text = self.small_font.render(str(power), True, (255, 255, 255))
                    self.screen.blit(text, (x * self.game_block_scale, y * self.game_block_scale))
                if block.name == "redstone_observer":
                    # Show its orientation
                    orientation = block.getattr("orientation")
                    text = self.small_font.render(orientation, True, (255, 255, 255))
                    self.screen.blit(text, ((x + 1) * self.game_block_scale, y * self.game_block_scale))
                if block.name == "redstone_repeater":
                    if block.getattr("orientation") == "r":
                        texture = pygame.transform.flip(texture, True, False)
                # Resize the texture to the game block scale
                texture = pygame.transform.scale(texture, (self.game_block_scale, self.game_block_scale))
                # Add shadow
                if not self.skip_shadow:
                    neighbourcount, neighbors = self.calculate_block_neighbourcount(world, x, y)
                    self.add_shadow(texture, neighbourcount, neighbors, block)

                # If the current block is water, make it a bit transparent
                if block.name == "water":
                    texture.set_alpha(150)

                # If the texture to use is water_flow, and if there is a water block to the right instead of the left, flip it
                if texture_to_use == "water_flow":
                    if x - 1 >= 0 and world[y][x - 1].name == "water":
                        texture = pygame.transform.flip(texture, True, False)

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
        elif selected_block.name == "redstone_dust":
            texture_to_use = "redstone_dust_" + selected_block.getattr("state")
        elif selected_block.name == "redstone_repeater":
            texture_to_use = "redstone_repeater_" + selected_block.getattr("state")
        elif selected_block.name == "redstone_lamp":
            texture_to_use = "redstone_lamp_" + selected_block.getattr("state")
        elif selected_block.name == "redstone_observer":
            texture_to_use = "redstone_observer_" + selected_block.getattr("orientation")
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
        if selected_block.name == "redstone_repeater":
            if selected_block.getattr("orientation") == "r":
                texture = pygame.transform.flip(texture, True, False)
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
