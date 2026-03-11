import random
import sys
import time

# -------------------------------
# CONFIG
# -------------------------------
MAP_WIDTH = 40
MAP_HEIGHT = 20
CAST_RANGE = 3

# Water area (lake)
water_tiles = [(x, y) for x in range(10, 30) for y in range(7, 15)]

# -------------------------------
# PLAYER DATA
# -------------------------------
player = {
    "x": 5,
    "y": 5,
    "money": 100,
    "inventory": [],
    "rod_level": 1,
    "boat": False,
    "skills": []
}

# -------------------------------
# FISH TYPES
# -------------------------------
FISH_TYPES = [
    {"name": "Minnow", "value": 5, "chance": 0.5},
    {"name": "Perch", "value": 15, "chance": 0.3},
    {"name": "Trout", "value": 30, "chance": 0.15},
    {"name": "Pike", "value": 60, "chance": 0.05}
]

# -------------------------------
# SHOP DATA
# -------------------------------
SHOP_ITEMS = {
    "rod_upgrade": {"price": 100, "desc": "Increases your chance to catch better fish"},
    "boat": {"price": 200, "desc": "Lets you travel on water"},
    "skill_luck": {"price": 150, "desc": "Adds a small bonus to catch rare fish"}
}

# -------------------------------
# FUNCTIONS
# -------------------------------
def show_map():
    for y in range(MAP_HEIGHT):
        row = ""
        for x in range(MAP_WIDTH):
            if (x, y) == (player["x"], player["y"]):
                row += "🧍"
            elif (x, y) in water_tiles:
                row += "🌊"
            else:
                row += "🌲"
        print(row)
    print(f"\n💰 {player['money']} | 🎣 Rod Lv.{player['rod_level']} | 🚤 {'Yes' if player['boat'] else 'No'} | 🎒 {len(player['inventory'])} fish\n")

def move(dx, dy):
    new_x = player["x"] + dx
    new_y = player["y"] + dy
    if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
        if (new_x, new_y) in water_tiles and not player["boat"]:
            print("🚫 You can’t walk on water without a boat!")
        else:
            player["x"], player["y"] = new_x, new_y
    else:
        print("⛔ Edge of the world!")

def near_water():
    for wx, wy in water_tiles:
        if abs(wx - player["x"]) <= CAST_RANGE and abs(wy - player["y"]) <= CAST_RANGE:
            return True
    return False

def fish():
    if not near_water():
        print("🎣 You’re too far from water to cast your line.")
        return

    print("🎣 Casting line...")
    time.sleep(1)

    roll = random.random()
    caught = None
    for f in FISH_TYPES:
        bonus = 0.02 * player["rod_level"]
        if "skill_luck" in player["skills"]:
            bonus += 0.03
        if roll < f["chance"] + bonus:
            caught = f
            break

    if caught:
        print(f"🐟 You caught a {caught['name']} worth ${caught['value']}!")
        player["inventory"].append(caught)
    else:
        print("💨 Nothing bit this time.")

def sell_fish():
    if not player["inventory"]:
        print("🪣 You have no fish to sell.")
        return

    total = sum(f["value"] for f in player["inventory"])
    player["money"] += total
    player["inventory"].clear()
    print(f"💰 You sold your fish for ${total}!")

def shop():
    print("\n🏪 Shop:")
    for name, item in SHOP_ITEMS.items():
        print(f" - {name} (${item['price']}): {item['desc']}")
    choice = input("\nBuy what? (type name or 'exit'): ").strip().lower()
    if choice == "exit":
        return
    if choice not in SHOP_ITEMS:
        print("❌ Not sold here.")
        return

    item = SHOP_ITEMS[choice]
    if player["money"] < item["price"]:
        print("💸 You can’t afford that.")
        return

    player["money"] -= item["price"]

    if choice == "rod_upgrade":
        player["rod_level"] += 1
        print("🎣 Rod upgraded!")
    elif choice == "boat":
        player["boat"] = True
        print("🚤 You bought a boat!")
    elif choice == "skill_luck":
        player["skills"].append("skill_luck")
        print("🍀 You feel luckier already!")

def help_menu():
    print("""
Commands:
  w/a/s/d - Move
  fish    - Fish near water
  sell    - Sell all fish
  shop    - Visit shop
  map     - Show map
  stats   - Show stats
  help    - Show this help
  quit    - Exit game
""")

