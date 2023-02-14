from math import cos, sin, radians

from constants import *


# GUI
class MainMenuBackground:
    def __init__(self):
        pass


class GameBackground:
    def __init__(self):
        self.rect = pg.Rect(0, 0, WIDTH, 304)

    def draw(self, win):
        win.fill(GREEN)
        pg.draw.rect(win, BLUE, self.rect)


class Button:
    def __init__(self, x, y, width, heigth, text="BUTTON", font_size=48):
        self.rect = pg.Rect(x, y, width, heigth)
        font = pg.font.Font('freesansbold.ttf', font_size)
        self.text = font.render(text, True, BLACK)
        self.tw = self.text.get_width() / 2
        self.th = self.text.get_height() / 2

    def draw(self, win):
        pg.draw.rect(win, WHITE, self.rect)
        win.blit(self.text, (self.rect.centerx - self.tw, self.rect.centery - self.th))

    def check_click(self, mx, my):
        return self.rect.collidepoint(mx, my)


class LoadingBar:
    def __init__(self, left, top, width, heigth, bg_color, fill_color, optimal_color=(0, 0, 0), start_value=0,
                 optimal_value=0, render_if_null=False):
        self.rect = pg.Rect(left, top, width, heigth)
        self.fill_rect = pg.Rect(left, top, width * start_value, heigth)
        self.draw_opt_rect = optimal_value > 0
        self.optimal_rect = pg.Rect(left + width * optimal_value, top, width * OPTIMAL_WIDTH_FACTOR, heigth)
        self.width = width
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.optimal_color = optimal_color
        self.val = start_value
        self.render_if_null = render_if_null

    def draw(self, win):
        if not self.render_if_null and self.val == 0:
            return

        pg.draw.rect(win, self.bg_color, self.rect)
        self.fill_rect.width = self.width * self.val
        pg.draw.rect(win, self.fill_color, self.fill_rect)
        if self.draw_opt_rect:
            pg.draw.rect(win, self.optimal_color, self.optimal_rect)


class Text:
    def __init__(self, x, y, text, size, color, font='freesansbold.ttf', bold=False):
        self.txt = pg.font.Font(font, size).render(text, True, color)
        self.font, self.size, self.color = font, size, color
        self.x, self.y = x, y

    def set_txt(self, new_txt):
        self.txt = pg.font.Font(self.font, self.size).render(new_txt, True, self.color)

    def draw(self, win):
        win.blit(self.txt, self.x, self.y)
        #TODO: fix


# Game elements
class Goal:
    def __init__(self):
        self.rect = pg.Rect(GOAL_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT)

    def draw(self, win):
        pg.draw.rect(win, BLACK, self.rect)


# TODO: make strong shot less precise

class Ball:
    def __init__(self, master):
        self.master = master
        self.rect = pg.Rect(BALL_START_X, BALL_START_Y, BALL_START_WIDTH, BALL_START_HEIGHT)
        self.sprite = BALL_SPRITE
        self.z = 0
        self.shooting = False
        self.t0 = 0
        self.dir = pg.Vector3(0, 0, GOAL_Z)
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.catched = False
        self.shoot_angle = 0

    def size_by_depth(self):
        return BALL_START_WIDTH + self.z * BALL_DEPTH_TO_SIZE

    def height_adjustment_by_depth(self):
        return self.z * BALL_DEPTH_TO_HEIGHT

    @staticmethod
    def target_y_adjustment(ty):
        return 170 + (ty - 140) * 15 / 140

    def draw(self, win):
        size = self.size_by_depth()
        win.blit(pg.transform.scale(self.sprite, (size, size)), (self.rect.x, self.rect.y))
        # pg.draw.circle(win, WHITE, (self.rect.x, self.rect.y), self.radius_by_depth())
        # pg.draw.line(win, BLUE, (self.rect.x, self.rect.y), (BALL_START_X + self.dir.x, BALL_START_Y + self.dir.y))
        # pg.draw.line(win, RED, (BALL_START_X, BALL_START_Y), (BALL_START_X + self.dir.x, BALL_START_Y + self.dir.y))

    def shoot(self, target, time_on_shoot, strength=1):
        if self.shooting:
            return

        self.shooting = True
        self.t0 = time_on_shoot
        print(GOAL_Y + GOAL_HEIGHT)
        print(target.y)
        if target.y <= GOAL_Y + GOAL_HEIGHT:
            target.y -= self.target_y_adjustment(target.y)
        else:
            target.y = BALL_TARGET_IF_FLOOR_SHOT

        self.dir.x = target.x - BALL_START_X
        self.dir.y = target.y - BALL_START_Y

        self.shoot_angle = radians(self.dir.angle_to(pg.Vector3(self.dir.x, FLOOR_LINE.y, self.dir.z)))
        spd = BALL_SPEED_FACTOR * strength
        self.vx = spd * cos(self.shoot_angle) * self.dir.x
        self.vy = spd * sin(self.shoot_angle) * self.dir.y
        self.vz = spd * cos(self.shoot_angle) * self.dir.z

    def handle_physics(self, t):
        if self.catched:
            self.rect.x = self.master.gk.rect.x + GOALKEEPER_WIDTH / 2 - BALL_END_WIDTH / 2
            self.rect.y = self.master.gk.rect.y + GOALKEEPER_HEIGHT / 2 - BALL_END_HEIGHT / 2

        if not self.shooting:
            return

        self.rect.x = self.vx * (t - self.t0) + BALL_START_X
        self.z = self.vz * (t - self.t0)
        if self.shoot_angle > 0.1:
            self.rect.y = 0.5 * GRAVITY * (t - self.t0) ** 2 + self.vy * (
                    t - self.t0) + self.height_adjustment_by_depth() + \
                          BALL_START_Y
        else:
            self.rect.y = self.vy * (
                    t - self.t0) + self.height_adjustment_by_depth() + \
                          BALL_START_Y
        # print("ball physics: ", self.rect.x, self.rect.y, self.z)

        if self.z >= GOAL_Z:
            self.shooting = False
            self.master.check_goal()

    def get_catched(self):
        self.catched = True

    def reset(self):
        self.shooting = False
        self.rect.x = BALL_START_X
        self.rect.y = BALL_START_Y
        self.z = BALL_START_Z
        self.catched = False


