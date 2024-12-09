import opensimplex
import random
import pygame
import json
import sys, os
from PIL import Image, ImageFilter

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def map_noise_to_height(noise_value, height):
    # Normalize noise from [-1, 1] to [0, 1]
    normalized_value = (noise_value + 1) / 2

    # Map to the range [0, height]
    mapped_value = normalized_value * height

    # Round to nearest integer
    return int(mapped_value)

class SoundManager:
    @staticmethod
    def checkmixer_online():
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    @staticmethod
    def playsound(soundfile_path):
        SoundManager.checkmixer_online()
        pygame.mixer.music.load(soundfile_path)
        pygame.mixer.music.play()

class SettingsManager:
    @staticmethod
    def apply_settings(settings):
        SoundManager.checkmixer_online()
        pygame.mixer.music.set_volume(settings["volume"] / 100)
        
        panorama_image = Image.open(resource_path("assets/game/panorama.png"))
        panorama_image = panorama_image.filter(ImageFilter.GaussianBlur(settings["panorama_blur"]))
        panorama_image.save(resource_path("assets/game/panorama_blurred.png"))

class Block:
    def __init__(self, name, attr={}):
        self.name = name
        self.attr = attr

    def __repr__(self):
        # Turns a dict to [key=value, key=value, ...]
        string = ", ".join([f"{key}=\"{value}\"" for key, value in self.attr.items()])
        return self.name + "[" + string + "]"

    def getattr(self, key):
        return self.attr.get(key, None)

    def copy(self):
        return Block(self.name, self.attr.copy())

    @staticmethod
    def from_string(string):
        # Turns a string like "dirt[color=\"brown\"]" to a Block object
        import re

        # Match the block name and attributes
        match = re.match(r"(\w+)\[(.*)\]", string)

        if not match:
            # If no attributes are provided, return a block with just a name
            return Block(name=string.strip())

        # Extract the name and attributes
        name = match.group(1)
        attr_string = match.group(2)

        # Parse attributes into a dictionary
        attr = {}
        if attr_string:
            # Split attributes by commas and parse key="value" pairs
            attr_pairs = attr_string.split(", ")
            for pair in attr_pairs:
                key, value = pair.split("=")
                attr[key] = value.strip("\"")  # Remove surrounding quotes

        return Block(name=name, attr=attr)

class WorldGenerator:
    def __init__(self, seed, width, height, scale=0.1):
        self.seed = seed
        self.noise = opensimplex.OpenSimplex(seed)
        self.width = width
        self.height = height
        self.scale = scale  # Added scale factor

    def generate(self):
        # Uses 1D noise to generate a heightmap to later generate the world
        heightmap = []
        for x in range(self.width):
            noise_value = self.noise.noise2(x * self.scale, 0)  # Scaled noise
            noise_value = map_noise_to_height(noise_value, self.height)
            noise_value -= 2
            heightmap.append(noise_value)

        oremap = []
        for x in range(self.width):
            column = []
            for y in range(self.height):
                noise_value = self.noise.noise2(x * self.scale, y * self.scale)
                # Do NOT allow negatives, so map them from [-1, 1] to [0, 1]
                noise_value = (noise_value + 1) / 2
                column.append(noise_value)
            oremap.append(column)

        orethresholds = {
            "diamond_ore": 0.66,
            "gold_ore": 0.6,
            "iron_ore": 0.5,
            "coal_ore": 0.3
        }

        world = []
        for x in range(self.width):
            column = []
            for y in range(self.height):
                terrain_height = heightmap[x]

                # Add a second noise layer for caves
                cave_noise = self.noise.noise2(x * self.scale, y * self.scale)
                is_cave = cave_noise > 0.5  # Adjust threshold for cave density
                
                if y == terrain_height and not is_cave:
                    column.append(Block("grass"))
                elif y > terrain_height - 3 and y < terrain_height and not is_cave:
                    column.append(Block("dirt"))
                elif y < terrain_height and not is_cave:
                    # WAIT! What if we can add some ores here?
                    for ore, threshold in orethresholds.items():
                        if oremap[x][y] > threshold:
                            # BUT! The higher we are, the lower chance of spawning ores
                            if random.random() < 0.3 - (y / self.height):
                                column.append(Block(ore))
                            break
                    column.append(Block("stone"))
                elif is_cave and y < terrain_height:
                    column.append(Block("air"))
                else:
                    column.append(Block("air"))
            world.append(column)

        # Transpose it
        world = list(map(list, zip(*world)))

        # Flip it
        world = world[::-1]

        # Wait! Let's add some trees!
        for x in range(self.width):
            for y in range(self.height):
                if world[y][x].name == "grass" and random.random() < 0.1:
                    structure = StructureManager.load_structure("oak_tree")
                    world = StructureManager.place_structure(world, structure, x, y + 1)

        return world

