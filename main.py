import pygame
import sys
import random
import math
import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (34, 139, 34)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
DIAMOND = (185, 242, 255)

# Game states
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    FISHING = "fishing"
    FISH_CAUGHT = "fish_caught"
    INVENTORY = "inventory"
    GLOSSARY = "glossary"
    QUEST = "quest"
    PAUSED = "paused"

# Rarity levels
class Rarity(Enum):
    CARDBOARD = "Cardboard"
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    DIAMOND = "Diamond"
    TROPHY = "Trophy"
    RECORD = "Record Fish"

# Reward types
class RewardType(Enum):
    BAIT = "bait"
    ROD = "rod"
    LOCATION = "location"
    COSMETIC = "cosmetic"

@dataclass
class Reward:
    type: RewardType
    name: str
    description: str
    value: str

@dataclass
class Quest:
    id: str
    name: str
    description: str
    target: int
    current: int
    reward: Reward
    completed: bool

# Fish species data
FISH_SPECIES = {
    "European Perch": {
        "weight_range": (0.2, 2.0),
        "length_range": (15, 40),
        "location": "Europe",
        "rarity": Rarity.CARDBOARD,
        "bait": ["Worm", "Minnow"],
        "difficulty": 1,
        "description": "A common freshwater fish found in European lakes and rivers."
    },
    "Northern Pike": {
        "weight_range": (1.0, 15.0),
        "length_range": (30, 120),
        "location": "Europe",
        "rarity": Rarity.BRONZE,
        "bait": ["Large Minnow", "Spoon"],
        "difficulty": 3,
        "description": "A predatory fish known for its aggressive strikes."
    },
    "European Carp": {
        "weight_range": (2.0, 25.0),
        "length_range": (40, 100),
        "location": "Europe",
        "rarity": Rarity.SILVER,
        "bait": ["Corn", "Bread"],
        "difficulty": 2,
        "description": "A large bottom-feeding fish popular in European waters."
    },
    "Atlantic Salmon": {
        "weight_range": (3.0, 20.0),
        "length_range": (50, 150),
        "location": "Europe",
        "rarity": Rarity.GOLD,
        "bait": ["Fly", "Spoon"],
        "difficulty": 6,
        "description": "A prized game fish that migrates from ocean to rivers."
    },
    "Rainbow Trout": {
        "weight_range": (0.5, 5.0),
        "length_range": (20, 60),
        "location": "North America",
        "rarity": Rarity.SILVER,
        "bait": ["Fly", "Worm"],
        "difficulty": 4,
        "description": "A beautiful fish prized by anglers for its fighting spirit."
    },
    "Largemouth Bass": {
        "weight_range": (0.5, 8.0),
        "length_range": (25, 75),
        "location": "North America",
        "rarity": Rarity.GOLD,
        "bait": ["Plastic Worm", "Crankbait"],
        "difficulty": 5,
        "description": "A popular game fish known for its powerful strikes."
    },
    "Nile Perch": {
        "weight_range": (5.0, 100.0),
        "length_range": (60, 200),
        "location": "Africa",
        "rarity": Rarity.DIAMOND,
        "bait": ["Large Fish", "Artificial Lure"],
        "difficulty": 7,
        "description": "A massive predator that can grow over 200kg."
    },
    "Peacock Bass": {
        "weight_range": (1.0, 12.0),
        "length_range": (30, 80),
        "location": "South America",
        "rarity": Rarity.SILVER,
        "bait": ["Topwater Lure", "Live Bait"],
        "difficulty": 5,
        "description": "A colorful and aggressive game fish from the Amazon."
    },
    "Blue Marlin": {
        "weight_range": (100.0, 500.0),
        "length_range": (200, 400),
        "location": "Deep Ocean",
        "rarity": Rarity.TROPHY,
        "bait": ["Large Tuna", "Artificial Lure"],
        "difficulty": 9,
        "description": "The ultimate trophy fish, a true test of skill and patience."
    },
    "Legendary Kraken": {
        "weight_range": (1000.0, 2000.0),
        "length_range": (500, 800),
        "location": "Abyssal Depths",
        "rarity": Rarity.RECORD,
        "bait": ["Mythical Bait"],
        "difficulty": 10,
        "description": "A mythical sea creature that few have ever seen."
    }
}

@dataclass
class Fish:
    species: str
    weight: float
    length: float
    rarity: Rarity
    difficulty: int
    bait_used: str
    catch_time: str
    personal_record: bool = False

class Sprite:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.animation_frame = 0
        self.animation_timer = 0
        
    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:  # Change frame every 10 ticks
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

