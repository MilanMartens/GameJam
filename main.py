import random
import arcade
import math 
import json
import os

SPRITE_SCALING = 1.2
PLAYER_MOVEMENT_SPEED = 5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprite Change Coins"

HIGHSCORE_FILE = "highscore.json"

def load_highscore():
    """Load highscore from file, return 0 if file doesn't exist"""
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('highscore', 0)
        return 0
    except:
        return 0

def save_highscore(score):
    """Save highscore to file"""
    try:
        data = {'highscore': score}
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass  # Silently fail if we can't save


class Collectable(arcade.Sprite):
    """ This class represents something the player collects. """

    def __init__(self, scale):
        super().__init__(scale=scale)
        # Flip this once the coin has been collected.
        self.changed = False
        
        # Setup burger animation
        self.setup_burger_animation()
        self.animation_timer = random.uniform(0, 0.4)  # Random start for variety
        self.animation_speed = random.uniform(0.25, 0.35)  # Varied animation speed
        self.current_frame = 0
        
        # Bounce animation
        self.bounce_timer = random.uniform(0, 6.28)  # Random start phase
        self.bounce_speed = random.uniform(2.5, 3.5)  # Bounce frequency
        self.bounce_height = random.uniform(8, 15)  # Bounce amplitude
        self.original_y = 0  # Will be set when positioned
        
        # Scale pulsing
        self.pulse_timer = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(4.0, 6.0)
        self.base_scale = scale
        self.pulse_amount = random.uniform(0.1, 0.2)  # 10-20% size variation
        
    def setup_burger_animation(self):
        """Setup burger texture"""
        # Load the single burger image
        burger_texture = arcade.load_texture("WarioSprites/burger.png")
        
        # Create animation frames list with just one frame
        self.animation_frames = [burger_texture]
        
        # Set initial texture
        self.texture = burger_texture
        
    def update(self, delta_time=1/60):
        """Update burger animation with multiple effects"""
        super().update()
        
        # Only animate if not collected yet - simplified for performance
        if not self.changed:
            # Simple bounce animation only (removed complex pulsing)
            self.bounce_timer += delta_time
            bounce_offset = math.sin(self.bounce_timer * 3.0) * 10  # Fixed values for better performance
            self.center_y = self.original_y + bounce_offset
        else:
            # Simplified Collection Effect for better performance
            self.collection_timer = getattr(self, 'collection_timer', 0.0) + delta_time
            
            # Single phase: Quick scale and spin effect
            if self.collection_timer < 0.5:
                # Simple scale burst
                scale_factor = 1.0 + (self.collection_timer * 4.0)
                self.scale = self.base_scale * scale_factor
                
                # Simple spinning
                self.angle += delta_time * 720  # 2 rotations per second
                
                # Move upward
                self.center_y += delta_time * 100
            else:
                # Final fade out phase
                fade_factor = 1.0 - ((self.collection_timer - 0.5) / 0.5)
                self.scale = self.base_scale * max(0.1, fade_factor)
                self.center_y += delta_time * 50


class Enemy(arcade.Sprite):
    """Enemy sprite that moves horizontally across screen"""
    
    def __init__(self, scale, direction, window_width=1280):
        super().__init__(scale=scale)
        self.direction = direction  # 1 for right, -1 for left
        self.window_width = window_width  # Store window width for boundary checking
        
        # Load random food texture from food folder
        food_files = [
            "01_Cherry_Red.png", "02_Cherry_Black.png", "03_Cranberry.png",
            "04_Cucumber.png", "05_CustardApple.png", "06_Plum.png", 
            "07_Dragonfruit.png", "10_Grapes_Black.png", "11_Grapes_Green.png",
            "12_Grapefruit.png", "13_Guava.png", "14_Kiwi.png", "15_Lemon.png",
            "16_Apple.png", "19_Peach.png", "20_Passionfruit.png", "21_Apricot.png",
            "22_Strawberry.png", "23_Watermelon.png", "24_Melon.png"
        ]
        
        # Choose random food sprite
        random_food = random.choice(food_files)
        try:
            self.texture = arcade.load_texture(f"food/{random_food}")
        except:
            # Fallback to Wario sprite if food sprite fails to load
            self.texture = arcade.load_texture("WarioSprites/Run1Wario.png")
        
        # Set horizontal speed
        self.speed = random.uniform(3.0, 6.0)  # Random speed between 3-6 (increased from 2-4)
        self.change_x = self.speed * self.direction
        
        # Set rotation speed (random spin speed)
        self.rotation_speed = random.uniform(-5.0, 5.0)  # Random rotation between -5 and 5 degrees per frame
        
    def update(self, delta_time=1/60):
        super().update()
        
        # Rotate the food sprite
        self.angle += self.rotation_speed
        
        # Remove enemy when it goes completely off screen using stored window width
        if self.direction > 0 and self.left > self.window_width + 50:  # Moving right, completely off right edge
            self.remove_from_sprite_lists()
        elif self.direction < 0 and self.right < -50:  # Moving left, completely off left edge
            self.remove_from_sprite_lists()


