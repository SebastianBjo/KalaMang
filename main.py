class Shop:
    def __init__(self):
        self.currency = 1000  # Starting currency
        self.items = {'Rod': 300, 'Bait': 50, 'Boat upgrade': 500}

    def buy_item(self, item):
        if item in self.items and self.currency >= self.items[item]:
            self.currency -= self.items[item]
            print(f'Bought {item}!')
        else:
            print('Not enough currency or item not available.')

class Player:
    def __init__(self):
        self.experience = 0
        self.level = 1

    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= self.level * 100:  # Level up every 100 XP
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience = 0
        print(f'Leveled up to level {self.level}!')

class Biome:
    def __init__(self, name, unique_fish):
        self.name = name
        self.unique_fish = unique_fish

class Boat:
    def __init__(self):
        self.speed = 10
        self.upgrade_cost = 400

    def upgrade(self):
        self.speed += 5
        self.upgrade_cost += 200
        print('Boat upgraded! Speed is now:', self.speed)

# Example instances
shop = Shop()
player = Player()
river = Biome('River', ['Trout', 'Catfish'])
sea = Biome('Sea', ['Shark', 'Tuna'])
boat = Boat()  