class HumanCharacter(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60, BROWN)
        self.speed = 5
        self.facing_right = True
        self.is_casting = False
        self.cast_timer = 0
        self.fishing_line = None
        self.cast_target = None
        self.cast_progress = 0
        self.animation_state = "idle"  # idle, walking, casting, fishing
        self.animation_timer = 0
        self.arm_swing = 0
        
    def move(self, keys):
        was_moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.facing_right = False
            was_moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.facing_right = True
            was_moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
            was_moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            was_moving = True
            
        # Keep player on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        
        # Update animation state
        if was_moving:
            self.animation_state = "walking"
        else:
            self.animation_state = "idle"
            
        self.update_animation()
        
    def start_casting(self, target_x, target_y):
        self.is_casting = True
        self.cast_timer = 0
        self.cast_target = (target_x, target_y)
        self.cast_progress = 0
        self.animation_state = "casting"
        
    def update_casting(self):
        if self.is_casting:
            self.cast_timer += 1
            self.cast_progress = min(1.0, self.cast_timer / 60)  # 1 second cast animation
            
            if self.cast_timer >= 60:  # 1 second cast animation
                self.is_casting = False
                self.animation_state = "fishing"
                return True
        return False
        
    def stop_fishing(self):
        self.is_casting = False
        self.cast_target = None
        self.cast_progress = 0
        self.animation_state = "idle"
    
    def draw(self, screen):
        # Update animation timers
        self.animation_timer += 1
        if self.animation_state == "walking":
            self.arm_swing = math.sin(self.animation_timer * 0.3) * 5
        else:
            self.arm_swing = 0
            
        # Draw human character with enhanced animations
        # Head with breathing animation
        head_color = (255, 218, 185)  # Skin tone
        head_y_offset = math.sin(self.animation_timer * 0.1) * 1
        pygame.draw.circle(screen, head_color, (self.x + self.width//2, self.y + 10 + head_y_offset), 12)
        
        # Eyes with blinking animation
        if self.animation_timer % 120 < 10:  # Blink every 2 seconds
            eye_color = (0, 0, 0)
        else:
            eye_color = (255, 255, 255)
        pygame.draw.circle(screen, eye_color, (self.x + self.width//2 - 4, self.y + 8), 2)
        pygame.draw.circle(screen, eye_color, (self.x + self.width//2 + 4, self.y + 8), 2)
        
        # Body with breathing animation
        body_color = (70, 130, 180)  # Blue shirt
        body_scale = 1 + math.sin(self.animation_timer * 0.1) * 0.05
        body_width = int(24 * body_scale)
        body_height = int(30 * body_scale)
        pygame.draw.rect(screen, body_color, (self.x + 8, self.y + 20, body_width, body_height))
        
        # Arms with walking/swinging animation
        arm_color = (255, 218, 185)
        if self.is_casting:
            # Casting animation - arms up and back
            cast_angle = self.cast_progress * math.pi
            arm_offset = int(10 * math.sin(cast_angle))
            
            # Left arm
            pygame.draw.rect(screen, arm_color, (self.x + 5 - arm_offset, self.y + 25, 8, 20))
            # Right arm
            pygame.draw.rect(screen, arm_color, (self.x + 27 + arm_offset, self.y + 25, 8, 20))
            
            # Fishing rod with casting animation
            rod_start = (self.x + self.width//2, self.y + 15)
            rod_angle = -math.pi/4 + (cast_angle * 0.5)  # Start back, swing forward
            rod_length = 40 + int(20 * self.cast_progress)
            rod_end_x = rod_start[0] + math.cos(rod_angle) * rod_length
            rod_end_y = rod_start[1] + math.sin(rod_angle) * rod_length
            
            pygame.draw.line(screen, BROWN, rod_start, (rod_end_x, rod_end_y), 3)
            
            # Fishing line with casting animation
            if self.cast_target and self.cast_progress > 0.5:
                line_progress = (self.cast_progress - 0.5) * 2  # Last 50% of cast
                line_end_x = rod_end_x + (self.cast_target[0] - rod_end_x) * line_progress
                line_end_y = rod_end_y + (self.cast_target[1] - rod_end_y) * line_progress
                pygame.draw.line(screen, BLACK, (rod_end_x, rod_end_y), (line_end_x, line_end_y), 1)
                
                # Draw splash at target when line reaches
                if line_progress >= 1.0:
                    splash_radius = int(10 * (1 - (self.animation_timer % 30) / 30))
                    if splash_radius > 0:
                        pygame.draw.circle(screen, (255, 255, 255), 
                                        (int(self.cast_target[0]), int(self.cast_target[1])), splash_radius, 2)
        else:
            # Normal arms with walking animation
            left_arm_y = self.y + 30 + self.arm_swing
            right_arm_y = self.y + 30 - self.arm_swing
            pygame.draw.rect(screen, arm_color, (self.x + 5, left_arm_y, 8, 15))
            pygame.draw.rect(screen, arm_color, (self.x + 27, right_arm_y, 8, 15))
        
        # Legs with walking animation
        leg_color = (25, 25, 112)  # Dark blue pants
        if self.animation_state == "walking":
            left_leg_y = self.y + 50 + self.arm_swing
            right_leg_y = self.y + 50 - self.arm_swing
        else:
            left_leg_y = self.y + 50
            right_leg_y = self.y + 50
            
        pygame.draw.rect(screen, leg_color, (self.x + 10, left_leg_y, 8, 10))
        pygame.draw.rect(screen, leg_color, (self.x + 22, right_leg_y, 8, 10))
        
        # Feet with walking animation
        foot_color = (139, 69, 19)  # Brown shoes
        if self.animation_state == "walking":
            left_foot_y = left_leg_y + 10
            right_foot_y = right_leg_y + 10
        else:
            left_foot_y = self.y + 60
            right_foot_y = self.y + 60
            
        pygame.draw.rect(screen, foot_color, (self.x + 8, left_foot_y, 6, 4))
        pygame.draw.rect(screen, foot_color, (self.x + 26, right_foot_y, 6, 4))
        
        # Draw fishing line when fishing
        if self.animation_state == "fishing" and self.cast_target:
            rod_start = (self.x + self.width//2, self.y + 15)
            rod_end = (self.x + self.width//2 + (30 if self.facing_right else -30), self.y - 20)
            pygame.draw.line(screen, BROWN, rod_start, rod_end, 3)
            pygame.draw.line(screen, BLACK, rod_end, self.cast_target, 1)

class FishingMinigame:
    def __init__(self):
        self.is_active = False
        self.fish = None
        self.hook_bar_pos = 0
        self.target_zone_start = 0
        self.target_zone_end = 0
        self.bar_speed = 2
        self.direction = 1
        self.hook_set = False
        self.fish_escape_timer = 0
        self.max_escape_time = 600  # 10 seconds at 60 FPS - much more forgiving
        self.flash_timer = 0
        self.strike_indicator = 0
        
    def start_fishing(self, fish_species):
        self.is_active = True
        self.fish = fish_species
        self.hook_bar_pos = 50
        # Make target zone much larger and easier
        self.target_zone_start = random.randint(25, 55)
        self.target_zone_end = self.target_zone_start + random.randint(25, 35)  # Much larger zone
        self.bar_speed = max(1, FISH_SPECIES[fish_species]["difficulty"] - 3)  # Easier speed
        self.direction = 1
        self.hook_set = False
        self.fish_escape_timer = 0
        self.flash_timer = 0
        self.strike_indicator = 0
        
    def update(self):
        if not self.is_active:
            return
            
        # Move the hook bar
        self.hook_bar_pos += self.bar_speed * self.direction
        
        # Bounce off edges
        if self.hook_bar_pos <= 0 or self.hook_bar_pos >= 100:
            self.direction *= -1
            self.hook_bar_pos = max(0, min(100, self.hook_bar_pos))
            
        # Check if fish escapes
        if not self.hook_set:
            self.fish_escape_timer += 1
            if self.fish_escape_timer >= self.max_escape_time:
                self.is_active = False
                return "escape"
        
        # Update flash timer
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        # Update strike indicator
        self.strike_indicator = (self.strike_indicator + 1) % 60
        
        return None
        
    def set_hook(self):
        if self.target_zone_start <= self.hook_bar_pos <= self.target_zone_end:
            self.hook_set = True
            self.flash_timer = 30
            return True
        else:
            self.is_active = False
            return False
            
    def draw(self, screen):
        if not self.is_active:
            return
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw fish info
        if self.fish:
            fish_data = FISH_SPECIES[self.fish]
            font = pygame.font.Font(None, 48)
            
            # Fish name with rarity color
            color = WHITE
            if fish_data['rarity'] == Rarity.CARDBOARD: color = GRAY
            elif fish_data['rarity'] == Rarity.BRONZE: color = BRONZE
            elif fish_data['rarity'] == Rarity.SILVER: color = SILVER
            elif fish_data['rarity'] == Rarity.GOLD: color = GOLD
            elif fish_data['rarity'] == Rarity.DIAMOND: color = DIAMOND
            elif fish_data['rarity'] == Rarity.TROPHY: color = ORANGE
            elif fish_data['rarity'] == Rarity.RECORD: color = PURPLE
            
            fish_text = f"{self.fish} - {fish_data['rarity'].value}"
            text = font.render(fish_text, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100))
            
            # Difficulty indicator
            diff_text = f"Difficulty: {fish_data['difficulty']}/10"
            text = pygame.font.Font(None, 36).render(diff_text, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 150))
        
        # Draw background bar with better graphics
        bar_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50, 400, 30)
        pygame.draw.rect(screen, (50, 50, 50), bar_rect)
        pygame.draw.rect(screen, WHITE, bar_rect, 3)
        
        # Draw target zone with gradient effect
        target_x = SCREEN_WIDTH//2 - 200 + (self.target_zone_start * 4)
        target_width = (self.target_zone_end - self.target_zone_start) * 4
        target_color = GREEN if not self.flash_timer else YELLOW
        
        # Draw gradient target zone
        for i in range(int(target_width)):
            alpha = 128 + (i / target_width) * 127
            color = (*target_color, int(alpha))
            pygame.draw.line(screen, color, 
                           (target_x + i, SCREEN_HEIGHT//2 - 50),
                           (target_x + i, SCREEN_HEIGHT//2 - 20))
        
        # Draw hook position with animation
        hook_x = SCREEN_WIDTH//2 - 200 + (self.hook_bar_pos * 4)
        hook_color = RED if not self.hook_set else GREEN
        
        # Animated hook indicator
        hook_size = 8 + int(4 * math.sin(self.strike_indicator * 0.2))
        pygame.draw.circle(screen, hook_color, (hook_x, SCREEN_HEIGHT//2 - 35), hook_size)
        pygame.draw.circle(screen, WHITE, (hook_x, SCREEN_HEIGHT//2 - 35), hook_size, 2)
        
        # Draw time remaining with visual indicator
        time_left = (self.max_escape_time - self.fish_escape_timer) / 60
        time_text = f"Time: {time_left:.1f}s"
        text = pygame.font.Font(None, 36).render(time_text, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 80))
        
        # Visual time indicator
        time_bar_width = 200 * (time_left / (self.max_escape_time / 60))
        time_bar_color = GREEN if time_left > 5 else YELLOW if time_left > 2 else RED
        pygame.draw.rect(screen, time_bar_color, 
                        (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, time_bar_width, 10))
        
        # Draw instructions with better visibility
        if not self.hook_set:
            text = pygame.font.Font(None, 36).render("Press SPACE to set hook!", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        else:
            text = pygame.font.Font(None, 36).render("Hook set! Keep it steady!", True, GREEN)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 50))

class VisualEffects:
    def __init__(self):
        self.ripples = []
        self.particles = []
        self.fish_shadows = []
        self.water_animation = 0
        
    def add_ripple(self, x, y):
        self.ripples.append({"x": x, "y": y, "radius": 0, "max_radius": 80, "alpha": 255})
        
    def add_particle(self, x, y, color, velocity):
        self.particles.append({
            "x": x, "y": y,
            "vx": velocity[0], "vy": velocity[1],
            "life": 60, "max_life": 60,
            "color": color
        })
        
    def add_fish_shadow(self, x, y, size):
        self.fish_shadows.append({
            "x": x, "y": y, "size": size,
            "life": 120, "max_life": 120
        })
        
    def update(self):
        # Update ripples
        for ripple in self.ripples[:]:
            ripple["radius"] += 3
            ripple["alpha"] = int(255 * (1 - ripple["radius"] / ripple["max_radius"]))
            if ripple["radius"] >= ripple["max_radius"]:
                self.ripples.remove(ripple)
                
        # Update particles
        for particle in self.particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.particles.remove(particle)
                
        # Update fish shadows
        for shadow in self.fish_shadows[:]:
            shadow["life"] -= 1
            if shadow["life"] <= 0:
                self.fish_shadows.remove(shadow)
                
        # Update water animation
        self.water_animation = (self.water_animation + 1) % 360
                
    def draw(self, screen):
        # Draw animated water
        for i in range(200):
            wave_offset = math.sin((i + self.water_animation) * 0.1) * 3
            alpha = int(100 + (i / 200) * 100)
            color = (0, 100 + alpha//2, 150 + alpha//2)
            y_pos = SCREEN_HEIGHT - 200 + i
            pygame.draw.line(screen, color, 
                           (0, y_pos + wave_offset), 
                           (SCREEN_WIDTH, y_pos + wave_offset))
        
        # Draw ripples
        for ripple in self.ripples:
            if ripple["alpha"] > 0:
                color = (0, 100, 200, ripple["alpha"])
                pygame.draw.circle(screen, color, (ripple["x"], ripple["y"]), ripple["radius"], 3)
                
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle["life"] / particle["max_life"]))
            color = (*particle["color"], alpha)
            pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), 3)
            
        # Draw fish shadows
        for shadow in self.fish_shadows:
            alpha = int(100 * (shadow["life"] / shadow["max_life"]))
            color = (0, 0, 0, alpha)
            pygame.draw.ellipse(screen, color, 
                              (shadow["x"], shadow["y"], shadow["size"], shadow["size"]//3))

class RewardSystem:
    def __init__(self):
        self.available_rewards = {
            "Premium Worm": Reward(RewardType.BAIT, "Premium Worm", "Better chance to catch rare fish", "premium_worm"),
            "Golden Rod": Reward(RewardType.ROD, "Golden Rod", "Increases catch rate by 25%", "golden_rod"),
            "Tropical Location": Reward(RewardType.LOCATION, "Tropical Waters", "Unlock tropical fishing spot", "tropical"),
            "Fisherman Hat": Reward(RewardType.COSMETIC, "Fisherman Hat", "Stylish fishing hat", "hat"),
            "Diamond Lure": Reward(RewardType.BAIT, "Diamond Lure", "Attracts diamond-tier fish", "diamond_lure"),
            "Master Rod": Reward(RewardType.ROD, "Master Rod", "Ultimate fishing rod", "master_rod")
        }
        
    def get_quest_reward(self, quest_id):
        rewards = list(self.available_rewards.values())
        return random.choice(rewards)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.create_sounds()
        
    def create_sounds(self):
        # Simple sound system without numpy dependency
        self.sounds = {
            'splash': None,
            'catch': None,
            'escape': None,
            'menu_select': None
        }
    
    def play_sound(self, sound_name):
        # Placeholder for sound effects
        # In a real implementation, you'd load actual sound files
        pass

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("European Forest Fishing Adventure")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.player = HumanCharacter(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.fishing_minigame = FishingMinigame()
        self.background = self.create_forest_background()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.effects = VisualEffects()
        self.sound_manager = SoundManager()
        self.reward_system = RewardSystem()
        
        # Menu system
        self.menu_selection = 0
        self.menu_options = ["Start Game", "Instructions", "Quit"]
        
        # Game state variables
        self.fish_shadow_timer = 0
        self.catch_message = ""
        self.catch_message_timer = 0
        self.caught_fish = []
        self.current_bait = "Worm"
        self.available_baits = ["Worm"]
        self.quests = self.create_quests()
        self.rewards_earned = []
        
        # Fish inspection
        self.inspecting_fish = None
        
        # Casting system
        self.is_casting = False
        self.cast_target = None
        self.mouse_pos = (0, 0)
        
    def create_quests(self):
        return [
            Quest("first_fish", "First Catch", "Catch your first fish", 1, 0, 
                  self.reward_system.get_quest_reward("first_fish"), False),
            Quest("gold_fish", "Golden Hunter", "Catch 3 gold-tier fish", 3, 0,
                  self.reward_system.get_quest_reward("gold_fish"), False),
            Quest("heavy_fish", "Heavy Weight", "Catch a fish over 10kg", 1, 0,
                  self.reward_system.get_quest_reward("heavy_fish"), False),
            Quest("species_collector", "Species Collector", "Catch 5 different species", 5, 0,
                  self.reward_system.get_quest_reward("species_collector"), False),
            Quest("trophy_hunter", "Trophy Hunter", "Catch a trophy fish", 1, 0,
                  self.reward_system.get_quest_reward("trophy_hunter"), False)
        ]
        
    def create_forest_background(self):
        # Create a parallax forest background
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(DARK_GREEN)
        
        # Draw distant mountains
        for i in range(5):
            x = i * 300
            points = [(x, SCREEN_HEIGHT//2), (x + 150, SCREEN_HEIGHT//2 - 100), 
                     (x + 300, SCREEN_HEIGHT//2)]
            pygame.draw.polygon(background, (50, 100, 50), points)
        
        # Draw trees in layers
        for layer in range(3):
            tree_count = 15 - layer * 5
            for i in range(tree_count):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT//2 - layer * 50)
                tree_size = 30 - layer * 5
                # Tree trunk
                pygame.draw.rect(background, BROWN, (x, y, 15 + layer * 5, 50 + layer * 10))
                # Tree top
                pygame.draw.circle(background, GREEN, (x + 7 + layer * 2, y), tree_size)
            
        return background
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.state == GameState.PLAYING and not self.player.is_casting:
                        # Start casting to mouse position
                        self.is_casting = True
                        self.cast_target = event.pos
                        self.player.start_casting(event.pos[0], event.pos[1])
                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.MENU
                    elif self.state == GameState.FISHING:
                        self.fishing_minigame.is_active = False
                        self.player.stop_fishing()
                        self.state = GameState.PLAYING
                    elif self.state in [GameState.INVENTORY, GameState.GLOSSARY, GameState.QUEST, GameState.FISH_CAUGHT]:
                        self.state = GameState.PLAYING
                        
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.FISHING:
                        if self.fishing_minigame.set_hook():
                            self.catch_fish()
                        else:
                            self.state = GameState.PLAYING
                    elif self.state == GameState.FISH_CAUGHT:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.PLAYING and not self.player.is_casting:
                        # Cast to center of water area
                        target_x = SCREEN_WIDTH // 2
                        target_y = SCREEN_HEIGHT - 100
                        self.is_casting = True
                        self.cast_target = (target_x, target_y)
                        self.player.start_casting(target_x, target_y)
                        
                if event.key == pygame.K_c and self.state == GameState.PLAYING:
                    # Cancel casting/fishing
                    self.player.stop_fishing()
                    self.is_casting = False
                    self.cast_target = None
                        
                if event.key == pygame.K_i and self.state == GameState.PLAYING:
                    self.state = GameState.INVENTORY
                    
                if event.key == pygame.K_g and self.state == GameState.PLAYING:
                    self.state = GameState.GLOSSARY
                    
                if event.key == pygame.K_q and self.state == GameState.PLAYING:
                    self.state = GameState.QUEST
                    
                # Fish inspection controls
                if self.state == GameState.FISH_CAUGHT:
                    if event.key == pygame.K_k:  # Keep fish
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_r:  # Release fish
                        self.caught_fish.pop()  # Remove the last caught fish
                        self.state = GameState.PLAYING
                    
                # Menu navigation
                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:  # Start Game
                            self.state = GameState.PLAYING
                        elif self.menu_selection == 1:  # Instructions
                            # Could add instructions screen
                            pass
                        elif self.menu_selection == 2:  # Quit
                            return False
                    
        return True
        
    def catch_fish(self):
        fish_species = self.fishing_minigame.fish
        fish_data = FISH_SPECIES[fish_species]
        
        # Calculate weight based on rarity and species
        base_weight = random.uniform(*fish_data["weight_range"])
        rarity_multiplier = {
            Rarity.CARDBOARD: 1.0,
            Rarity.BRONZE: 1.2,
            Rarity.SILVER: 1.5,
            Rarity.GOLD: 2.0,
            Rarity.DIAMOND: 3.0,
            Rarity.TROPHY: 5.0,
            Rarity.RECORD: 10.0
        }
        
        weight = base_weight * rarity_multiplier[fish_data["rarity"]]
        length = random.uniform(*fish_data["length_range"])
        
        # Check if it's a personal record
        personal_record = True
        for fish in self.caught_fish:
            if fish.species == fish_species and fish.weight >= weight:
                personal_record = False
                break
        
        # Create fish object
        fish = Fish(
            species=fish_species,
            weight=weight,
            length=length,
            rarity=fish_data["rarity"],
            difficulty=fish_data["difficulty"],
            bait_used=self.current_bait,
            catch_time=pygame.time.get_ticks(),
            personal_record=personal_record
        )
        
        self.caught_fish.append(fish)
        self.fishing_minigame.is_active = False
        self.state = GameState.FISH_CAUGHT
        
        # Add catch effects
        self.catch_message = f"Caught {fish_species} ({weight:.1f}kg)!"
        self.catch_message_timer = 180  # 3 seconds at 60 FPS
        
        # Play catch sound
        self.sound_manager.play_sound('catch')
        
        # Add celebration particles
        for _ in range(15):
            self.effects.add_particle(
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                (255, 255, 0),
                (random.uniform(-8, 8), random.uniform(-8, 8))
            )
            
        # Add ripple effect
        self.effects.add_ripple(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)
        
        # Update quests
        self.update_quests(fish)
        
    def update_quests(self, fish):
        for quest in self.quests:
            if quest.completed:
                continue
                
            if quest.id == "first_fish":
                quest.current = len(self.caught_fish)
                if quest.current >= quest.target:
                    quest.completed = True
                    self.give_reward(quest.reward)
                    
            elif quest.id == "gold_fish":
                gold_count = len([f for f in self.caught_fish if f.rarity == Rarity.GOLD])
                quest.current = gold_count
                if quest.current >= quest.target:
                    quest.completed = True
                    self.give_reward(quest.reward)
                    
            elif quest.id == "heavy_fish":
                if fish.weight >= 10:
                    quest.current = 1
                    quest.completed = True
                    self.give_reward(quest.reward)
                    
            elif quest.id == "species_collector":
                unique_species = len(set(f.species for f in self.caught_fish))
                quest.current = unique_species
                if quest.current >= quest.target:
                    quest.completed = True
                    self.give_reward(quest.reward)
                    
            elif quest.id == "trophy_hunter":
                if fish.rarity == Rarity.TROPHY:
                    quest.current = 1
                    quest.completed = True
                    self.give_reward(quest.reward)
                    
    def give_reward(self, reward):
        self.rewards_earned.append(reward)
        
        if reward.type == RewardType.BAIT:
            if reward.value not in self.available_baits:
                self.available_baits.append(reward.value)
                self.current_bait = reward.value
        elif reward.type == RewardType.ROD:
            # Could implement rod upgrades
            pass
        elif reward.type == RewardType.LOCATION:
            # Could implement new locations
            pass
        elif reward.type == RewardType.COSMETIC:
            # Could implement cosmetic upgrades
            pass
            
    def start_fishing(self):
        # Random chance to get a fish based on location and bait
        if random.random() < 0.4:  # 40% chance - increased for easier gameplay
            available_fish = list(FISH_SPECIES.keys())
            fish_species = random.choice(available_fish)
            self.fishing_minigame.start_fishing(fish_species)
            self.state = GameState.FISHING
            
            # Play splash sound
            self.sound_manager.play_sound('splash')
            
            # Add visual effects at cast target
            if self.cast_target:
                self.effects.add_ripple(self.cast_target[0], self.cast_target[1])
                for _ in range(8):
                    self.effects.add_particle(
                        self.cast_target[0], 
                        self.cast_target[1],
                        (255, 255, 255),
                        (random.uniform(-3, 3), random.uniform(-4, -1))
                    )
        else:
            # No fish caught - add small ripple
            if self.cast_target:
                self.effects.add_ripple(self.cast_target[0], self.cast_target[1])
            
    def draw_fish_caught(self):
        if not self.caught_fish:
            return
            
        fish = self.caught_fish[-1]  # Get the last caught fish
        fish_data = FISH_SPECIES[fish.species]
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw fish inspection panel
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 250, 600, 500)
        pygame.draw.rect(self.screen, DARK_GREEN, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Fish name with rarity color
        color = WHITE
        if fish.rarity == Rarity.CARDBOARD: color = GRAY
        elif fish.rarity == Rarity.BRONZE: color = BRONZE
        elif fish.rarity == Rarity.SILVER: color = SILVER
        elif fish.rarity == Rarity.GOLD: color = GOLD
        elif fish.rarity == Rarity.DIAMOND: color = DIAMOND
        elif fish.rarity == Rarity.TROPHY: color = ORANGE
        elif fish.rarity == Rarity.RECORD: color = PURPLE
        
        title = self.font.render(fish.species, True, color)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 220))
        
        # Rarity badge
        rarity_text = self.small_font.render(fish.rarity.value, True, WHITE)
        self.screen.blit(rarity_text, (SCREEN_WIDTH//2 - rarity_text.get_width()//2, SCREEN_HEIGHT//2 - 190))
        
        # Fish stats
        y_offset = SCREEN_HEIGHT//2 - 150
        stats = [
            f"Weight: {fish.weight:.1f} kg",
            f"Length: {fish.length:.1f} cm",
            f"Location: {fish_data['location']}",
            f"Bait Used: {fish.bait_used}",
            f"Difficulty: {fish.difficulty}/10"
        ]
        
        for stat in stats:
            text = self.small_font.render(stat, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 200, y_offset))
            y_offset += 30
            
        # Personal record indicator
        if fish.personal_record:
            record_text = self.font.render("NEW PERSONAL RECORD!", True, GOLD)
            self.screen.blit(record_text, (SCREEN_WIDTH//2 - record_text.get_width()//2, y_offset + 20))
            
        # Fish description
        desc_text = fish_data['description']
        # Wrap text if too long
        words = desc_text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) * 8 < 500:  # Approximate character width
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
            
        for i, line in enumerate(lines):
            text = self.small_font.render(line, True, LIGHT_GRAY)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 200, y_offset + 60 + i * 25))
            
        # Action buttons
        keep_text = self.font.render("Press K to KEEP", True, GREEN)
        release_text = self.font.render("Press R to RELEASE", True, RED)
        continue_text = self.font.render("Press SPACE to continue", True, WHITE)
        
        self.screen.blit(keep_text, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(release_text, (SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 200))
        
    def draw_quest(self):
        self.screen.fill(DARK_GREEN)
        
        title = self.font.render("Quests & Rewards", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - 100, 50))
        
        y_pos = 120
        for quest in self.quests:
            # Quest name and progress
            color = GREEN if quest.completed else WHITE
            quest_text = f"{quest.name}: {quest.current}/{quest.target}"
            text = self.font.render(quest_text, True, color)
            self.screen.blit(text, (50, y_pos))
            
            # Quest description
            desc_text = self.small_font.render(quest.description, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (50, y_pos + 25))
            
            # Reward info
            if not quest.completed:
                reward_text = f"Reward: {quest.reward.name} - {quest.reward.description}"
                text = self.small_font.render(reward_text, True, YELLOW)
                self.screen.blit(text, (50, y_pos + 45))
            else:
                completed_text = "COMPLETED!"
                text = self.small_font.render(completed_text, True, GREEN)
                self.screen.blit(text, (50, y_pos + 45))
                
            y_pos += 80
            
        # Show earned rewards
        if self.rewards_earned:
            rewards_title = self.font.render("Earned Rewards:", True, GOLD)
            self.screen.blit(rewards_title, (50, y_pos + 20))
            
            for i, reward in enumerate(self.rewards_earned):
                reward_text = f"{reward.name}: {reward.description}"
                text = self.small_font.render(reward_text, True, WHITE)
                self.screen.blit(text, (50, y_pos + 50 + i * 25))
                
        back_text = self.font.render("Press ESC to return", True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 50))
        
    def draw_menu(self):
        self.screen.fill(DARK_GREEN)
        
        # Draw forest background elements
        for i in range(10):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT//3)
            pygame.draw.rect(self.screen, BROWN, (x, y, 15, 40))
            pygame.draw.circle(self.screen, GREEN, (x + 7, y), 20)
        
        title = self.font.render("European Forest Fishing Adventure", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - 250, 100))
        
        subtitle = self.small_font.render("A 2D Fishing Adventure", True, LIGHT_GRAY)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - 100, 140))
        
        for i, option in enumerate(self.menu_options):
            color = YELLOW if i == self.menu_selection else WHITE
            text = self.font.render(option, True, color)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 100, 250 + i * 50))
            
        # Draw instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER to select",
            "ESC to return to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, LIGHT_GRAY)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 150 + i * 25))
            
    def draw_playing(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Update and draw visual effects
        self.effects.update()
        self.effects.draw(self.screen)
        
        # Add random fish shadows in water
        self.fish_shadow_timer += 1
        if self.fish_shadow_timer > 120:  # Every 2 seconds
            self.fish_shadow_timer = 0
            if random.random() < 0.3:  # 30% chance
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(SCREEN_HEIGHT - 180, SCREEN_HEIGHT - 50)
                size = random.randint(20, 60)
                self.effects.add_fish_shadow(x, y, size)
        
        # Draw casting target indicator
        if self.is_casting and self.cast_target:
            # Draw target circle
            pygame.draw.circle(self.screen, (255, 255, 0), self.cast_target, 15, 2)
            pygame.draw.circle(self.screen, (255, 255, 0), self.cast_target, 5)
            
        # Draw mouse cursor when not casting
        if self.state == GameState.PLAYING and not self.player.is_casting:
            # Draw crosshair at mouse position
            x, y = self.mouse_pos
            pygame.draw.line(self.screen, WHITE, (x - 10, y), (x + 10, y), 2)
            pygame.draw.line(self.screen, WHITE, (x, y - 10), (x, y + 10), 2)
            
        # Draw player
        self.player.draw(self.screen)
        
        # Draw catch message
        if self.catch_message_timer > 0:
            self.catch_message_timer -= 1
            alpha = int(255 * (self.catch_message_timer / 180))
            if alpha > 0:
                # Draw background for message
                text_surface = self.font.render(self.catch_message, True, WHITE)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
                pygame.draw.rect(self.screen, (0, 0, 0, 128), 
                               (text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10))
                self.screen.blit(text_surface, text_rect)
        
        # Draw UI with rarity colors
        info_text = f"Fish Caught: {len(self.caught_fish)} | Bait: {self.current_bait}"
        text = self.small_font.render(info_text, True, WHITE)
        self.screen.blit(text, (10, 10))
        
        # Draw rarity statistics
        rarity_counts = {}
        for fish in self.caught_fish:
            rarity = fish.rarity.value
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
            
        y_offset = 30
        for rarity, count in rarity_counts.items():
            color = WHITE
            if rarity == "Cardboard": color = GRAY
            elif rarity == "Bronze": color = BRONZE
            elif rarity == "Silver": color = SILVER
            elif rarity == "Gold": color = GOLD
            elif rarity == "Diamond": color = DIAMOND
            elif rarity == "Trophy": color = ORANGE
            elif rarity == "Record Fish": color = PURPLE
            
            rarity_text = f"{rarity}: {count}"
            text = self.small_font.render(rarity_text, True, color)
            self.screen.blit(text, (10, y_offset))
            y_offset += 20
        
        # Draw controls
        controls = "WASD: Move | SPACE: Cast | Mouse: Aim | C: Cancel | I: Inventory | G: Glossary | Q: Quests"
        text = self.small_font.render(controls, True, WHITE)
        self.screen.blit(text, (10, SCREEN_HEIGHT - 30))
        
        # Draw casting status
        if self.player.is_casting:
            cast_text = f"Casting... {int(self.player.cast_progress * 100)}%"
            text = self.small_font.render(cast_text, True, YELLOW)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 10))
        elif self.player.animation_state == "fishing":
            fish_text = "Fishing... Press C to stop"
            text = self.small_font.render(fish_text, True, GREEN)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 10))
        
    def draw_inventory(self):
        self.screen.fill(DARK_GREEN)
        
        title = self.font.render("Inventory - Caught Fish", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - 150, 50))
        
        if not self.caught_fish:
            text = self.font.render("No fish caught yet!", True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 100, 200))
        else:
            # Sort fish by rarity
            sorted_fish = sorted(self.caught_fish, key=lambda f: list(Rarity).index(f.rarity), reverse=True)
            
            for i, fish in enumerate(sorted_fish[-15:]):  # Show last 15
                y_pos = 120 + i * 50
                if y_pos < SCREEN_HEIGHT - 100:
                    # Color based on rarity
                    color = WHITE
                    if fish.rarity == Rarity.CARDBOARD: color = GRAY
                    elif fish.rarity == Rarity.BRONZE: color = BRONZE
                    elif fish.rarity == Rarity.SILVER: color = SILVER
                    elif fish.rarity == Rarity.GOLD: color = GOLD
                    elif fish.rarity == Rarity.DIAMOND: color = DIAMOND
                    elif fish.rarity == Rarity.TROPHY: color = ORANGE
                    elif fish.rarity == Rarity.RECORD: color = PURPLE
                    
                    fish_text = f"{fish.species} - {fish.weight:.1f}kg ({fish.rarity.value})"
                    text = self.small_font.render(fish_text, True, color)
                    self.screen.blit(text, (50, y_pos))
                    
                    # Show bait used
                    bait_text = f"Bait: {fish.bait_used}"
                    text = self.small_font.render(bait_text, True, LIGHT_GRAY)
                    self.screen.blit(text, (50, y_pos + 15))
                    
        back_text = self.font.render("Press ESC to return", True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 50))
        
    def draw_glossary(self):
        self.screen.fill(DARK_GREEN)
        
        title = self.font.render("Fish Glossary", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - 100, 50))
        
        # Sort by rarity
        sorted_species = sorted(FISH_SPECIES.items(), 
                              key=lambda x: list(Rarity).index(x[1]['rarity']), reverse=True)
        
        y_pos = 120
        for species, data in sorted_species:
            if y_pos < SCREEN_HEIGHT - 100:
                # Color based on rarity
                color = WHITE
                if data['rarity'] == Rarity.CARDBOARD: color = GRAY
                elif data['rarity'] == Rarity.BRONZE: color = BRONZE
                elif data['rarity'] == Rarity.SILVER: color = SILVER
                elif data['rarity'] == Rarity.GOLD: color = GOLD
                elif data['rarity'] == Rarity.DIAMOND: color = DIAMOND
                elif data['rarity'] == Rarity.TROPHY: color = ORANGE
                elif data['rarity'] == Rarity.RECORD: color = PURPLE
                
                species_text = f"{species} - {data['rarity'].value}"
                text = self.small_font.render(species_text, True, color)
                self.screen.blit(text, (50, y_pos))
                
                desc_text = f"Location: {data['location']} | Weight: {data['weight_range'][0]}-{data['weight_range'][1]}kg | Difficulty: {data['difficulty']}"
                text = self.small_font.render(desc_text, True, LIGHT_GRAY)
                self.screen.blit(text, (50, y_pos + 20))
                
                bait_text = f"Bait: {', '.join(data['bait'])}"
                text = self.small_font.render(bait_text, True, LIGHT_GRAY)
                self.screen.blit(text, (50, y_pos + 35))
                
                y_pos += 80
                
        back_text = self.font.render("Press ESC to return", True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 50))
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            keys = pygame.key.get_pressed()
            
            if self.state == GameState.PLAYING:
                self.player.move(keys)
                
                # Update casting
                if self.player.is_casting:
                    if self.player.update_casting():
                        self.start_fishing()
                    
            elif self.state == GameState.FISHING:
                result = self.fishing_minigame.update()
                if result == "escape":
                    self.state = GameState.PLAYING
                    self.player.stop_fishing()
                    # Play escape sound
                    self.sound_manager.play_sound('escape')
                    # Add escape effect
                    for _ in range(5):
                        self.effects.add_particle(
                            SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                            (255, 0, 0),
                            (random.uniform(-5, 5), random.uniform(-5, 5))
                        )
                    
            # Draw
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.draw_playing()
            elif self.state == GameState.FISHING:
                self.draw_playing()
                self.fishing_minigame.draw(self.screen)
            elif self.state == GameState.FISH_CAUGHT:
                self.draw_playing()
                self.draw_fish_caught()
            elif self.state == GameState.INVENTORY:
                self.draw_inventory()
            elif self.state == GameState.GLOSSARY:
                self.draw_glossary()
            elif self.state == GameState.QUEST:
                self.draw_quest()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 