class StartView(arcade.View):
    """Start screen with titlescreen image"""
    
    def __init__(self):
        super().__init__()
        self.background_color = (0, 13, 55)  # #000D37
        
        # Create sprite list for titlescreen
        self.titlescreen_list = arcade.SpriteList()
        
        # Load the titlescreen image
        try:
            self.titlescreen_sprite = arcade.Sprite("WarioSprites/titlescreen.png")
            self.titlescreen_list.append(self.titlescreen_sprite)
        except:
            # If loading fails, create empty list
            self.titlescreen_sprite = None
            
        # Load highscore
        self.highscore = load_highscore()
        

    
    def on_draw(self):
        """Draw the start screen"""
        self.clear()
        
        # Get dynamic screen center (works with fullscreen and different window sizes)
        center_x = self.window.width // 2
        center_y = self.window.height // 2
        
        # Update titlescreen position and scale dynamically
        if self.titlescreen_sprite:
            self.titlescreen_sprite.center_x = center_x
            self.titlescreen_sprite.center_y = center_y
            
            # Scale to fit current window size while maintaining aspect ratio
            scale_x = self.window.width / self.titlescreen_sprite.texture.width
            scale_y = self.window.height / self.titlescreen_sprite.texture.height
            self.titlescreen_sprite.scale = min(scale_x, scale_y)
            
            # Draw the titlescreen
            self.titlescreen_list.draw()
        else:
            # Fallback if titlescreen can't be loaded - no text, just show blank screen
            pass
            
        # Draw highscore in top-left corner
        if self.highscore > 0:
            arcade.draw_text(
                f"High Score: {self.highscore}",
                20,
                self.window.height - 40,
                arcade.color.YELLOW,
                font_size=24,
                anchor_x="left",
                font_name="Arial",
                bold=True
            )
            
        # Draw Item Shop button in top-right corner
        shop_button_width = 150
        shop_button_height = 40
        shop_button_x = self.window.width - shop_button_width - 20
        shop_button_y = self.window.height - shop_button_height - 20
        
        # Button background
        arcade.draw_lrbt_rectangle_filled(
            shop_button_x,
            shop_button_x + shop_button_width,
            shop_button_y,
            shop_button_y + shop_button_height,
            arcade.color.DARK_BLUE
        )
        
        # Button border
        arcade.draw_lrbt_rectangle_outline(
            shop_button_x,
            shop_button_x + shop_button_width,
            shop_button_y,
            shop_button_y + shop_button_height,
            arcade.color.LIGHT_BLUE,
            3
        )
        
        # Button text
        arcade.draw_text(
            "ITEM SHOP",
            shop_button_x + shop_button_width // 2,
            shop_button_y + shop_button_height // 2 - 8,
            arcade.color.WHITE,
            font_size=16,
            anchor_x="center",
            font_name="Arial",
            bold=True
        )

    
    def on_update(self, delta_time):
        """Update start screen"""
        pass
    
    def on_key_press(self, key, modifiers):
        """Handle key presses on start screen"""
        if key == arcade.key.SPACE:
            # Start the game
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.F11:
            # Toggle fullscreen
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.ESCAPE:
            # Quit the game

            self.window.close()
    
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks on start screen"""
        # Simple check: if click is in the right half of the top part of screen, go to item shop
        if x > self.window.width * 0.5 and y > self.window.height * 0.7:
            # Open item shop
            item_shop_view = ItemShopView()
            self.window.show_view(item_shop_view)
        else:
            # Start game when clicking anywhere else on start screen
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


class GameOverView(arcade.View):
    """Game Over screen with button navigation"""
    
    def __init__(self, final_score):
        super().__init__()
        self.final_score = final_score
        self.background_color = arcade.color.BLACK
        
        # Load current highscore and check if we have a new one
        self.highscore = load_highscore()
        self.is_new_highscore = final_score > self.highscore
        
        # Update highscore if needed
        if self.is_new_highscore:
            self.highscore = final_score
            save_highscore(final_score)
        
        # Button system
        self.selected_button = 0  # 0 = Restart, 1 = Start Screen, 2 = Quit
        self.buttons = [
            {"text": "RESTART GAME", "action": "restart"},
            {"text": "START SCREEN", "action": "start_screen"},
            {"text": "QUIT GAME", "action": "quit"}
        ]
        
        # Animation timer for button glow effect
        self.animation_timer = 0.0
    
    def on_draw(self):
        """Draw the game over screen"""
        self.clear()
        
        # Use actual window dimensions for proper centering in fullscreen
        center_x = self.window.width // 2
        center_y = self.window.height // 2
        
        # Draw "GAME OVER" text
        arcade.draw_text(
            "GAME OVER",
            center_x,
            center_y + 50,
            arcade.color.RED,
            font_size=50,
            anchor_x="center",
            font_name="Arial",
            bold=True
        )
        
        # Draw final score
        score_color = arcade.color.YELLOW if self.is_new_highscore else arcade.color.WHITE
        arcade.draw_text(
            f"Final Score: {self.final_score}",
            center_x,
            center_y + 10,
            score_color,
            font_size=30,
            anchor_x="center",
            font_name="Arial",
            bold=self.is_new_highscore
        )
        
        # Draw NEW HIGHSCORE message if applicable
        if self.is_new_highscore:
            # Animated glow effect
            glow_alpha = int(128 + 127 * math.sin(self.animation_timer * 8))
            glow_color = (*arcade.color.GOLD[:3], glow_alpha)
            
            arcade.draw_text(
                "NEW HIGH SCORE!",
                center_x,
                center_y - 30,
                arcade.color.GOLD,
                font_size=24,
                anchor_x="center",
                font_name="Arial",
                bold=True
            )
        else:
            # Show current highscore
            arcade.draw_text(
                f"High Score: {self.highscore}",
                center_x,
                center_y - 30,
                arcade.color.GRAY,
                font_size=20,
                anchor_x="center",
                font_name="Arial"
            )
        
       
        # Draw buttons
        button_start_y = center_y - 100
        button_height = 50
        button_width = 300
        button_spacing = 70
        
        for i, button in enumerate(self.buttons):
            button_y = button_start_y - (i * button_spacing)
            
            # Determine button colors based on selection
            if i == self.selected_button:
                # Selected button - bright colors with animation
                glow_intensity = math.sin(self.animation_timer * 6) * 0.3 + 0.7
                button_color = (
                    int(255 * glow_intensity),
                    int(165 * glow_intensity),
                    0
                )
                text_color = arcade.color.BLACK
                border_color = arcade.color.YELLOW
                border_width = int(4 + math.sin(self.animation_timer * 8) * 2)
            else:
                # Unselected button - darker colors
                button_color = arcade.color.DARK_GRAY
                text_color = arcade.color.WHITE
                border_color = arcade.color.GRAY
                border_width = 2
            
            # Draw button background
            arcade.draw_lrbt_rectangle_filled(
                center_x - button_width // 2,
                center_x + button_width // 2,
                button_y - button_height // 2,
                button_y + button_height // 2,
                button_color
            )
            
            # Draw button border
            arcade.draw_lrbt_rectangle_outline(
                center_x - button_width // 2,
                center_x + button_width // 2,
                button_y - button_height // 2,
                button_y + button_height // 2,
                border_color, border_width
            )
            
            # Draw button text
            arcade.draw_text(
                button["text"],
                center_x,
                button_y - 10,
                text_color,
                font_size=22,
                anchor_x="center",
                font_name="Arial",
                bold=True
            )
            

    
    def on_key_press(self, key, modifiers):
        """Handle key presses on game over screen"""
        # Navigation with arrow keys only
        if key == arcade.key.UP:
            self.selected_button = (self.selected_button - 1) % len(self.buttons)
        elif key == arcade.key.DOWN:
            self.selected_button = (self.selected_button + 1) % len(self.buttons)
        
        # Execute selected action with ENTER or SPACE only
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            self.execute_selected_action()
    
    def execute_selected_action(self):
        """Execute the action of the currently selected button"""
        action = self.buttons[self.selected_button]["action"]
        
        if action == "restart":
            # Restart the game directly
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif action == "start_screen":
            # Go back to start screen
            start_view = StartView()
            self.window.show_view(start_view)
        elif action == "quit":
            # Quit the game
            self.window.close()
    
    def on_update(self, delta_time):
        """Update animation timer"""
        self.animation_timer += delta_time


class ItemShopView(arcade.View):
    """Item Shop screen"""
    
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.PURPLE
        
        # Create sprite list for the shiny wario sprite
        self.sprite_list = arcade.SpriteList()
        
        # Load Shiny Wario sprite
        self.shiny_wario_sprite = None
        try:
            self.shiny_wario_sprite = arcade.Sprite("ShinyWarioSprites/SSWarioShiny.png", scale=2.0)
            self.sprite_list.append(self.shiny_wario_sprite)
        except Exception as e:
            print(f"Could not load Shiny Wario sprite: {e}")
        
        # Shop item data
        self.shop_item = {
            "name": "Shiny Wario Skin",
            "price": 40,
            "description": "Unlock the shiny appearance!"
        }
        
        # Purchase state
        self.item_purchased = False
        self.player_coins = 50  # Give player some coins for testing
        
        # Animation variables
        self.animation_timer = 0.0
        
    def on_draw(self):
        """Draw the item shop screen"""
        self.clear()
        
        # Get dynamic screen center
        center_x = self.window.width // 2
        center_y = self.window.height // 2
        
        # Draw title
        arcade.draw_text(
            "ITEM SHOP",
            center_x,
            self.window.height - 60,
            arcade.color.GOLD,
            font_size=50,
            anchor_x="center"
        )
        
        # Draw player coins
        arcade.draw_text(
            f"Coins: {self.player_coins}",
            50,
            self.window.height - 50,
            arcade.color.YELLOW,
            font_size=20,
            bold=True
        )
        
        # Draw shop item box
        item_width = 400
        item_height = 300
        item_x = center_x - item_width // 2
        item_y = center_y - item_height // 2
        
        # Item background
        arcade.draw_lrbt_rectangle_filled(
            item_x, item_x + item_width,
            item_y, item_y + item_height,
            arcade.color.DARK_BLUE
        )
        
        # Item border
        arcade.draw_lrbt_rectangle_outline(
            item_x, item_x + item_width,
            item_y, item_y + item_height,
            arcade.color.GOLD, 3
        )
        
        # Position and animate Shiny Wario sprite
        if self.shiny_wario_sprite:
            # Floating animation - move up and down
            float_offset = math.sin(self.animation_timer * 2) * 15
            
            # Scale animation - pulse effect
            scale_base = 2.0
            scale_variation = math.sin(self.animation_timer * 3) * 0.2
            self.shiny_wario_sprite.scale = scale_base + scale_variation
            
            # Rotation animation - slight wobble
            rotation_offset = math.sin(self.animation_timer * 1.5) * 5
            self.shiny_wario_sprite.angle = rotation_offset
            
            # Position with floating effect
            self.shiny_wario_sprite.center_x = center_x
            self.shiny_wario_sprite.center_y = center_y + 50 + float_offset
            
            self.sprite_list.draw()
        else:
            # Animated fallback if sprite couldn't be loaded
            float_offset = math.sin(self.animation_timer * 2) * 10
            pulse_size = 40 + math.sin(self.animation_timer * 3) * 5
            
            arcade.draw_circle_filled(center_x, center_y + 50 + float_offset, pulse_size, arcade.color.GOLD)
            arcade.draw_circle_outline(center_x, center_y + 50 + float_offset, pulse_size, arcade.color.ORANGE, 3)
            arcade.draw_text(
                "SHINY",
                center_x,
                center_y + 50 + float_offset,
                arcade.color.BLACK,
                font_size=14,
                anchor_x="center",
                bold=True
            )
        
        # Item name
        arcade.draw_text(
            self.shop_item["name"],
            center_x,
            center_y - 50,
            arcade.color.GOLD,
            font_size=24,
            anchor_x="center",
            bold=True
        )
        
        # Item description
        arcade.draw_text(
            self.shop_item["description"],
            center_x,
            center_y - 80,
            arcade.color.WHITE,
            font_size=16,
            anchor_x="center"
        )
        
        # Item price
        arcade.draw_text(
            f"Price: {self.shop_item['price']} coins",
            center_x,
            center_y - 110,
            arcade.color.YELLOW,
            font_size=20,
            anchor_x="center",
            bold=True
        )
        
        # Buy button
        button_width = 200
        button_height = 50
        button_x = center_x - button_width // 2
        button_y = center_y - 180
        
        # Determine button appearance based on purchase state and affordability
        if self.item_purchased:
            button_color = arcade.color.GRAY
            border_color = arcade.color.DARK_GRAY
            button_text = "PURCHASED"
            text_color = arcade.color.WHITE
        elif self.player_coins >= self.shop_item["price"]:
            button_color = arcade.color.GREEN
            border_color = arcade.color.DARK_GREEN
            button_text = "BUY NOW"
            text_color = arcade.color.WHITE
        else:
            button_color = arcade.color.RED
            border_color = arcade.color.DARK_RED
            button_text = "NOT ENOUGH COINS"
            text_color = arcade.color.WHITE
        
        # Button background
        arcade.draw_lrbt_rectangle_filled(
            button_x,
            button_x + button_width,
            button_y,
            button_y + button_height,
            button_color
        )
        
        # Button border
        arcade.draw_lrbt_rectangle_outline(
            button_x,
            button_x + button_width,
            button_y,
            button_y + button_height,
            border_color,
            3
        )
        
        # Button text
        arcade.draw_text(
            button_text,
            center_x,
            button_y + button_height // 2 - 8,
            text_color,
            font_size=16 if button_text == "NOT ENOUGH COINS" else 20,
            anchor_x="center",
            bold=True
        )
        
        # Back instruction
        arcade.draw_text(
            "Press ESC to go back",
            center_x,
            50,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center"
        )
    
    def on_update(self, delta_time):
        """Update animation timer"""
        self.animation_timer += delta_time
        
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks on item shop"""
        center_x = self.window.width // 2
        center_y = self.window.height // 2
        
        # Buy button coordinates
        button_width = 200
        button_height = 50
        button_x = center_x - button_width // 2
        button_y = center_y - 180
        
        # Check if clicking on buy button
        if (button_x <= x <= button_x + button_width and
            button_y <= y <= button_y + button_height):
            # Handle purchase
            if not self.item_purchased and self.player_coins >= self.shop_item["price"]:
                # Deduct coins and mark as purchased
                self.player_coins -= self.shop_item["price"]
                self.item_purchased = True
                print(f"Item purchased! Remaining coins: {self.player_coins}")
            elif self.item_purchased:
                print("Item already purchased!")
            else:
                print("Not enough coins!")
        else:
            # Return to start screen when clicking elsewhere
            start_view = StartView()
            self.window.show_view(start_view)
        
    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.ESCAPE or key == arcade.key.ENTER:
            # Return to start screen
            start_view = StartView()
            self.window.show_view(start_view)
        elif key == arcade.key.F11:
            # Toggle fullscreen
            self.window.set_fullscreen(not self.window.fullscreen)


