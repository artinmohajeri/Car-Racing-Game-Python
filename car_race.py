import pygame, time, math
from utils import scale_image, draw, blit_rotate_center,move_player, finish_line_colide_handle, blit_text_center, BaseCar, GameInfo
pygame.font.init()


# loading game images ↓↓↓
GRASS = scale_image(pygame.image.load("./img/grass.jpg"),2)
TRACK = pygame.image.load("./img/track.png")
TRACK_BORDER = pygame.image.load("./img/track-border.png")
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH_LINE = pygame.image.load("./img/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH_LINE)
LAMBORGHINI = scale_image(pygame.image.load("./img/lamborghini.png"),0.6)
CORVETTE = scale_image(pygame.image.load("./img/corvette.png"),0.6)
FINISH_POSITION = (255, 250)

# displaying the window ↓↓↓
WIN_PADDING = 300
WIDTH, HEIGHT = TRACK.get_width() + WIN_PADDING, TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

# the location that the computer car should go()
COMPUTER_CAR_PATH = [(303, 93), (251, 55), (199, 111), (200, 409), (396, 617), (472, 608), (489, 540), (520, 423), (592, 396), (668, 449), (657, 582), (722, 636), (771, 601), (767, 311), (517, 302), (514, 252), (548, 211), (754, 219), (770, 180), (759, 76), (406, 68), (389, 145), (381, 335), (335, 324), (303, 257)]

# declaring the font ↓↓↓
FONT = pygame.font.SysFont("comicsans",44)

# list of images and their positions ↓↓↓
images = [
    (GRASS,(0,0)),
    (TRACK,(WIN_PADDING/2,0)),
    (FINISH_LINE,(FINISH_POSITION)),
    (TRACK_BORDER,(WIN_PADDING/2,0)),
    ]

class ComputerCar(BaseCar):
    IMG = CORVETTE
    START_POSITION = (308,200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    # def draw_points(self, win):
        # for point in self.path:
            # pygame.draw.circle(win, (255,0,0), point, 5)
    # def draw(self, win):
    #     super().draw(win)
    #     self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_difference = target_x - self.x
        y_difference = target_y - self.y
        if y_difference == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_difference/y_difference)
        if target_y > self.y:
            desired_radian_angle += math.pi
        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >=180:
            difference_in_angle -= 360
        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point +=1

    def move(self):
        # make sure not trying to move to a point that doesnt exit
        if self.current_point >= len(self.path):
            return
        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0


class PlayerCar(BaseCar):
    IMG = LAMBORGHINI
    START_POSITION = (275, 200)
    def reduce_speed(self):
        # make sure we dont move backward. just stop
        self.vel = max(self.vel - self.acceleration/2,0)
        self.move()

    def collide_stop(self):
        self.vel = -self.vel/2
        self.move()


# making a player object instance ↓↓↓
player_car = PlayerCar(4, 4)
computer_car = ComputerCar(2,5,COMPUTER_CAR_PATH)

# declaring speed of game running(frames per seconds) ↓↓↓
FPS = 60
run = True
clock = pygame.time.Clock()


game_info = GameInfo()

# create the main event loop ↓↓↓
while run:
    clock.tick(FPS)
    draw(WIN, images, player_car, computer_car, game_info, FONT, HEIGHT)

    while not game_info.started:
        pygame.display.update()
        blit_text_center(WIN, FONT,f"Press any key to start level {game_info.level}")
        for event in pygame.event.get():
            # close the window if pressing close button
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                break
            if event.type == pygame.KEYDOWN:
                game_info.start_level()


    pygame.display.update()
    for event in pygame.event.get():
        # close the window if pressing close button
        if event.type == pygame.QUIT:
            run = False
            break
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     position = pygame.mouse.get_pos()
        #     computer_car.path.append(position)
    move_player(player_car)
    computer_car.move()

    # make sure when we hit the border. we cant go further.
    if player_car.collide(TRACK_BORDER_MASK):
        player_car.collide_stop()

    finish_line_colide_handle(player_car, computer_car, FINISH_MASK, FINISH_POSITION, game_info, WIN, FONT, run)

    if game_info.game_finished():
        blit_text_center(WIN,FONT,"You WIN!")
        pygame.display.update()
        pygame.time.wait(3000)
        game_info.reset()
        computer_car.reset()
        player_car.reset()

# print(computer_car.path)
pygame.quit()