class Player:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.blockselector = [0, 0]
        self.placeable_blocks = [
                Block("grass"),
                Block("dirt"),
                Block("stone"),
                Block("cobblestone"),
                Block("stone_bricks"),
                Block("coal_ore"),
                Block("iron_ore"),
                Block("gold_ore"),
                Block("diamond_ore"),
                Block("oak_planks"),
                Block("oak_log"), # Horizontal = false
                Block("oak_log", {"horiz": "T"}), # Horizontal = true
                Block("oak_stairs", {"orientation": "ur"}), # Upper right
                Block("oak_stairs", {"orientation": "ul"}), # Upper left
                Block("oak_stairs", {"orientation": "dl"}), # Down left
                Block("oak_stairs", {"orientation": "dr"}), # Down right
                Block("oak_slab", {"orientation": "u"}), # Upper
                Block("oak_slab", {"orientation": "d"}), # Down
                Block("oak_leaves"),
        ]
        self.selected_block = 0

    def keypress(self, world, keys, tick):
        # if event.type == pygame.KEYDOWN:
        if keys[pygame.K_a]:
            # Move left
            if tick % 2 != 0:
                return
            if self.pos[0] > 0 and world[self.pos[1]][self.pos[0] - 1].name == "air":
                self.pos[0] -= 1
        if keys[pygame.K_d]:
            # Move right
            if tick % 2 != 0:
                return
            if self.pos[0] < len(world[0]) - 1 and world[self.pos[1]][self.pos[0] + 1].name == "air":
                self.pos[0] += 1
        if keys[pygame.K_w]:
            # Move up
            if tick % 2 != 0:
                return
            if self.pos[1] > 0 and world[self.pos[1] - 1][self.pos[0]].name == "air":
                self.pos[1] -= 1
        if keys[pygame.K_s]:
            # Move down
            if tick % 2 != 0:
                return
            if self.pos[1] < len(world) - 1 and world[self.pos[1] + 1][self.pos[0]].name == "air":
                self.pos[1] += 1

        if keys[pygame.K_LEFT]:
            # Move left in the block selector
            if tick % 2 != 0:
                return
            if self.blockselector[0] == -1:
                return
            self.blockselector[0] -= 1
        if keys[pygame.K_RIGHT]:
            # Move right in the block selector
            if tick % 2 != 0:
                return
            if self.blockselector[0] == 1:
                return
            self.blockselector[0] += 1
        if keys[pygame.K_UP]:
            # Move up in the block selector
            if tick % 2 != 0:
                return
            if self.blockselector[1] == -1:
                return
            self.blockselector[1] -= 1
        if keys[pygame.K_DOWN]:
            # Move down in the block selector
            if tick % 2 != 0:
                return
            if self.blockselector[1] == 1:
                return
            self.blockselector[1] += 1
        if keys[pygame.K_SPACE]:
            # Place a block
            added_up = [self.pos[1] + self.blockselector[1], self.pos[0] + self.blockselector[0]]
            if added_up[0] >= 0 and added_up[1] >= 0 and added_up[0] < len(world) and added_up[1] < len(world[0]):
                world[added_up[0]][added_up[1]] = self.placeable_blocks[self.selected_block]
        if keys[pygame.K_c]:
            # Remove a block
            added_up = [self.pos[1] + self.blockselector[1], self.pos[0] + self.blockselector[0]]
            if added_up[0] >= 0 and added_up[1] >= 0 and added_up[0] < len(world) and added_up[1] < len(world[0]):
                world[added_up[0]][added_up[1]] = Block("air")

    def keydown(self, world, event, tick):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                self.selected_block -= 1
                self.selected_block %= len(self.placeable_blocks)
            if event.key == pygame.K_l:
                self.selected_block += 1
                self.selected_block %= len(self.placeable_blocks)

    @staticmethod
    def find_best_spawn(world):
        for x in range(len(world)):
            for y in range(len(world[x])):
                if world[y][x].name != "air":
                    return x, y - 1

        return 0, 0

