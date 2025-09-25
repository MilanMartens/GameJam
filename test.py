import arcade
from pathlib import Path

window = arcade.Window(title="Arcade Window")
window.center_window()

assets_path = Path().absolute().resolve() / Path("assets")
arcade.resources.add_resource_handle("my-assets", assets_path)

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.level1 = arcade.load_tilemap(":my-assets:maps/level1/map1.tmx")

        # self.player_list = arcade.SpriteList()
        # self.player_list.append()

    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()
        self.level1.sprite_lists["ground"].draw()
        

game = GameView()
window.show_view(game)
arcade.run()