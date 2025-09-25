WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Arcade Test - Wario on Map"

# testing
class Player(arcade.Sprite):
    def __init__(self, texture_list: list[arcade.Texture]):
        super().__init__(texture_list[0])
        self.time_elapsed = 0
        self.textures = texture_list

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.time_elapsed += delta_time

        if self.time_elapsed > 0.1:
 
            if self.cur_texture_index < len(self.textures) :
                self.set_texture(self.cur_texture_index)
                self.cur_texture_index += 1
            
            self.time_elapsed = 0
                

        if self.cur_texture_index == 10:
            self.cur_texture_index = 0

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        # Sprite lists
        self.sprites = arcade.SpriteList()
        self.platforms = arcade.SpriteList()

        # testing
        self.sprites_list = arcade.SpriteList()
        warioSheet = arcade.load_spritesheet("WarioSprites\WarioSpritesAll.png")
        texture_list = warioSheet.get_texture_grid(size=(30,50), columns=10, count=10)
        self.player = Player(texture_list)
        self.player.position = 640, 360
        self.sprites_list.append(self.player)


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
        self.sprites_list.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.sprites_list.update()

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