class GameView(arcade.View):
    """
    Main application class.a
    """

    def __init__(self):
        super().__init__()

        # Sprite lists
        self.player_list = None
        self.coin_list = None
        self.printer_list = None
        self.enemy_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None
        self.bumper_texture = arcade.load_texture(":resources:images/pinball/bumper.png")
        
        # Printer system
        self.printers_spawned = False
        self.printer_spawn_timer = 0.0
        self.printer_spawn_interval = 6.0  # 6 seconds
        
        # Player movement
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        
        # Coin spawning system
        self.coin_spawn_timer = 0.0
        self.coin_spawn_interval = 5.0  # 5 seconds
        
        # Enemy spawning system
        self.enemy_spawn_timer = 0.0
        self.enemy_spawn_interval = 3.0  # 3 seconds (reduced from 4)
        
        # Performance optimization: Pre-create Text objects
        self.score_text = arcade.Text(
            "Score: 0",
            20, 0,  # y will be set dynamically
            arcade.color.WHITE,
            font_size=20,
            font_name="Arial",
            bold=True
        )
        
        # Load highscore for display
        self.highscore = load_highscore()
        self.highscore_text = arcade.Text(
            f"High Score: {self.highscore}",
            20, 0,  # y will be set dynamically
            arcade.color.YELLOW,
            font_size=16,
            font_name="Arial"
        )

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.printer_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        
        # Create animated Wario sprite using the spritesheet
        self.player_sprite = arcade.Sprite(scale=2.0)
        
        # Load animation frames from the spritesheet
        # Assuming the spritesheet has frames arranged horizontally
        self.setup_player_animations()
        
        self.player_sprite.center_x = WINDOW_WIDTH // 2
        self.player_sprite.center_y = WINDOW_HEIGHT // 2
        self.player_list.append(self.player_sprite)

        # Start with only 5 burgers
        for i in range(5):
            # Create the burger instance
            burger = Collectable(scale=SPRITE_SCALING)

            # Position the burger
            burger.center_x = random.randrange(WINDOW_WIDTH)
            burger.center_y = random.randrange(WINDOW_HEIGHT)
            burger.original_y = burger.center_y  # Store original position for bouncing

            # Add the burger to the lists
            self.coin_list.append(burger)

        # Load collection sound
        try:
            self.collect_sound = arcade.load_sound("sound/eating.mp3")
        except:
            # Fallback if sound doesn't exist
            self.collect_sound = None
            
        # Load die sound
        try:
            self.die_sound = arcade.load_sound("sound/die.mp3")
        except:
            # Fallback if sound doesn't exist
            self.die_sound = None

        # Set the background color (we'll draw a custom background instead)
        self.background_color = arcade.color.DARK_GREEN
        
        # Background animation timer
        self.background_timer = 0.0

    def setup_player_animations(self):
        # Load idle PNG for no key pressed
        self.idle_texture_still = arcade.load_texture("WarioSprites/SSWario.png")
        """Setup Wario animations from spritesheet"""
        # Load both spritesheets
        self.spritesheet_right = arcade.load_texture("WarioSprites/WarioSpritesAll.png")
        self.spritesheet_left = arcade.load_texture("WarioSprites/WarioSpritesAllBackwards.png")

        # Idle animations
        self.idle_texture_list_right = []
        self.idle_texture_list_left = []
        idle_frame_right = self.spritesheet_right.crop(0, 0, 32, 32)
        idle_frame_left = self.spritesheet_left.crop(0, 0, 32, 32)
        self.idle_texture_list_right.append(idle_frame_right)
        self.idle_texture_list_left.append(idle_frame_left)

        # Walking animations
        self.walking_texture_list_right = []
        self.walking_texture_list_left = []
        for i in range(4):
            frame_right = self.spritesheet_right.crop(i * 32, 0, 32, 32)
            frame_left = self.spritesheet_left.crop(i * 32, 0, 32, 32)
            self.walking_texture_list_right.append(frame_right)
            self.walking_texture_list_left.append(frame_left)

        # Set up initial animations (default to right)
        self.player_sprite.idle_texture_pair = self.idle_texture_list_right
        self.player_sprite.walk_textures = self.walking_texture_list_right
        self.player_sprite.texture = self.idle_texture_list_right[0]

        # Animation variables
        self.player_sprite.cur_texture = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.2  # Change frame every 0.2 seconds

    def update_player_animation(self, delta_time):
        """Update Wario animation based on movement"""
        self.animation_timer += delta_time
        
        # Check if player is moving
        is_moving = (self.player_sprite.change_x != 0 or self.player_sprite.change_y != 0)

        # Determine direction (left or right)
        if self.player_sprite.change_x < 0:
            # Moving left
            self.player_sprite.idle_texture_pair = self.idle_texture_list_left
            self.player_sprite.walk_textures = self.walking_texture_list_left
        else:
            # Moving right or idle
            self.player_sprite.idle_texture_pair = self.idle_texture_list_right
            self.player_sprite.walk_textures = self.walking_texture_list_right

        # Check if no arrow key is pressed
        no_key_pressed = not (self.up_pressed or self.down_pressed or self.left_pressed or self.right_pressed)

        if no_key_pressed:
            # Use still idle PNG
            self.player_sprite.texture = self.idle_texture_still
            self.player_sprite.cur_texture = 0
        elif is_moving:
            # Use walking animation
            if self.animation_timer >= self.animation_speed:
                self.player_sprite.cur_texture += 1
                if self.player_sprite.cur_texture >= len(self.player_sprite.walk_textures):
                    self.player_sprite.cur_texture = 0
                self.player_sprite.texture = self.player_sprite.walk_textures[self.player_sprite.cur_texture]
                self.animation_timer = 0.0
        else:
            # Use idle animation
            self.player_sprite.texture = self.player_sprite.idle_texture_pair[0]
            self.player_sprite.cur_texture = 0
            self.player_sprite.cur_texture = 0

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw custom background
        self.draw_background()

        # Draw all the sprites.
        self.coin_list.draw()
        self.player_list.draw()
        self.printer_list.draw()
        self.enemy_list.draw()

        # Draw score box in top-left corner
        self.draw_score_box()

    def draw_score_box(self):
        """Draw score text in the top-left corner - optimized"""
        # Update text content and position only when needed
        self.score_text.text = f"Score: {self.score}"
        self.score_text.y = self.window.height - 40
        self.score_text.draw()
        
        # Draw highscore below current score
        if self.highscore > 0:
            self.highscore_text.text = f"High Score: {self.highscore}"
            self.highscore_text.y = self.window.height - 65
            self.highscore_text.draw()

    def draw_background(self):
        """Draw an optimized animated background"""
        # Simpler, stable Wario-themed background (purple -> magenta gradient)
        width = int(self.window.width)
        height = int(self.window.height)

        steps = 8
        for i in range(steps):
            t = i / max(1, steps - 1)
            # Interpolate between two purple shades
            r = int((30 * (1 - t)) + (140 * t))
            g = int((8 * (1 - t)) + (24 * t))
            b = int((60 * (1 - t)) + (180 * t))
            arcade.draw_lrbt_rectangle_filled(0, width, (height / steps) * i, (height / steps) * (i + 1), (r, g, b, 255))

        # Large subtle gold emblem behind the play area (use circle for safety)
        emblem_alpha = int(30 + 15 * math.sin(self.background_timer * 1.5))
        emblem_radius = int(min(width, height) * 0.45)
        arcade.draw_circle_filled(width // 2, height // 2 + 40, emblem_radius, (212, 175, 55, emblem_alpha))

        # Diagonal gold accents (low alpha to avoid overpowering)
        accent_count = 6
        for i in range(accent_count):
            x = (i - 1) * (width // (accent_count - 1)) + int((math.sin(self.background_timer * 0.6 + i) * 40))
            # Draw a rotated rectangle by computing its four corners and using draw_polygon_filled
            stripe_w = max(12, width // 60)
            angle_deg = 20
            angle = math.radians(angle_deg)
            cx = x
            cy = height // 2
            hw = width / 2
            hh = stripe_w / 2
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            pts = []
            for lx, ly in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]:
                rx = cx + lx * cos_a - ly * sin_a
                ry = cy + lx * sin_a + ly * cos_a
                pts.append((rx, ry))
            arcade.draw_polygon_filled(pts, (210, 180, 0, 25))

        # Floating gold coins (small decorative circles)
        coin_count = 7
        for i in range(coin_count):
            cx = int((width / coin_count) * i + 40 + math.sin(self.background_timer * 0.5 + i) * 30)
            cy = int(height * 0.7 + math.cos(self.background_timer * 0.4 + i) * 30)
            r = 8 + (i % 3) * 3
            arcade.draw_circle_filled(cx, cy, r, (212, 175, 55, 220))
            arcade.draw_circle_filled(cx - r // 3, cy + r // 3, r // 2, (255, 235, 155, 160))

        # Small sparkles
        for i in range(10):
            sx = int((width / 10) * i + math.sin(self.background_timer * 2 + i) * 20)
            sy = int(height * 0.9 + math.cos(self.background_timer * 3 + i) * 10)
            alpha = int(80 + 60 * (math.sin(self.background_timer * 3 + i) * 0.5 + 0.5))
            arcade.draw_circle_filled(sx, sy, 2, (255, 255, 200, alpha))

    def spawn_coins(self, num_coins=3):
        """Spawn new burgers at random locations"""
        for i in range(num_coins):
            # Create the burger instance
            burger = Collectable(scale=SPRITE_SCALING)

            # Position the burger randomly, but not too close to the player
            attempts = 0
            while attempts < 50:  # Prevent infinite loop
                burger.center_x = random.randrange(50, int(self.window.width) - 50)
                burger.center_y = random.randrange(50, int(self.window.height) - 50)
                
                # Check if burger is far enough from player
                distance = ((burger.center_x - self.player_sprite.center_x) ** 2 + 
                           (burger.center_y - self.player_sprite.center_y) ** 2) ** 0.5
                
                if distance > 100:  # At least 100 pixels away from player
                    break
                attempts += 1

            # Store original position for bouncing animation
            burger.original_y = burger.center_y

            # Add the burger to the lists
            self.coin_list.append(burger)

    def spawn_printers(self):
        """Spawn up to 5 printers from the top of the screen"""
        used_positions = []  # Keep track of used x positions
        
        # Spawn between 3 and 5 printers randomly
        num_printers = random.randint(3, 5)
        
        for i in range(num_printers):
            # Create a printer sprite scaled down to 32x32 pixels first
            printer = arcade.Sprite("WarioSprites/printer.png")
            
            # Step 1: Calculate base scale to make it 32x32 pixels (initial scale down)
            target_size = 32
            if printer.texture.width > 0:  # Avoid division by zero
                base_scale_factor = target_size / max(printer.texture.width, printer.texture.height)
            else:
                base_scale_factor = 0.1  # Fallback scale
            
            # Step 2: Apply random upscaling on top of the base scale
            random_upscale = random.uniform(0.8, 3.0)  # Random scale multiplier between 0.8x and 3.0x
            final_scale = base_scale_factor * random_upscale
            
            printer.scale = final_scale
            
            # Find a random x position that doesn't overlap with existing printers
            # Use actual window width for proper positioning in fullscreen
            actual_width = self.window.width
            attempts = 0
            while attempts < 50:  # Prevent infinite loop
                random_x = random.randrange(50, actual_width - 50)
                
                # Check if this position is too close to any existing position
                too_close = False
                for used_x in used_positions:
                    if abs(random_x - used_x) < 120:  # Minimum 120 pixels apart (increased for larger printers)
                        too_close = True
                        break
                
                # Also check if too close to player (avoid spawning directly above player)
                player_distance = abs(random_x - self.player_sprite.center_x)
                if player_distance < 150:  # Minimum 150 pixels away from player
                    too_close = True
                
                if not too_close:
                    used_positions.append(random_x)
                    break
                    
                attempts += 1
            
            # If we couldn't find a good position after 50 attempts, use a fallback
            if attempts >= 50:
                # Fallback to evenly spaced across actual window width
                actual_width = self.window.width
                spacing = (actual_width - 200) // num_printers  # Distribute evenly
                random_x = 100 + (i * spacing)
                used_positions.append(random_x)
            
            # Position the printer at the top of the screen
            printer.center_x = random_x
            # Use actual window height for proper positioning in fullscreen
            actual_height = self.window.height
            printer.center_y = actual_height + 100  # Start further above the screen for more reaction time
            
            # Calculate falling speed based on score (faster with more coins)
            base_speed = 1.5  # Reduced from 2 to 1.5 for gentler start
            speed_increase = self.score * 0.05  # Reduced from 0.1 to 0.05 for slower acceleration
            max_speed = 6  # Reduced maximum speed from 8 to 6
            printer.change_y = -min(base_speed + speed_increase, max_speed)
            
            # Add to the printer list
            self.printer_list.append(printer)

    def spawn_enemies(self):
        """Spawn enemies from left and right sides of screen"""
        # Calculate number of enemies based on score (gradually increasing)
        base_enemies = 2  # Start with minimum 2 enemies
        score_bonus = self.score // 5  # +1 enemy for every 5 points
        max_enemies = 8  # Cap at 8 enemies per spawn
        
        min_enemies = min(base_enemies + score_bonus, max_enemies)
        max_enemies_spawn = min(base_enemies + score_bonus + 2, max_enemies)
        
        num_enemies = random.randint(min_enemies, max_enemies_spawn)
        
        for i in range(num_enemies):
            # Random scale for enemy size variety
            enemy_scale = random.uniform(1.0, 2.0)
            
            # Randomly choose to spawn from left or right
            spawn_from_left = random.choice([True, False])
            
            if spawn_from_left:
                # Spawn from left side, moving right
                enemy = Enemy(scale=enemy_scale, direction=1, window_width=self.window.width)
                enemy.center_x = -30  # Start off left edge
            else:
                # Spawn from right side, moving left
                enemy = Enemy(scale=enemy_scale, direction=-1, window_width=self.window.width)
                enemy.center_x = self.window.width + 30  # Start off right edge
            
            # Random Y position (middle area of screen to avoid printers)
            enemy.center_y = random.randrange(100, self.window.height - 100)
            
            # Add to enemy list
            self.enemy_list.append(enemy)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.F11:
            # Toggle fullscreen with F11
            self.window.set_fullscreen(not self.window.fullscreen)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Update background animation timer
        self.background_timer += delta_time

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        # Update player animation
        self.update_player_animation(delta_time)

        # Keep player on screen using actual window size
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        elif self.player_sprite.right > self.window.width - 1:
            self.player_sprite.right = self.window.width - 1

        if self.player_sprite.bottom < 0:
            self.player_sprite.bottom = 0
        elif self.player_sprite.top > self.window.height - 1:
            self.player_sprite.top = self.window.height - 1

        # Update coin spawn timer
        self.coin_spawn_timer += delta_time
        
        # Spawn new coins every 5 seconds
        if self.coin_spawn_timer >= self.coin_spawn_interval:
            self.spawn_coins(3)  # Spawn 3 new coins
            self.coin_spawn_timer = 0.0  # Reset timer

        # Spawn printers when score reaches 5 (first time only)
        if self.score >= 5 and not self.printers_spawned:
            self.spawn_printers()
            self.printers_spawned = True
            self.printer_spawn_timer = 0.0  # Reset timer for recurring spawns
        
        # After first spawn, spawn new printers with decreasing intervals
        if self.printers_spawned:
            # Calculate dynamic spawn interval based on score (faster with more coins)
            base_interval = 6.0  # Base 6 seconds
            interval_decrease = self.score * 0.1  # 0.1 seconds less per coin
            min_interval = 3.0  # Minimum 3 seconds between spawns
            current_interval = max(base_interval - interval_decrease, min_interval)
            
            self.printer_spawn_timer += delta_time
            if self.printer_spawn_timer >= current_interval:
                self.spawn_printers()
                self.printer_spawn_timer = 0.0  # Reset timer

        # Enemy spawning system - start spawning after score 3
        if self.score >= 3:
            self.enemy_spawn_timer += delta_time
            
            # Calculate dynamic spawn interval (faster with higher score)
            base_interval = 3.0  # Base 3 seconds (reduced from 4)
            interval_decrease = self.score * 0.08  # 0.08 seconds less per point (increased from 0.05)
            min_interval = 1.5  # Minimum 1.5 seconds between spawns (reduced from 2)
            current_interval = max(base_interval - interval_decrease, min_interval)
            
            if self.enemy_spawn_timer >= current_interval:
                self.spawn_enemies()
                self.enemy_spawn_timer = 0.0  # Reset timer

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.player_list.update()
        self.coin_list.update()
        self.printer_list.update()
        self.enemy_list.update()

        # Remove printers that have fallen off the screen
        for printer in self.printer_list:
            if printer.bottom < -50:
                printer.remove_from_sprite_lists()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        # Loop through each colliding sprite, change it, and add to the score.
        for coin in hit_list:
            # Have we collected this?
            if not coin.changed:
                # Mark as collected and start collection animation
                coin.changed = True
                coin.collection_timer = 0.0  # Initialize collection timer
                self.score += 1
                
                # Make Wario fatter with each burger collected
                current_scale = self.player_sprite.scale
                if isinstance(current_scale, tuple):
                    # If scale is a tuple, increase both x and y scale
                    self.player_sprite.scale = (current_scale[0] + 0.1, current_scale[1] + 0.1)
                else:
                    # If scale is a float, just add to it
                    self.player_sprite.scale = current_scale + 0.1
                
                # Play collection sound
                if self.collect_sound:
                    arcade.play_sound(self.collect_sound)
                
                # Remove burger after collection animation completes
                # This will be handled by a timer or by checking if it's completely shrunk
                
        # Remove burgers that have completed their collection animation
        for coin in self.coin_list:
            if coin.changed and hasattr(coin, 'collection_timer') and coin.collection_timer > 1.0:
                coin.remove_from_sprite_lists()

        # Check for collision with printers (game over)
        printer_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.printer_list)
        if printer_hit_list:
            # Play die sound
            if self.die_sound:
                arcade.play_sound(self.die_sound)
            
            # Player hit a printer - game over!
            game_over_view = GameOverView(self.score)
            self.window.show_view(game_over_view)
            
        # Check for collision with enemies (game over)
        enemy_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)
        if enemy_hit_list:
            # Play die sound
            if self.die_sound:
                arcade.play_sound(self.die_sound)
            
            # Player hit an enemy - game over!
            game_over_view = GameOverView(self.score)
            self.window.show_view(game_over_view)


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, fullscreen=True, resizable=True)
    # Enable fullscreen toggle with F11
    window.set_fullscreen(True)

    # Show the start screen first
    start_view = StartView()
    window.show_view(start_view)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()