def stats():
    print(f"""
📊 STATS:
Money: ${player['money']}
Rod Level: {player['rod_level']}
Boat: {player['boat']}
Fish in Inventory: {len(player['inventory'])}
Skills: {', '.join(player['skills']) if player['skills'] else 'None'}
""")

# -------------------------------
# GAME LOOP
# -------------------------------
print("🎣 Welcome to KalaMang!")
help_menu()
show_map()

while True:
    cmd = input("\n> ").strip().lower()
    if cmd in ["w", "a", "s", "d"]:
        if cmd == "w": move(0, -1)
        elif cmd == "s": move(0, 1)
        elif cmd == "a": move(-1, 0)
        elif cmd == "d": move(1, 0)
        show_map()
    elif cmd == "fish": fish()
    elif cmd == "sell": sell_fish()
    elif cmd == "shop": shop()
    elif cmd == "map": show_map()
    elif cmd == "stats": stats()
    elif cmd == "help": help_menu()
    elif cmd == "quit":
        print("👋 Thanks for playing KalaMang!")
        sys.exit()
    else:
        print("❓ Unknown command. Type 'help' for commands.")
# European Forest Fishing Adventure - Complete Feature List

## 🎮 Core Gameplay Features

### Fishing System
- **Timing-based Hook Setting**: Press SPACE when the red marker is in the green zone
- **Variable Difficulty**: Each fish species has different difficulty levels (1-10)
- **Fish Escape Timer**: Limited time to set the hook before fish escapes
- **Visual Feedback**: Hook bar changes color when set, target zone flashes
- **Real-time Timer**: Shows remaining time to catch the fish

### Fish Species (20 Total)
**European Fish:**
- European Perch (Cardboard) - Common freshwater fish
- Northern Pike (Bronze) - Aggressive predator
- European Carp (Silver) - Large bottom-feeder
- Atlantic Salmon (Gold) - Prized game fish

**North American Fish:**
- Rainbow Trout (Silver) - Beautiful game fish
- Largemouth Bass (Gold) - Popular bass species
- Smallmouth Bass (Silver) - Feisty fighter
- Muskellunge (Diamond) - "Fish of 10,000 casts"

**Asian Fish:**
- Koi Carp (Bronze) - Ornamental carp
- Asian Arowana (Trophy) - Rare and expensive
- Giant Mekong Catfish (Record) - Largest freshwater fish

**African Fish:**
- Nile Perch (Diamond) - Massive predator
- Tigerfish (Gold) - Ferocious with sharp teeth

**South American Fish:**
- Peacock Bass (Silver) - Colorful Amazon fish
- Pirarucu (Trophy) - Prehistoric-looking giant

**Ocean Fish:**
- Mahi Mahi (Diamond) - Fast tropical predator
- Blue Marlin (Trophy) - Ultimate trophy fish
- Yellowfin Tuna (Gold) - Powerful ocean predator
- Swordfish (Diamond) - Deep-sea predator

**Mythical/Record Fish:**
- Legendary Kraken (Record) - Mythical sea creature
- Ancient Coelacanth (Record) - Living fossil

## 🏆 Rarity System (Inspired by The Hunter: Call of the Wild)

### Rarity Levels
1. **Cardboard** (Gray) - Common, easy to catch
2. **Bronze** (Brown) - Uncommon, moderate difficulty
3. **Silver** (Silver) - Rare, challenging
4. **Gold** (Gold) - Very rare, difficult
5. **Diamond** (Cyan) - Extremely rare, very difficult
6. **Trophy** (Orange) - Legendary, extremely difficult
7. **Record Fish** (Purple) - Mythical creatures, ultimate challenge

### Weight System
- Each fish has realistic weight ranges
- Rarity affects weight multiplier
- Record fish can weigh over 1000kg

## 🎨 Visual Effects & Graphics

### Environment
- **European Forest Background**: Dark green forest with trees
- **Water Gradient**: Realistic water appearance with depth
- **Lily Pads**: Decorative water plants
- **Tree Variety**: Randomly placed trees with trunks and foliage

### Visual Effects
- **Water Ripples**: Animated ripples when fishing
- **Fish Shadows**: Random fish shadows moving in water
- **Particle Effects**: Celebration particles when catching fish
- **Flash Effects**: Target zone flashes when hook is set
- **Semi-transparent Overlays**: During fishing minigame

