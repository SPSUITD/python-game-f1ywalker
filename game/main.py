"""
Platformer Game
"""
import arcade
import math
import time
# Constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 960
SCREEN_TITLE = "Platformer"


# Constants used to scale our sprites from their original size

#Size
CHARACTER_SCALING = 0.8
TILE_SCALING = 1

#Player movement settings
JUMP_MAX_HEIGHT = 100
PLAYER_X_SPEED = 5
PLAYER_Y_SPEED = 5
MAX_FALL_SPEED = 20
GRAVITY = 0.35

#Animations speed
PLAYER_SPRITE_IMAGE_CHANGE_SPEED = 50
PLAYER_SPRITE_DASH_ANIMATION_SPEED = 20

#Dash settings
DASH_SPEED = 15
DASH_DURATION = 0.2
DASH_COOLDOWN = 1

#Spawn Points
PLAYER_START_X_1 = 64
PLAYER_START_Y_1 = 200
PLAYER_START_X_2 = 64
PLAYER_START_Y_2 = 1100
NUMBER_OF_LEVELS = 2

class MyGame(arcade.Window):
    """
    Main application class.
    """
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        #Map_Settings
        self.test = 0
        self.tile_map = None
        self.map_height = 0
        self.map_width = 0

        #Lists
        self.wall_list = None
        self.player_list = None
        self.player_sprite = None

        #Camera
        self.camera = None
        self.gui_camera = None
        self.camera_max = 0
        self.score = 0

        self.player_jump = False
        self.jump_start = 0

        #Button_State
        self.key_right_pressed = False
        self.key_left_pressed = False
        self.key_space_pressed = False
        self.last_button_pressed = None
        self.last_button_x = None

        #Collision
        self.collide = False
        self.collide_left = False
        self.collide_right = False
        self.collide_top = False
        self.collide_coin = False

        #Speed
        self.player_dx = PLAYER_X_SPEED
        self.fall_speed = PLAYER_Y_SPEED
        self.jump_speed = PLAYER_Y_SPEED
        self.fall_speed = 0

        #Dash_Settings
        self.dashing = False
        self.dash_end_time = 0
        self.last_dash_direction = None
        self.dash_cooldown = DASH_COOLDOWN  # Cooldown time in seconds
        self.last_dash_time = -self.dash_cooldown  # Initialize to allow immediate dash at start
        self.dash_frame_index = 0
        self.dash_frame_timer = 0
        self.dash_frame_duration = 0.05  # Duration to display each dash frame (in seconds)

        #Interface
        self.total_time = 0.0
        self.total_time_print = ""

        #Animations
        self.player_sprite_images_right = []
        self.player_sprite_images_left = []
        self.player_sprite_images_dash_right = []
        self.player_sprite_images_dash_left = []
        self.player_sprite_images_up_right = []
        self.player_sprite_images_up_left = []
        self.player_sprite_images_down_right = []
        self.player_sprite_images_down_left = []
        self.player_sprite_idle = []

        #Jump_Settings
        self.jump_frame_index = 0
        self.jump_frame_timer = 0
        self.jump_frame_duration = 0.1

        #Level_Settings
        self.end_of_map = 0
        self.level = 1

        self.coins_list = []

        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)


    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)
        map_name = f"map/map{self.level}.json"
        layer_options = {
            "platforms01": {
                "use_spatial_hash": True,
            },
            "coins": {
                "use_spatial_hash": True,
            },
            "honey": {
                "use_spatial_hash": True,
            },
            "spikes": {
                "use_spatial_hash": True,
            }
        }
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.end_of_map = self.tile_map.width * self.tile_map.tile_width

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        # Set up the player, specifically placing it at these coordinates.
        image_source = "img/bear/walk_cycle/Bear_Walk_Cycle1.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        if self.level == 1:
            self.player_sprite.center_x = PLAYER_START_X_1
            self.player_sprite.center_y = PLAYER_START_Y_1
        if self.level == 2:
            self.player_sprite.center_x = PLAYER_START_X_2
            self.player_sprite.center_y = PLAYER_START_Y_2

        self.player_list.append(self.player_sprite)
        self.jump_start = self.player_sprite.center_y


        self.score = 0


        for i in range(1, 5):
            self.player_sprite_images_right.append(arcade.load_texture(f"img/bear/walk_cycle/Bear_Walk_Cycle{i}.png"))
        for i in range(4, 0, -1):
            self.player_sprite_images_left.append(
                arcade.load_texture(f"img/bear/walk_cycle/Bear_Walk_Cycle{i}.png", flipped_horizontally=True))
        for i in range(1, 5):
            self.player_sprite_images_dash_left.append(arcade.load_texture(f"img/bear/dash/bear_dash{i}.png"))
        for i in range(4, 0, -1):
            self.player_sprite_images_dash_right.append(
                arcade.load_texture(f"img/bear/dash/bear_dash{i}.png", flipped_horizontally=True))
        for i in range(1, 4):
            self.player_sprite_images_up_right.append(arcade.load_texture(f"img/bear/up/bear_jump{i}.png"))
        for i in range(3, 0, -1):
            self.player_sprite_images_up_left.append(
                arcade.load_texture(f"img/bear/up/bear_jump{i}.png", flipped_horizontally=True))
        for i in range(1, 3):
            self.player_sprite_images_down_right.append(arcade.load_texture(f"img/bear/fall/bear_fall{i}.png"))
        for i in range(2, 0, -1):
            self.player_sprite_images_down_left.append(
                arcade.load_texture(f"img/bear/fall/bear_fall{i}.png", flipped_horizontally=True))

    def on_draw(self):
        """Render the screen."""
        # Clear the screen to the background color
        self.clear()

        # Activate our Camera
        self.camera.use()

        # Draw our sprites
        self.scene.draw()
        self.player_list.draw()

        self.gui_camera.use()

        arcade.draw_text(
            str(f"Время : {self.total_time_print}"),
            10,
            10,
            arcade.csscolor.WHITE,
            18,
        )
        score_text = f"Счёт: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            50,
            arcade.csscolor.WHITE,
            18,
        )


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            self.last_button_pressed = "Up"
            if self.collide:
                self.player_jump = True
                self.jump_start = self.player_sprite.center_y
                self.fall_speed = PLAYER_Y_SPEED  # Reset fall speed on jump

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.center_y +=15

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.key_left_pressed = True
            self.last_button_x = "Left"

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.key_right_pressed = True
            self.last_button_x = "Right"

        elif key == arcade.key.SPACE:
            self.key_space_pressed = True
            self.start_dash()


    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.key_left_pressed = False
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.key_right_pressed = False

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        self.map_height = self.tile_map.height * self.tile_map.tile_height
        self.map_width = self.tile_map.width * self.tile_map.tile_width

        self.test = screen_center_y
        if screen_center_x + self.camera.viewport_width > self.map_width:
            screen_center_x = self.map_width - self.camera.viewport_width

        if screen_center_y + self.camera.viewport_height > self.map_height:
            screen_center_y = self.map_height - self.camera.viewport_height

        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def player_movement(self):
        current_time = time.time()
        # Fix in the player_movement method
        if self.dashing:
            if current_time > self.dash_end_time:
                self.end_dash()
            else:
                # Update dash animation frame based on the timer
                if current_time - self.dash_frame_timer > self.dash_frame_duration:
                    self.dash_frame_timer = current_time
                    self.dash_frame_index = (self.dash_frame_index + 1) % 4  # Loop through dash frames

                    if self.last_dash_direction == "left":
                        self.player_sprite.texture = self.player_sprite_images_dash_left[self.dash_frame_index]
                    elif self.last_dash_direction == "right":
                        self.player_sprite.texture = self.player_sprite_images_dash_right[self.dash_frame_index]

                if self.last_dash_direction == "left":
                    self.player_sprite.center_x -= DASH_SPEED
                    if self.collide_left:  # Check the boolean value directly
                        self.player_sprite.center_x += DASH_SPEED  # Move back if collision detected
                        self.end_dash()
                elif self.last_dash_direction == "right":
                    self.player_sprite.center_x += DASH_SPEED
                    if self.collide_right:  # Check the boolean value directly
                        self.player_sprite.center_x -= DASH_SPEED  # Move back if collision detected
                        self.end_dash()
                return  # Exit early during dash

        # When player hits the collision
        if self.collide:
            self.player_dy = 0
            self.fall_speed = 0  # Reset fall speed on collision
        else:
            self.player_dy = PLAYER_Y_SPEED + self.fall_speed

        if self.key_left_pressed and not self.collide_left:
            self.player_sprite.center_x -= self.player_dx
            self.player_sprite.texture = self.player_sprite_images_left[
                int(self.player_sprite.center_x / PLAYER_SPRITE_IMAGE_CHANGE_SPEED) % 4]

        if self.key_right_pressed and not self.collide_right:
            self.player_sprite.center_x += self.player_dx
            self.player_sprite.texture = self.player_sprite_images_right[
                int(self.player_sprite.center_x / PLAYER_SPRITE_IMAGE_CHANGE_SPEED) % 4]

        if self.player_jump:
            if self.last_button_x == "Right":
                if current_time - self.jump_frame_timer > self.jump_frame_duration:
                    self.jump_frame_timer = current_time
                    self.jump_frame_index = (self.jump_frame_index + 1) % 3  # Loop through jump frames
                self.player_sprite.texture = self.player_sprite_images_up_right[self.jump_frame_index]
            distance_covered = self.player_sprite.center_y - self.jump_start

            if self.last_button_x == "Left":
                if current_time - self.jump_frame_timer > self.jump_frame_duration:
                    self.jump_frame_timer = current_time
                    self.jump_frame_index = (self.jump_frame_index + 1) % 3  # Loop through jump frames
                self.player_sprite.texture = self.player_sprite_images_up_left[self.jump_frame_index]
            distance_covered = self.player_sprite.center_y - self.jump_start
            distance_left = JUMP_MAX_HEIGHT - distance_covered
            jump_speed_ratio = max(distance_left / JUMP_MAX_HEIGHT, 0.1)  # Minimum ratio to ensure some speed
            adjusted_jump_speed = self.jump_speed * jump_speed_ratio * GRAVITY
            self.player_sprite.center_y += adjusted_jump_speed

            self.player_sprite.center_y += self.player_dy
            if self.player_sprite.center_y >= self.jump_start + JUMP_MAX_HEIGHT:
                self.player_jump = False
                self.fall_speed = adjusted_jump_speed  # Set fall speed to the speed at the highest point
        else:
            if self.last_button_x == "Left":
                self.player_sprite.texture = self.player_sprite_images_left[
                    int(self.player_sprite.center_x / PLAYER_SPRITE_IMAGE_CHANGE_SPEED) % 4]
            elif self.last_button_x == "Right":
                self.player_sprite.texture = self.player_sprite_images_right[
                    int(self.player_sprite.center_x / PLAYER_SPRITE_IMAGE_CHANGE_SPEED) % 4]

            self.player_sprite.center_y -= self.player_dy

        if not self.collide and not self.player_jump:
            self.fall_speed = min(self.fall_speed + GRAVITY, MAX_FALL_SPEED)  # Increase fall speed over time

    def start_dash(self):
        current_time = time.time()

        if current_time - self.last_dash_time >= self.dash_cooldown:
            self.dashing = True
            self.dash_end_time = current_time + DASH_DURATION
            self.last_dash_time = current_time  # Update last dash time
            self.dash_frame_index = 0  # Reset dash frame index
            self.dash_frame_timer = current_time  # Reset dash frame timer

            if self.last_button_x == "Left":
                self.last_dash_direction = "left"
            elif self.last_button_x == "Right":
                self.last_dash_direction = "right"

            # Set the initial dash texture
            if self.last_dash_direction == "left":
                self.player_sprite.texture = self.player_sprite_images_dash_left[self.dash_frame_index]
            elif self.last_dash_direction == "right":
                self.player_sprite.texture = self.player_sprite_images_dash_right[self.dash_frame_index]

    def end_dash(self):
        self.dashing = False
        # Reset to the appropriate walking texture
        if self.last_button_x == "Left":
            self.player_sprite.texture = self.player_sprite_images_left[
                int(self.player_sprite.center_x / PLAYER_SPRITE_IMAGE_CHANGE_SPEED) % 4]
        elif self.last_button_x == "Right":
            self.player_sprite.texture = self.player_sprite_images_right[
                int(self.player_sprite.center_x / PLAYER_SPRITE_IMAGE_CHANGE_SPEED) % 4]

    def calculate_collision(self):
        self.collide_coin = False
        self.collide = False
        self.collide_left = False
        self.collide_right = False
        self.collide_top = False
        for block in self.scene["platforms01"]:
            if (self.player_sprite.center_x + self.player_sprite.width / 5 > block.center_x - block.width / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 5 < block.center_x + block.width / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 2 <= block.center_y + block.height / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 2 >= block.center_y - block.height / 2):
                self.player_sprite.center_y = block.center_y + block.height / 2 + self.player_sprite.height / 2
                self.collide = True
            if (self.player_sprite.center_y + self.player_sprite.height / 4 >= block.center_y - block.height / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 4 <= block.center_y + block.height / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 4 <= block.center_x + block.width / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 4 >= block.center_x - block.width / 2):
                self.player_sprite.center_x = block.center_x + block.width / 2 + self.player_sprite.width / 4
                self.collide_left = True
            if (self.player_sprite.center_y + self.player_sprite.height / 4 > block.center_y - block.height / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 4 < block.center_y + block.height / 2
                    and self.player_sprite.center_x + self.player_sprite.width / 4 >= block.center_x - block.width / 2
                    and self.player_sprite.center_x + self.player_sprite.width / 4 <= block.center_x + block.width / 2):
                self.player_sprite.center_x = block.center_x - block.width / 2 - self.player_sprite.width / 4
                self.collide_right = True
            if (self.player_sprite.center_x + self.player_sprite.width / 5 > block.center_x - block.width / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 5 < block.center_x + block.width / 2
                    and self.player_sprite.center_y + self.player_sprite.height / 2 >= block.center_y - block.height / 2
                    and self.player_sprite.center_y + self.player_sprite.height / 2 <= block.center_y + block.height / 2):
                self.player_sprite.center_y = block.center_y - block.height / 2 - self.player_sprite.height / 2
                self.player_jump = False
                self.collide_top = True
        for block in self.scene["spikes"]:
            if (self.player_sprite.center_x + self.player_sprite.width / 5 > block.center_x - block.width / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 5 < block.center_x + block.width / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 2 <= block.center_y + block.height / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 2 >= block.center_y - block.height / 2):
                self.player_sprite.center_y = block.center_y + block.height / 2 + self.player_sprite.height / 2
                self.collide = True
                if self.level == 1:
                    self.player_sprite.center_x = PLAYER_START_X_1
                    self.player_sprite.center_y = PLAYER_START_Y_1
                if self.level == 2:
                    self.player_sprite.center_x = PLAYER_START_X_2
                    self.player_sprite.center_y = PLAYER_START_Y_2
        for block in self.scene["coins"]:
            if (self.player_sprite.center_x + self.player_sprite.width / 5 > block.center_x - block.width / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 5 < block.center_x + block.width / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 2 <= block.center_y + block.height / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 2 >= block.center_y - block.height / 2):
                self.collide_coin = True
                block.remove_from_sprite_lists()
                self.score += 1
            if (self.player_sprite.center_y + self.player_sprite.height / 4 >= block.center_y - block.height / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 4 <= block.center_y + block.height / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 4 <= block.center_x + block.width / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 4 >= block.center_x - block.width / 2):
                self.collide_coin = True
                block.remove_from_sprite_lists()
                self.score += 1
            if (self.player_sprite.center_y + self.player_sprite.height / 4 > block.center_y - block.height / 2
                    and self.player_sprite.center_y - self.player_sprite.height / 4 < block.center_y + block.height / 2
                    and self.player_sprite.center_x + self.player_sprite.width / 4 >= block.center_x - block.width / 2
                    and self.player_sprite.center_x + self.player_sprite.width / 4 <= block.center_x + block.width / 2):
                self.collide_coin = True
                block.remove_from_sprite_lists()
                self.score += 1
            if (self.player_sprite.center_x + self.player_sprite.width / 5 > block.center_x - block.width / 2
                    and self.player_sprite.center_x - self.player_sprite.width / 5 < block.center_x + block.width / 2
                    and self.player_sprite.center_y + self.player_sprite.height / 2 >= block.center_y - block.height / 2
                    and self.player_sprite.center_y + self.player_sprite.height / 2 <= block.center_y + block.height / 2):
                self.collide_coin = True
                block.remove_from_sprite_lists()
                self.score += 1
        if self.level == 2:
            for block in self.scene["honey"]:
                if block.center_x + block.width / 2 >= self.player_sprite.center_x >= block.center_x - block.width / 2 \
                        and block.center_y + block.height / 2 >= self.player_sprite.center_y >= block.center_y - block.height / 2:
                    arcade.exit()

    def on_update(self, delta_time):
        self.center_camera_to_player()
        self.player_movement()

        if self.player_jump:
            self.collide = False
        else:
            self.calculate_collision()

        self.total_time += delta_time

        ms, sec = math.modf(self.total_time)

        minutes = int(sec) // 60

        seconds = int(sec) % 60

        msec = int(ms * 100)

        self.total_time_print = f"{minutes:02d}:{seconds:02d}:{msec:02d}"

        if self.level == 1:
            if self.player_sprite.center_y < -50:
                self.player_sprite.center_x = PLAYER_START_X_1
                self.player_sprite.center_y = PLAYER_START_Y_1
        if self.level == 2:
            if self.player_sprite.center_y < -50:
                self.player_sprite.center_x = PLAYER_START_X_2
                self.player_sprite.center_y = PLAYER_START_Y_2

        if self.player_sprite.center_x >= self.end_of_map:
            if self.level < NUMBER_OF_LEVELS:
                self.level += 1
            else:
                arcade.exit()

            self.setup()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()