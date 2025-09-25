import arcade

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Arcade Test - Wario on Map"


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        # Sprite lists
        self.sprites = arcade.SpriteList()
        self.platforms = arcade.SpriteList()

        # Wario sprite
        player = arcade.Sprite("WarioSprites/Run1Wario.png", scale=1)
        player.center_x = 100
        player.center_y = 160  # Slightly above ground
        self.sprites.append(player)
        self.player = player  # so you can move/collide

        # Ground tiles
        for x in range(0, WINDOW_WIDTH, 64):
            tile = arcade.Sprite(":resources:images/tiles/stoneMid.png", scale=0.5)
            tile.center_x = x + 32  # tile width / 2
            tile.center_y = 32  # on ground
            self.platforms.append(tile)

        # A floating platform
        for x in range(300, 500, 64):
            tile = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=0.5)
            tile.center_x = x + 32
            tile.center_y = 200
            self.platforms.append(tile)

        # Simple physics
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.platforms, gravity_constant=0.7)

    def on_draw(self):
        self.clear()
        self.platforms.draw()
        self.sprites.draw()
        arcade.draw_text("Wario on a simple map!", 180, 570, arcade.color.WHITE, 18)

    def on_update(self, delta_time):
        self.physics_engine.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = -4
        elif key == arcade.key.RIGHT:
            self.player.change_x = 4
        elif key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player.change_y = 13

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0


def main():
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
