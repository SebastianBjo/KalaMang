#!/usr/bin/env python3
"""
KalaMang - main.py

Text-based fishing game loop implementing:
- Large map (configurable)
- No walking on water (need a boat to move on water)
- Cannot catch fish on land (must be on water tile to fish)
- Casting range (based on rod + skills)
- Sell fish to buy boats, rods, skills
- Named locations with shops and docks
- Multiple rods, boats, fish species, skills

Install: none required (Python 3.8+)
Usage: python main.py
"""

import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

# -------------------------
# Configuration / Balancing
# -------------------------
MAP_WIDTH = 40   # make map far larger
MAP_HEIGHT = 20
LAND_PROBABILITY = 0.6  # probability a tile is land when generating
SEED = None  # set to int for reproducible maps

START_MONEY = 100
START_ROD = "Basic Rod"
START_BOAT = None  # player starts on land, no boat

# -------------------------
# Domain Models
# -------------------------
@dataclass
class Fish:
    name: str
    base_price: int
    rarity: float  # lower is rarer (0..1), used for chance weights
    min_size: float  # for variety (in kg)
    max_size: float

@dataclass
class Rod:
    name: str
    price: int
    casting_range: int  # how many tiles away you can cast
    base_catch_chance: float  # base probability modifier (0..1)

@dataclass
class Boat:
    name: str
    price: int
    speed: int  # tiles per move (for possible future use)
    durability: int

@dataclass
class Skill:
    name: str
    price: int
    description: str
    effect: dict  # e.g. {"casting_range": 2} or {"luck": 0.05}

@dataclass
class Player:
    name: str = "Player"
    x: int = 0
    y: int = 0
    money: int = START_MONEY
    inventory: Dict[str, List[dict]] = field(default_factory=lambda: {})  # fish: list of catches
    rod: Rod = None
    boat: Boat = None
    skills: List[Skill] = field(default_factory=list)

    def add_fish(self, fish_name: str, size: float, price: int):
        self.inventory.setdefault(fish_name, []).append({"size": size, "price": price})

    def inventory_value(self):
        return sum(sum(item["price"] for item in v) for v in self.inventory.values())

# -------------------------
# Game Data
# -------------------------
FISH_TYPES = [
    Fish("Rudd", base_price=5, rarity=0.9, min_size=0.05, max_size=0.4),
    Fish("Trout", base_price=20, rarity=0.6, min_size=0.3, max_size=2.0),
    Fish("Pike", base_price=50, rarity=0.3, min_size=1.0, max_size=10.0),
    Fish("Salmon", base_price=80, rarity=0.15, min_size=2.0, max_size=12.0),
    Fish("Catfish", base_price=60, rarity=0.2, min_size=1.0, max_size=8.0),
]

RODS = {
    "Basic Rod": Rod("Basic Rod", price=0, casting_range=2, base_catch_chance=0.5),
    "Long Rod": Rod("Long Rod", price=120, casting_range=5, base_catch_chance=0.6),
    "Pro Rod": Rod("Pro Rod", price=350, casting_range=8, base_catch_chance=0.72),
}

BOATS = {
    "Rowboat": Boat("Rowboat", price=200, speed=1, durability=100),
    "Motorboat": Boat("Motorboat", price=800, speed=2, durability=300),
}

SKILLS = {
    "Casting Mastery": Skill("Casting Mastery", price=150, description="Increase casting range by 2.", effect={"casting_range": 2}),
    "Lucky Hook": Skill("Lucky Hook", price=200, description="Increase luck (catch chance) by 7%.", effect={"luck": 0.07}),
    "Quick Reel": Skill("Quick Reel", price=180, description="Increase reeling success by 6%.", effect={"reel": 0.06}),
}

# -------------------------
# Map & Location Generation
# -------------------------
class Tile:
    def __init__(self, is_land: bool):
        self.is_land = is_land
        self.name = None  # optional named location (town, dock, etc.)

