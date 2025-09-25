import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Arcade Scene Example"

class MyScene(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        arcade.start_render()
        # Draw ground
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 100, 0, arcade.color.DARK_SPRING_GREEN)
        # Draw sun
        arcade.draw_circle_filled(700, 500, 50, arcade.color.YELLOW)
        # Draw a tree
        arcade.draw_rectangle_filled(150, 130, 20, 60, arcade.color.BROWN)
        arcade.draw_circle_filled(150, 170, 40, arcade.color.DARK_GREEN)
        # Draw a house
        arcade.draw_rectangle_filled(400, 150, 120, 80, arcade.color.BRICK_RED)
        arcade.draw_triangle_filled(340, 190, 460, 190, 400, 250, arcade.color.DARK_BROWN)
        arcade.draw_rectangle_filled(400, 140, 30, 40, arcade.color.LIGHT_GRAY)

def main():
    window = MyScene()
    arcade.run()

if __name__ == "__main__":
    main()