class StructureManager:
    @staticmethod
    def load_structure(name):
        with open(resource_path(f"assets/structures/{name}.json"), "r") as f:
            data = json.load(f)

        return data
    
    @staticmethod
    def place_structure(world, structure_dict, x, y):
        # {
        # 	"keys": {
		#       "s": "oak_log",
        # 		"l": "oak_leaves",
        # 		" ": "air"
        # 	},
	    #   "dim": [5, 7],
        # 	"structure": [
        # 		" lll ",
        # 		" lll ",
        # 		"lllll",
	    #       "lllll",
        # 	    "  s  ",
		#       "  s  ",
        # 		"  s  "
	    #   ],
	    #   "placepoint": [2, 6]
        # }

        keys = structure_dict["keys"]
        dim = structure_dict["dim"]
        structure = structure_dict["structure"]
        placepoint = structure_dict["placepoint"]

        x -= placepoint[0]
        y -= placepoint[1]

        for dx in range(dim[0]):
            for dy in range(dim[1]):
                if x + dx >= len(world[0]) or y + dy >= len(world):
                    continue
                if structure[dy][dx] in keys:
                    if keys[structure[dy][dx]] == "air":
                        continue
                    world[y + dy][x + dx] = Block(keys[structure[dy][dx]])

        return world

class WorldManager:
    @staticmethod
    def save_world(name, world):
        # {
        #     "world": [[Block, Block, ...], [Block, Block, ...], ...]
        #     "wf_version": 1 (worldfile version)
        # }
        
        # Convert the world to a list of lists of strings
        world_data = [[block.__repr__() for block in column] for column in world]

        # Save the world to a JSON file
        # Variable to store ~/.mineplace/worlds or %APPDATA%/mineplace/worlds
        folder_to_save = ""
        if os.name == "nt":
            folder_to_save = os.getenv("APPDATA")
        else:
            folder_to_save = os.path.expanduser("~")
        folder_to_save = os.path.join(folder_to_save, "mineplace", "saves")

        with open(f"{folder_to_save}/{name}.json", "w") as f:
            json.dump({"world": world_data, "wf_version": 1}, f)

    @staticmethod
    def load_world(name):
        # Load the world from a JSON file
        folder_to_load = ""
        if os.name == "nt":
            folder_to_load = os.getenv("APPDATA")
        else:
            folder_to_load = os.path.expanduser("~")
        folder_to_load = os.path.join(folder_to_load, "mineplace", "saves")

        with open(f"{folder_to_load}/{name}.json", "r") as f:
            data = json.load(f)

        # Convert the list of lists of strings back to a list of lists of Blocks
        world = [[Block.from_string(block_string) for block_string in column] for column in data["world"]]
        
        datanew = {
            "world": world,
            "wf_version": data["wf_version"]
        }

        return datanew
    
    @staticmethod
    def all_world_files():
        folder_to_load = ""
        if os.name == "nt":
            folder_to_load = os.getenv("APPDATA")
        else:
            folder_to_load = os.path.expanduser("~")
        folder_to_load = os.path.join(folder_to_load, "mineplace", "saves")

        return [f.split(".")[0] for f in os.listdir(folder_to_load) if f.endswith(".json")]

    @staticmethod
    def get_world_ver(name):
        folder_to_load = ""
        if os.name == "nt":
            folder_to_load = os.getenv("APPDATA")
        else:
            folder_to_load = os.path.expanduser("~")
        folder_to_load = os.path.join(folder_to_load, "mineplace", "saves")

        with open(f"{folder_to_load}/{name}.json", "r") as f:
            data = json.load(f)

        return data["wf_version"]

    @staticmethod
    def delete_world(name):
        folder_to_load = ""
        if os.name == "nt":
            folder_to_load = os.getenv("APPDATA")
        else:
            folder_to_load = os.path.expanduser("~")
        folder_to_load = os.path.join(folder_to_load, "mineplace", "saves")

        os.remove(f"{folder_to_load}/{name}.json")

def update_world(world):
    # Update the world
    # Step 1: Randomly make dirt blocks grass (if grass blocks are everywhere except above)
    # for x in range(len(world)):
    #     for y in range(len(world[x])):
    #         if world[x][y].name == "dirt":
    #             if y < len(world[x]) - 1 and world[x][y + 1].name == "grass" and random.random() < 0.1:
    #                 # If there is a block above the dirt block, don't change it
    #                 if y > 0 and world[x][y - 1].name != "air":
    #                     continue
    #                 world[x][y] = Block("grass")
    for y in range(len(world)):
        for x in range(len(world[y])):
            if world[y][x].name == "dirt":
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if y + dy < 0 or y + dy >= len(world) or x + dx < 0 or x + dx >= len(world[y]):
                            continue
                        if world[y - 1][x].name != "air":
                            continue
                        if world[y + dy][x + dx].name == "grass" and random.random() < 0.1:
                            world[y][x] = Block("grass")
            if world[y][x].name == "grass":
                if y - 1 >= 0:
                    if world[y - 1][x].name != "air":
                        world[y][x] = Block("dirt")

    return world