### UI Elements
- **Color-coded Rarity Display**: Each rarity has distinct colors
- **Real-time Statistics**: Fish caught count and rarity breakdown
- **Catch Messages**: Temporary display of caught fish info
- **Progress Indicators**: Quest completion status

## 🎵 Sound System

### Sound Effects
- **Splash Sound**: When starting to fish
- **Catch Sound**: When successfully catching a fish
- **Escape Sound**: When fish escapes
- **Menu Selection**: Navigation sounds

## 📊 Game Systems

### Inventory System
- **Fish Collection**: Track all caught fish
- **Rarity Sorting**: Fish sorted by rarity (highest first)
- **Detailed Information**: Species, weight, rarity, bait used
- **Color-coded Display**: Each rarity has distinct colors

### Fish Glossary (Pokedex-style)
- **Complete Catalog**: All available fish species
- **Detailed Information**: Location, weight range, difficulty, bait
- **Rarity-based Sorting**: Highest rarity first
- **Color-coded Entries**: Visual rarity indicators

### Quest System
- **Progressive Challenges**: Multiple quest types
- **Real-time Tracking**: Live progress updates
- **Completion Indicators**: Green text for completed quests
- **Quest Types**:
  - Catch your first fish
  - Catch 5 different species
  - Catch 10 different species
  - Catch a trophy fish
  - Catch a record fish
  - Catch 50 total fish

### Bait System
- **Multiple Bait Types**: Worm, Minnow, Fly, Spoon, etc.
- **Fish Preferences**: Different fish prefer different baits
- **Current Bait Display**: Shows active bait in UI

## 🎮 Controls

### Main Game
- **WASD/Arrow Keys**: Move player character
- **SPACE**: Start fishing
- **I**: Open inventory
- **G**: Open fish glossary
- **Q**: Open quests
- **ESC**: Return to menu/pause

### Menu Navigation
- **UP/DOWN**: Navigate menu options
- **ENTER**: Select menu option
- **ESC**: Return to previous menu

### Fishing Minigame
- **SPACE**: Set the hook (timing-based)
- **ESC**: Cancel fishing

## 🏞️ Environment Features

### Forest Setting
- **European Theme**: Authentic forest atmosphere
- **Water Body**: Large lake/river for fishing
- **Explorable Area**: Walk around the forest
- **Dynamic Elements**: Fish shadows, water ripples

### Player Character
- **Simple Design**: Blue rectangle with fishing rod
- **Smooth Movement**: Responsive controls
- **Boundary Limits**: Cannot walk off screen

## 📈 Statistics & Progress

### Tracking Systems
- **Total Fish Caught**: Running count
- **Rarity Breakdown**: Count by rarity level
- **Species Collection**: Unique species caught
- **Quest Progress**: Real-time quest completion

### Data Persistence
- **Session-based**: Progress maintained during play session
- **Fish Details**: Complete catch information stored
- **Quest State**: Current quest progress tracked

## 🎯 Game Balance

### Difficulty Progression
- **Easy Start**: Common fish for beginners
- **Gradual Challenge**: Increasing difficulty with rarity
- **Skill-based**: Timing and reflexes required
- **Random Elements**: Fish selection and timing variations

### Catch Rates
- **30% Success Rate**: Realistic fishing experience
- **Rarity Influence**: Higher rarity = lower catch chance
- **Bait Effectiveness**: Different baits affect success

## 🔧 Technical Features

### Performance
- **60 FPS**: Smooth gameplay
- **Efficient Rendering**: Optimized visual effects
- **Memory Management**: Clean object lifecycle

### Code Quality
- **Modular Design**: Separate classes for different systems
- **Extensible**: Easy to add new fish species
- **Well-documented**: Clear code structure

## 🚀 Future Enhancement Potential

### Possible Additions
- **Save/Load System**: Persistent progress
- **More Locations**: Different fishing environments
- **Equipment Upgrades**: Better rods, lures, etc.
- **Weather System**: Dynamic fishing conditions
- **Time of Day**: Different fish active at different times
- **Multiplayer**: Competitive fishing
- **Achievements**: Additional goals and rewards
- **Soundtrack**: Background music
- **Animations**: More detailed character and fish animations
