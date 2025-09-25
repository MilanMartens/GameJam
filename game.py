import arcade
from arcade.types import Color

# --- Constants ---
WINDOW_TITLE = "Platformer"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Scaling
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Camera
FOLLOW_DECAY_CONST = 0.3  # get within 1% of the target position within 2 seconds

# --------------------------
# Custom animated player class
# --------------------------
class Player(arcade.Sprite):
    def __init__(self, textures, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textures = textures
        self.current_texture_index = 0
        self.time_elapsed = 0
        self.texture = self.textures[self.current_texture_index]

    def update_animation(self, delta_time: float = 1/60):
        self.time_elapsed += delta_time
        if self.time_elapsed > 0.1:
            self.current_texture_index = (self.current_texture_index + 1) % len(self.textures)
            self.texture = self.textures[self.current_texture_index]
            self.time_elapsed = 0

# --------------------------
# Main Game class
# --------------------------
class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__()

        # Camera setup
        self.camera_sprites = arcade.Camera2D()
        self.camera_bounds = self.window.rect
        self.camera_gui = arcade.Camera2D()

        # Scene setup
        self.scene = self.create_scene()

        # Player animation frames (built-in sheet, 8 frames)
        SPRITE_SHEET_PATH = "WarioSprites/WarioSpritesRun.png"
        TILE_WIDTH, TILE_HEIGHT, NUM_FRAMES = 64, 128, 8   # <-- update if your frames are different

        self.player_textures = [
            arcade.load_texture(
                SPRITE_SHEET_PATH,
                i * TILE_WIDTH,       # x offset
                0,                    # y offset
                TILE_WIDTH,           # width
                TILE_HEIGHT           # height
            )
            for i in range(NUM_FRAMES)
        ]




        # Animated player sprite
        self.player_sprite = Player(self.player_textures, scale=CHARACTER_SCALING)
        self.player_sprite.center_x, self.player_sprite.center_y = 128, 128

        # Physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

        self.score = 0
        self.left_key_down = False
        self.right_key_down = False

        self.score_display = arcade.Text(
            "Score: 0",
            x=10,
            y=10,
            color=arcade.csscolor.WHITE,
            font_size=18,
        )

    def create_scene(self) -> arcade.Scene:
        """Load the tilemap and create the scene object."""
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }
        tile_map = arcade.load_tilemap(
            ":resources:tiled_maps/map.json",
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        if tile_map.background_color:
            self.window.background_color = Color.from_iterable(tile_map.background_color)

        self.camera_bounds = arcade.LRBT(
            self.window.width/2.0,
            tile_map.width * GRID_PIXEL_SIZE - self.window.width/2.0,
            self.window.height/2.0,
            tile_map.height * GRID_PIXEL_SIZE
        )
        return arcade.Scene.from_tilemap(tile_map)

    def reset(self):
        """Reset the game to the initial state."""
        self.score = 0
        self.scene = self.create_scene()
        self.player_sprite.center_x, self.player_sprite.center_y = 128, 128
        self.scene.add_sprite("Player", self.player_sprite)

    def on_draw(self):
        """Render the screen."""
        self.clear()
        with self.camera_sprites.activate():
            self.scene.draw()
        with self.camera_gui.activate():
            self.score_display.text = f"Score: {self.score}"
            self.score_display.draw()

    def update_player_speed(self):
        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        if self.left_key_down and not self.right_key_down:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_key_down and not self.left_key_down:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
            self.update_player_speed()

    def center_camera_to_player(self):
        self.camera_sprites.position = arcade.math.smerp_2d(
            self.camera_sprites.position,
            self.player_sprite.position,
            self.window.delta_time,
            FOLLOW_DECAY_CONST,
        )
        self.camera_sprites.view_data.position = arcade.camera.grips.constrain_xy(
            self.camera_sprites.view_data, self.camera_bounds
        )

    def on_update(self, delta_time: float):
        """Movement and game logic"""
        self.physics_engine.update()
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1
        self.center_camera_to_player()
        self.player_sprite.update_animation(delta_time)

    def on_resize(self, width: int, height: int):
        """Resize window"""
        super().on_resize(width, height)
        self.camera_sprites.match_window()
        self.camera_gui.match_window(position=True)

# --------------------------
# Main function
# --------------------------
def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()
    game.reset()
    window.show_view(game)
    arcade.run()

if __name__ == "__main__":
    main()