class GoalKeeper:
    def __init__(self, master):
        self.master = master
        self.sprite = GOALKEEPER_SPRITE
        self.rect = pg.Rect(GOALKEEPER_START_X, GOALKEEPER_START_Y, GOALKEEPER_WIDTH, GOALKEEPER_HEIGHT)
        self.r_rect = self.rect
        self.jumping = False
        self.jumping_dir = 0
        self.angle = 0
        self.t0 = 0
        self.x0 = 0
        self.vy = 0
        self.vx = 0

    def draw(self, win):
        if self.angle != 0:
            rotated_sprite = pg.transform.rotate(self.sprite, -self.jumping_dir * self.angle)
            rotated_rect = rotated_sprite.get_rect(center=self.sprite.get_rect(topleft=self.rect.topleft).center)
            self.r_rect = rotated_rect
            win.blit(rotated_sprite, (rotated_rect.x, rotated_rect.y))
            # pg.draw.rect(win, PINK, self.r_rect)
        else:
            win.blit(self.sprite, (self.rect.x, self.rect.y))

    def handle_movement(self, p_keys, t):
        if self.jumping:
            t -= self.t0
            self.rect.x = self.vx * t + self.x0
            self.rect.y = 0.5 * GRAVITY * t ** 2 - self.vy * t + GOALKEEPER_START_Y
            self.angle += GOALKEEPER_TURN_SPEED

            if self.angle != 0 and self.r_rect.y >= GOALKEEPER_START_Y + GOALKEEPER_HEIGHT - GOALKEEPER_WIDTH:  # 207
                self.reset(False)
            elif self.angle == 0 and self.rect.y >= GOAL_Y:
                self.reset(False)

            return

        if p_keys[pg.K_q]:
            self.rect.x -= GOALKEEPER_SPEED
            self.jumping_dir = -1
        if p_keys[pg.K_d]:
            self.rect.x += GOALKEEPER_SPEED
            self.jumping_dir = 1
        if not p_keys[pg.K_q] and not p_keys[pg.K_d]:
            self.jumping_dir = 0
        if p_keys[pg.K_SPACE]:
            self.jumping = True
            self.t0 = t
            self.x0 = self.rect.x
            self.vx = self.jumping_dir * GOALKEEPER_JUMP_SPEED_X * cos(GOALKEEPER_JUMP_ANGLE)
            self.vy = GOALKEEPER_JUMP_SPEED_Y * sin(GOALKEEPER_JUMP_ANGLE if self.jumping_dir != 0 else PI_HALVES)

    def try_catching(self, ball):
        if self.r_rect.colliderect(ball.rect):
            ball.get_catched()
            return True

    def reset(self, reset_x=True):
        if reset_x:
            self.rect.x = GOALKEEPER_START_X
        self.rect.y = GOALKEEPER_START_Y
        self.r_rect = self.rect
        self.angle = 0
        self.jumping = False
        self.jumping_dir = 0