class WorldMap:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT, seed=None):
        if seed is not None:
            random.seed(seed)
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.locations = {}  # name -> (x,y)
        self.generate()

    def generate(self):
        # Create simple island/continent layout: random noise smoothed by cellular automata-like pass
        for y in range(self.height):
            for x in range(self.width):
                is_land = random.random() < LAND_PROBABILITY
                self.grid[y][x] = Tile(is_land=is_land)

        # Smooth a few iterations so water/land clumps
        for _ in range(3):
            new = [[None for _ in range(self.width)] for _ in range(self.height)]
            for y in range(self.height):
                for x in range(self.width):
                    land_neighbors = 0
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.height and 0 <= nx < self.width:
                                if self.grid[ny][nx].is_land:
                                    land_neighbors += 1
                    new[y][x] = Tile(is_land=(land_neighbors >= 5))
            self.grid = new

        # Place a few named locations (towns/docks) on land adjacent to water
        potential_spots = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].is_land:
                    # check if adjacent to water (dock candidate)
                    adjacent_water = False
                    for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.height and 0 <= nx < self.width:
                            if not self.grid[ny][nx].is_land:
                                adjacent_water = True
                    if adjacent_water:
                        potential_spots.append((x,y))
        random.shuffle(potential_spots)
        names = ["Vagle Harbor", "Old Pier", "Seabreeze Town", "Pärnu Dock", "Northwatch"]
        for i, name in enumerate(names):
            if i < len(potential_spots):
                x,y = potential_spots[i]
                self.grid[y][x].name = name
                self.locations[name] = (x,y)

    def in_bounds(self, x,y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_land(self, x,y):
        if not self.in_bounds(x,y): return False
        return self.grid[y][x].is_land

    def tile_name(self, x,y):
        if not self.in_bounds(x,y): return None
        return self.grid[y][x].name

    def pretty_map(self, player: Player):
        # Show small viewport around player for convenience
        view = 10
        left = max(0, player.x - view)
        right = min(self.width-1, player.x + view)
        top = max(0, player.y - view)
        bottom = min(self.height-1, player.y + view)
        rows = []
        for y in range(top, bottom+1):
            line = ""
            for x in range(left, right+1):
                if x == player.x and y == player.y:
                    line += "P"
                elif self.grid[y][x].name:
                    line += "L"  # location
                elif self.grid[y][x].is_land:
                    line += "."
                else:
                    line += "~"
            rows.append(line)
        return "\n".join(rows)

# -------------------------
# Utility functions
# -------------------------
def weighted_choice(fish_types: List[Fish], luck=0.0):
    # weight by rarity (higher rarity => higher weight), adjust with luck
    weights = []
    for f in fish_types:
        base = f.rarity
        # luck slightly increases chance of rare fish (reduce weight smoothing)
        weight = max(0.01, base + luck * (1 - base))
        weights.append(weight)
    total = sum(weights)
    r = random.random() * total
    upto = 0
    for f, w in zip(fish_types, weights):
        if upto + w >= r:
            return f
        upto += w
    return fish_types[-1]

def clamp(n, a, b):
    return max(a, min(b, n))

# -------------------------
# Game logic
# -------------------------
class Game:
    def __init__(self):
        if SEED is not None:
            self.world = WorldMap(seed=SEED)
        else:
            self.world = WorldMap()
        # place player at a named location or random land tile
        start_x, start_y = self.find_starting_land()
        self.player = Player(x=start_x, y=start_y)
        self.player.rod = RODS[START_ROD]
        self.player.boat = START_BOAT
        self.running = True

    def find_starting_land(self):
        # try to place at a named location or any land tile
        if self.world.locations:
            name = random.choice(list(self.world.locations.keys()))
            x,y = self.world.locations[name]
            return x, y
        for y in range(self.world.height):
            for x in range(self.world.width):
                if self.world.is_land(x,y):
                    return x,y
        return 0,0

    def can_move_to(self, x, y):
        # cannot move outside map
        if not self.world.in_bounds(x,y):
            return False, "Out of bounds."
        tile_land = self.world.is_land(x,y)
        if tile_land:
            # always can move to land tiles on foot
            return True, None
        else:
            # water tile: can move only if in a boat
            if self.player.boat is None:
                return False, "You can't walk on water. Buy a boat to move on water tiles."
            return True, None

    def move(self, dx, dy):
        nx = self.player.x + dx
        ny = self.player.y + dy
        ok, reason = self.can_move_to(nx, ny)
        if not ok:
            print(reason)
            return
        self.player.x = nx
        self.player.y = ny
        tile_name = self.world.tile_name(nx, ny)
        if tile_name:
            print(f"You arrive at {tile_name}.")
        else:
            print("You moved.")
        # if we moved onto land while having a boat, boat stays but you're on the shore (no special handling here)

    def look(self):
        x,y = self.player.x, self.player.y
        if self.world.is_land(x,y):
            print(f"You are on land at ({x},{y}).")
            name = self.world.tile_name(x,y)
            if name:
                print(f"This place is called {name}. You can access a shop here.")
        else:
            print(f"You are on water at ({x},{y}). Cast away!")
        # show adjacent tiles
        print("Surroundings (N,S,E,W):")
        for dname, (dx,dy) in [("N",(0,-1)),("S",(0,1)),("E",(1,0)),("W",(-1,0))]:
            nx, ny = x+dx, y+dy
            if self.world.in_bounds(nx,ny):
                t = "Land" if self.world.is_land(nx,ny) else "Water"
                tn = self.world.tile_name(nx,ny)
                extra = f" - {tn}" if tn else ""
                print(f"  {dname}: {t} {extra}")
            else:
                print(f"  {dname}: Out of bounds")

    def get_casting_range(self):
        # calculate casting range from rod + skills
        base = self.player.rod.casting_range
        extra = 0
        for s in self.player.skills:
            extra += s.effect.get("casting_range", 0)
        return base + extra

    def get_luck(self):
        # positive modifier to fish rarity/catch chance
        luck = 0.0
        for s in self.player.skills:
            luck += s.effect.get("luck", 0.0)
        return luck

    def fish(self):
        x,y = self.player.x, self.player.y
        if self.world.is_land(x,y):
            print("You can't catch fish from land. You must be on a water tile (in a boat) to fish.")
            return

        # compute allowed casting positions within casting_range
        rng = self.get_casting_range()
        # list of water tiles within range
        water_tiles = []
        for dy in range(-rng, rng+1):
            for dx in range(-rng, rng+1):
                nx, ny = x+dx, y+dy
                if not self.world.in_bounds(nx,ny):
                    continue
                if not self.world.is_land(nx,ny):
                    # distance check (Manhattan or Euclidean?) Use Euclidean
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist <= rng:
                        water_tiles.append((nx,ny,dist))
        if not water_tiles:
            print("No water within casting range.")
            return

        # simulate cast: choose a tile, then fish type and success
        chosen = random.choice(water_tiles)
        dist = chosen[2]

        # catch chance depends on rod, rod.base_catch_chance improved by nearer distance and luck
        rod = self.player.rod
        base = rod.base_catch_chance
        # reduce chance slightly with distance (farther -> harder)
        distance_penalty = 0.03 * (dist)  # small penalty per tile
        luck = self.get_luck()
        final_chance = clamp(base - distance_penalty + luck, 0.01, 0.95)

        # reel / skill could improve (we'll roll a reeling success)
        success_roll = random.random()
        if success_roll > final_chance:
            print("A fish bit... but you failed to reel it in. Try again.")
            return

        # select fish weighted by rarity and luck (luck makes rarer fish slightly more likely)
        fish = weighted_choice(FISH_TYPES, luck=luck)
        size = round(random.uniform(fish.min_size, fish.max_size), 2)
        # price can scale with size
        price = int(fish.base_price * (1 + (size / (fish.max_size + 0.01)) * 1.5))
        self.player.add_fish(fish.name, size, price)
        print(f"You caught a {fish.name} ({size} kg) worth {price} coins!")

    def sell(self):
        if not self.player.inventory:
            print("You have no fish to sell.")
            return
        total = 0
        print("Selling all fish in inventory:")
        for name, items in list(self.player.inventory.items()):
            for it in items:
                print(f"  Sold {name} ({it['size']} kg) for {it['price']} coins.")
                total += it['price']
        self.player.inventory.clear()
        self.player.money += total
        print(f"You earned {total} coins. You now have {self.player.money} coins.")

    def open_shop(self):
        x,y = self.player.x, self.player.y
        name = self.world.tile_name(x,y)
        if not name:
            print("No shop here. Shops are located in named harbor locations.")
            return
        print(f"Welcome to {name} Shop! What would you like to see?")
        print("Items available: boats, rods, skills.")
        print("Type 'buy <category> <item>' (e.g. buy rod Long Rod)")

    def buy(self, category, item_name):
        category = category.lower()
        if category == "rod":
            if item_name not in RODS:
                print("Unknown rod.")
                return
            rod = RODS[item_name]
            if self.player.money < rod.price:
                print("Not enough money.")
                return
            self.player.money -= rod.price
            self.player.rod = rod
            print(f"You bought and equipped {rod.name}.")
        elif category == "boat":
            if item_name not in BOATS:
                print("Unknown boat.")
                return
            boat = BOATS[item_name]
            if self.player.money < boat.price:
                print("Not enough money.")
                return
            self.player.money -= boat.price
            self.player.boat = boat
            # when buying a boat, attempt to place player onto adjacent water tile if available
            if self.world.is_land(self.player.x, self.player.y):
                # find adjacent water to put boat
                placed = False
                for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx,ny = self.player.x+dx, self.player.y+dy
                    if self.world.in_bounds(nx,ny) and not self.world.is_land(nx,ny):
                        self.player.x, self.player.y = nx, ny
                        placed = True
                        break
                if not placed:
                    print("You bought the boat, but couldn't place it at this location. Move to a dock to launch later.")
                else:
                    print("You launched your new boat into the water!")
            print(f"You bought {boat.name}.")
        elif category == "skill":
            if item_name not in SKILLS:
                print("Unknown skill.")
                return
            skill = SKILLS[item_name]
            # check already learned
            if any(s.name == skill.name for s in self.player.skills):
                print("You already have that skill.")
                return
            if self.player.money < skill.price:
                print("Not enough money.")
                return
            self.player.money -= skill.price
            self.player.skills.append(skill)
            print(f"You learned the skill: {skill.name} - {skill.description}")
        else:
            print("Unknown category. Use rod, boat, or skill.")

    def show_shop_list(self):
        print("Rods:")
        for k,v in RODS.items():
            print(f"  {k}: Price {v.price}, Range {v.casting_range}, Catch {v.base_catch_chance*100:.0f}%")
        print("Boats:")
        for k,v in BOATS.items():
            print(f"  {k}: Price {v.price}, Speed {v.speed}")
        print("Skills:")
        for k,v in SKILLS.items():
            print(f"  {k}: Price {v.price} - {v.description}")

    def status(self):
        p = self.player
        print(f"Location: ({p.x},{p.y}) - {'Land' if self.world.is_land(p.x,p.y) else 'Water'}")
        tname = self.world.tile_name(p.x, p.y)
        if tname:
            print(f"At location: {tname}")
        print(f"Money: {p.money}")
        print(f"Equipped rod: {p.rod.name} (Range: {p.rod.casting_range})")
        print(f"Boat: {p.boat.name if p.boat else 'None'}")
        print("Skills:")
        if p.skills:
            for s in p.skills:
                print(f"  {s.name} - {s.description}")
        else:
            print("  None")
        print("Fish inventory:")
        if p.inventory:
            for name, items in p.inventory.items():
                for it in items:
                    print(f"  {name} ({it['size']} kg) - sell value {it['price']}")
        else:
            print("  Empty")

    def help(self):
        print("""
Commands:
  move n/s/e/w  - move north/south/east/west (can't walk on water)
  map            - show local map around you
  look           - describe your current tile and neighbors
  fish           - attempt to fish (must be on water)
  sell           - sell all fish in inventory
  shop           - open shop menu if at a harbor/location
  shoplist       - show all items available in shops
  buy <cat> <name> - buy an item. cat = rod|boat|skill  (e.g. buy rod Long Rod)
  equip rod <name> - equip a rod you bought (instant if bought)
  status         - show player status and inventory
  help           - show this message
  quit           - exit game
""")

    def equip(self, subcat, name):
        if subcat.lower() == "rod":
            if name not in RODS:
                print("Unknown rod.")
                return
            self.player.rod = RODS[name]
            print(f"Equipped rod: {name}")
        else:
            print("You can only equip rods currently.")

    def run_command(self, cmd):
        if not cmd:
            return
        parts = cmd.strip().split()
        if not parts:
            return
        op = parts[0].lower()
        if op == "move" and len(parts) >= 2:
            dir = parts[1].lower()
            deltas = {"n": (0,-1), "s": (0,1), "e": (1,0), "w": (-1,0),
                      "north":(0,-1),"south":(0,1),"east":(1,0),"west":(-1,0)}
            if dir in deltas:
                dx,dy = deltas[dir]
                self.move(dx, dy)
            else:
                print("Unknown direction. Use n/s/e/w.")
        elif op == "map":
            print(self.world.pretty_map(self.player))
        elif op == "look":
            self.look()
        elif op == "fish":
            self.fish()
        elif op == "sell":
            self.sell()
        elif op == "shop":
            self.open_shop()
        elif op == "shoplist":
            self.show_shop_list()
        elif op == "buy" and len(parts) >= 3:
            category = parts[1]
            item_name = " ".join(parts[2:])
            # require being at a named location to buy boats/skills? keep consistent: must be at a named location
            if self.world.tile_name(self.player.x, self.player.y) is None and category in ("boat","skill"):
                print("You can only buy boats or skills at a harbor/shop location. Move to a named location.")
                return
            self.buy(category, item_name)
        elif op == "equip" and len(parts) >= 3:
            self.equip(parts[1], " ".join(parts[2:]))
        elif op == "status":
            self.status()
        elif op == "help":
            self.help()
        elif op == "quit":
            print("Thanks for playing KalaMang!")
            self.running = False
        else:
            print("Unknown command. Type 'help' for commands.")

    def game_loop(self):
        print("Welcome to KalaMang! Type 'help' for a list of commands.")
        # show starting info
        self.status()
        while self.running:
            try:
                cmd = input("\n> ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            self.run_command(cmd)

# -------------------------
# Run game
# -------------------------
def main():
    print("Starting KalaMang...")
    g = Game()
    g.game_loop()

if __name__ == "__main__":
    main()
