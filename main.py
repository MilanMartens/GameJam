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
        burger_texture = arcade.load_texture("WarioSprites/burger1.png")
        
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


class StartView(arcade.View):
    """Start screen with titlescreen image"""
    
    def __init__(self):
        super().__init__()
        self.background_color = (0, 16, 56)  # #001038
        
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
            
        # Draw highscore in top-right corner
        if self.highscore > 0:
            arcade.draw_text(
                f"High Score: {self.highscore}",
                self.window.width - 20,
                self.window.height - 40,
                arcade.color.YELLOW,
                font_size=24,
                anchor_x="right",
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
            self.collect_sound = arcade.load_sound(":resources:sounds/coin1.wav")
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
        """Setup Wario animations from spritesheet"""
        # Load the spritesheet
        spritesheet = arcade.load_texture("WarioSprites/WarioSpritesAll.png")
        
        # Create idle animation (using just one frame for now)
        idle_texture_list = []
        # Extract frame from spritesheet - assuming it's the first frame
        # You may need to adjust these coordinates based on the actual spritesheet layout
        idle_frame = spritesheet.crop(0, 0, 32, 32)  # Adjust size as needed
        idle_texture_list.append(idle_frame)
        
        # Create walking animation frames
        walking_texture_list = []
        # Extract multiple frames for walking animation
        # Assuming frames are 32x32 pixels and arranged horizontally
        for i in range(4):  # 4 walking frames
            frame = spritesheet.crop(i * 32, 0, 32, 32)
            walking_texture_list.append(frame)
        
        # Set up animations
        self.player_sprite.idle_texture_pair = idle_texture_list
        self.player_sprite.walk_textures = walking_texture_list
        
        # Set initial texture
        self.player_sprite.texture = idle_texture_list[0]
        
        # Animation variables
        self.player_sprite.cur_texture = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.2  # Change frame every 0.2 seconds

    def update_player_animation(self, delta_time):
        """Update Wario animation based on movement"""
        self.animation_timer += delta_time
        
        # Check if player is moving
        is_moving = (self.player_sprite.change_x != 0 or self.player_sprite.change_y != 0)
        
        if is_moving:
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
        # Get current window dimensions for dynamic scaling
        width = self.window.width
        height = self.window.height
        
        # Simple gradient background - reduced from 20 to 10 rectangles for better performance
        for i in range(10):
            y_pos = (height / 10) * i
            color_intensity = int(30 + (i * 12))  # Gradually lighter
            
            arcade.draw_lrbt_rectangle_filled(
                0, width, y_pos, y_pos + (height / 10),
                (color_intensity, color_intensity + 40, color_intensity, 255)
            )
        
        # Reduced floating decorations - only 4 instead of 8
        for i in range(4):
            base_x = (width / 4) * i + 100
            base_y = height * 0.8 + math.sin(self.background_timer * 0.5 + i) * 20
            
            # Single cloud circle instead of 3 for performance
            arcade.draw_circle_filled(
                base_x,
                base_y,
                30,
                (255, 255, 255, 20)  # Semi-transparent white
            )
        
        # Reduced twinkling stars - only 8 instead of 15
        for i in range(8):
            star_x = (width / 8) * i + 50
            star_y = height * 0.9 + math.sin(self.background_timer * 2 + i) * 15
            
            # Simpler twinkling effect
            twinkle = math.sin(self.background_timer * 2 + i) * 0.5 + 0.5
            star_alpha = int(80 + twinkle * 100)
            
            arcade.draw_circle_filled(
                star_x, star_y, 2,
                (255, 255, 200, star_alpha)
            )

    def spawn_coins(self, num_coins=3):
        """Spawn new burgers at random locations"""
        for i in range(num_coins):
            # Create the burger instance
            burger = Collectable(scale=SPRITE_SCALING)

            # Position the burger randomly, but not too close to the player
            attempts = 0
            while attempts < 50:  # Prevent infinite loop
                burger.center_x = random.randrange(50, WINDOW_WIDTH - 50)
                burger.center_y = random.randrange(50, WINDOW_HEIGHT - 50)
                
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
            # Create a printer sprite using the custom printer texture
            printer = arcade.Sprite("WarioSprites/printer.png", scale=1.5)
            
            # Find a random x position that doesn't overlap with existing printers
            # Use actual window width for proper positioning in fullscreen
            actual_width = self.window.width
            attempts = 0
            while attempts < 50:  # Prevent infinite loop
                random_x = random.randrange(50, actual_width - 50)
                
                # Check if this position is too close to any existing position
                too_close = False
                for used_x in used_positions:
                    if abs(random_x - used_x) < 80:  # Minimum 80 pixels apart
                        too_close = True
                        break
                
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
            printer.center_y = actual_height + 20  # Start above the screen (y=0 is bottom)
            
            # Calculate falling speed based on score (faster with more coins)
            base_speed = 2
            speed_increase = self.score * 0.1  # 0.1 speed increase per coin
            max_speed = 8  # Maximum falling speed
            printer.change_y = -min(base_speed + speed_increase, max_speed)
            
            # Add to the printer list
            self.printer_list.append(printer)

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

        # Keep player on screen
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        elif self.player_sprite.right > WINDOW_WIDTH - 1:
            self.player_sprite.right = WINDOW_WIDTH - 1

        if self.player_sprite.bottom < 0:
            self.player_sprite.bottom = 0
        elif self.player_sprite.top > WINDOW_HEIGHT - 1:
            self.player_sprite.top = WINDOW_HEIGHT - 1

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

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.player_list.update()
        self.coin_list.update()
        self.printer_list.update()

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


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, fullscreen=False, resizable=True)
    
    # Enable fullscreen toggle with F11
    window.set_fullscreen(False)

    # Show the start screen first
    start_view = StartView()
    window.show_view(start_view)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()