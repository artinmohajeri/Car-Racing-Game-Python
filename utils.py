import pygame, math, time

# image change function ↓↓↓
def scale_image(img, factor):
    size = round(img.get_width() * factor),round(img.get_height() * factor)
    return pygame.transform.scale(img,size)


# display images on screen ↓↓↓
def draw(win, imgs, player_car, computer_car, game_info, FONT, HEIGHT):
    for img, position in imgs:
        win.blit(img, position)

    level_text = FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 100))

    time_text = FONT.render(f"Time {abs(round(game_info.get_level_time()))} s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 55))

    vel_text = FONT.render(f"Speed {round(player_car.vel)} px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    player_car.draw(win) 
    computer_car.draw(win) 


# car rotation ↓↓↓
def blit_rotate_center(win, img, top_left, angle):
    rotated_img = pygame.transform.rotate(img, angle)

    # changing the rotating origin from topleft to center ↓↓↓
    new_rect = rotated_img.get_rect(center=img.get_rect(topleft = top_left).center)
    win.blit(rotated_img, new_rect.topleft)

def move_player(player):
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_a]:
        player.rotate(left=True)
    if keys[pygame.K_d]:
        player.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player.move_forward()
    if keys[pygame.K_s]:
        player.move_backward()
        moved = True
    if not moved:
        player.reduce_speed()



class BaseCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POSITION
        self.acceleration = 0.1
    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel
    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
    def move_forward(self):
        # make sure we dont go faster that the max_velocity
        self.vel = min(self.vel+self.acceleration, self.max_vel)
        self.move()
    def move_backward(self):
        self.vel = max(self.vel - (self.acceleration*2), -self.max_vel/2)
        self.move()
    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal
    def collide(self, mask, x=150, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        collision = mask.overlap(car_mask, offset)
        return collision
    def reset(self):
        # time.sleep(1)
        self.x, self.y = self.START_POSITION
        self.angle = 0
        self.vel = 0


def finish_line_colide_handle(player_car, computer_car, FINISH_MASK, FINISH_POSITION, game_info, win, FONT, run):
    # make sure we cant cross the finnish line from top
    player_finish_collision_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    computer_finish_collision_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)

    if computer_finish_collision_collide:
        if computer_finish_collision_collide[1] == 0:
            computer_car.collide_stop()
        else:
            blit_text_center(win,FONT,"You Lost!")
            pygame.time.wait(3000)
            game_info.reset()
            computer_car.reset()
            player_car.reset()
            run = False
            pygame.quit()

    if player_finish_collision_collide:
        if player_finish_collision_collide[1] == 0:
            player_car.collide_stop()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)

class GameInfo:
    LEVELS = 5
    def __init__(self, level = 1):
        self.level = level
        self.started = False
        self.level_start_time = 0
    
    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0
    
    def game_finished(self):
        return self.level > self.LEVELS
    
    def start_level(self):
        self.started = True
        self.level_start_time = time.time()
    
    def get_level_time(self):
        if not self.started:
            return 0
        return self.level_start_time - time.time()

def blit_text_center(win, font, text):
    render = font.render(text , 1, (200,200,200))
    win.blit(render, ((win.get_width()/2 - render.get_height()/2)-300 , win.get_height()/2 - render.get_height()/2))