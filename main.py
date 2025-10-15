import random
import sys
import time

# -------------------------------
# CONFIG
# -------------------------------
MAP_WIDTH = 25
MAP_HEIGHT = 15
CAST_RANGE = 3

# Water area (center lake)
water_tiles = [(x, y) for x in range(8, 18) for y in range(5, 10)]

# -------------------------------
# PLAYER DATA
# -------------------------------
player = {
    "x": 3,
    "y": 7,
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
    {"name": "Perch", "value": 10, "chance": 0.3},
    {"name": "Trout", "value": 25, "chance": 0.15},
    {"name": "Pike", "value": 50, "chance": 0.05}
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
    for fish in FISH_TYPES:
        bonus = 0.02 * player["rod_level"]
        if "skill_luck" in player["skills"]:
            bonus += 0.03
        if roll < fish["chance"] + bonus:
            caught = fish
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

while True:
    cmd = input("\n> ").strip().lower()

    if cmd in ["w", "a", "s", "d"]:
        if cmd == "w": move(0, -1)
        elif cmd == "s": move(0, 1)
        elif cmd == "a": move(-1, 0)
        elif cmd == "d": move(1, 0)
        show_map()

    elif cmd == "fish":
        fish()

    elif cmd == "sell":
        sell_fish()

    elif cmd == "shop":
        shop()

    elif cmd == "map":
        show_map()

    elif cmd == "stats":
        stats()

    elif cmd == "help":
        help_menu()

    elif cmd == "quit":
        print("👋 Thanks for playing KalaMang!")
        sys.exit()

    else:
        print("❓ Unknown command. Type 'help' for commands.")
