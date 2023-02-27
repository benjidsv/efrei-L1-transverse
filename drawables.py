from math import cos, sin, asin, sqrt

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


class SideView:
    def __init__(self, ball):
        self.ball = ball
        self.sprite = MAP_SPRITE
        self.rect = pg.Rect(MAP_X, MAP_Y, MAP_SPRITE.get_width(), MAP_SPRITE.get_height())

    def ball_position_to_map_position(self):
        # TODO: fix
        return MAP_BALL_START_X + (self.ball.z - BALL_START_Z) * (MAP_GOAL_X - MAP_BALL_START_X) / (GOAL_Z -
                                                                                                    BALL_START_Z), \
               MAP_BALL_START_Y + (self.ball.y - BALL_START_Y) * (MAP_GOAL_Y - MAP_BALL_START_Y) / (
                           GOAL_Y + GOAL_HEIGHT -
                           BALL_START_Y)

    def draw(self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))
        x, y = self.ball_position_to_map_position()
        win.blit(pg.transform.scale(self.ball.sprite, (MAP_BALL_SIZE, MAP_BALL_SIZE)), (x, y))


# Game elements
class Goal:
    def __init__(self):
        self.rect = pg.Rect(GOAL_X, GOAL_Y, GOAL_WIDTH, GOAL_HEIGHT)

    def draw(self, win):
        pg.draw.rect(win, BLACK, self.rect)


class Ball:
    def __init__(self, master):
        self.a = 0
        self.b = 0
        self.c = 0
        self.angle_from_floor_to_shoot_dir = 0
        self.master = master
        self.rect = pg.Rect(BALL_START_X, BALL_START_Y, BALL_START_WIDTH, BALL_START_HEIGHT)
        self.sprite = BALL_SPRITE
        self.y = 0
        self.z = 0
        self.shooting = False
        self.t0 = 0
        self.dir = pg.Vector3(0, 0, GOAL_Z)
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.catched = False
        self.angle_from_floor_to_shoot = 0

    def size_by_depth(self):
        # Calcule la taille de la balle en fonction de la profondeur (z) par interpolation linéaire
        return BALL_START_WIDTH + self.z * BALL_DEPTH_TO_SIZE

    def height_adjustment_by_depth(self):
        # Calcule la hauteur de la balle (causée par la perspective) par interpolation linéaire
        return self.z * BALL_DEPTH_TO_HEIGHT

    @staticmethod
    def strength_to_height(s):
        # Calcule la hauteur à viser en fonction de la force du tir (le temps passé à rester appuyé sur le clic)
        return 60 + (s - 30) * -4.4

    def draw(self, win):
        size = self.size_by_depth()
        win.blit(pg.transform.scale(self.sprite, (size, size)), (self.rect.x, self.rect.y))

    def shoot(self, target, time_on_shoot, strength=1):
        if self.shooting:
            return  # Si on est déjà en train de tirer on annule

        self.t0 = time_on_shoot
        # Si la force est en dessous de 26 on tire au sol (car sinon la balle tombera trop bas)
        if strength < 26:
            target.y = BALL_TARGET_IF_FLOOR_SHOT
        else:
            target.y = self.strength_to_height(strength)

        # On calcule le vecteur direction et l'angle qu'il forme avec le sol
        self.dir.x = target.x - BALL_START_X
        self.dir.y = target.y - BALL_START_Y
        self.angle_from_floor_to_shoot_dir = radians(self.dir.angle_to(pg.Vector3(self.dir.x, FLOOR_LINE.y, self.dir.z))
                                                     )
        x = target.x - WIDTH / 2  # on centre x (car (0, 0) est en haut en à gauche)
        # On calcule l'angle formé par la projection de la trajectoire sur le plan (x, z) avec l'axe z
        angle_from_projection_to_axis = asin(GOAL_Z / sqrt(x ** 2 + GOAL_Z ** 2))

        v0 = self.dir.magnitude() * BALL_SPEED_FACTOR  # On calcule v0
        # On cacule vx,y,z à l'aide des équations horaires
        self.vx = v0 * cos(self.angle_from_floor_to_shoot_dir) * cos(angle_from_projection_to_axis)
        self.vy = v0 * sin(self.angle_from_floor_to_shoot_dir)
        self.vz = v0 * cos(self.angle_from_floor_to_shoot_dir) * sin(angle_from_projection_to_axis)

        if self.dir.x < 0:  # si la direction est négative on change le signe de la vitesse
            self.vx *= -1

        # TODO: fix floor shots (a few pixels too low)
        self.shooting = True

    def handle_physics(self, t):
        if self.catched:
            # Si le goal à attrapé la balle on la positionne dans ses mains
            self.rect.x = self.master.gk.rect.x + GOALKEEPER_WIDTH / 2 - BALL_END_WIDTH / 2
            self.rect.y = self.master.gk.rect.y + GOALKEEPER_HEIGHT / 2 - BALL_END_HEIGHT / 2
            return

        if not self.shooting:
            # Si on n'est pas en train de tirer c'est inutile d'éxecuter cette fonction car la balle est immobile
            return

        # On met à jour les coordonnées de la balle en fonction des valeurs calculées dans shoot()
        self.rect.x = self.vx * (t - self.t0) + BALL_START_X
        self.z = self.vz * (t - self.t0)
        if self.angle_from_floor_to_shoot_dir > 0.1:
            # Si l'angle est > 0,1 alors c'est un tir normal donc on calcule simplement y
            self.y = 0.5 * GRAVITY * (t - self.t0) ** 2 - self.vy * (t - self.t0) + BALL_START_Y
            # On affiche la balle avec un ajustement a cause de la perspective
            self.rect.y = self.y + self.height_adjustment_by_depth()
        else:
            # Si l'angle est < alors on tire au sol donc on applique pas de gravité
            self.rect.y = self.vy * (
                    t - self.t0) + self.height_adjustment_by_depth() + BALL_START_Y

        if self.z >= GOAL_Z:
            # Si la balle atteint la profondeur du but on vérifie si elle est dedans
            self.shooting = False
            self.master.check_goal()

    def get_catched(self):
        self.catched = True

    def reset(self):
        # On remet les valeurs à 0
        self.shooting = False
        self.rect.x = BALL_START_X
        self.rect.y = BALL_START_Y
        self.z = BALL_START_Z
        self.catched = False


class GoalKeeper:
    def __init__(self, master):
        # On initialise les variables
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
            # Si on a un angle on tourne l'image
            rotated_sprite = pg.transform.rotate(self.sprite, -self.jumping_dir * self.angle)
            rotated_rect = rotated_sprite.get_rect(center=self.sprite.get_rect(topleft=self.rect.topleft).center)
            self.r_rect = rotated_rect
            win.blit(rotated_sprite, (rotated_rect.x, rotated_rect.y))
        else:
            # Sinon on l'affiche normalement
            win.blit(self.sprite, (self.rect.x, self.rect.y))

    def handle_movement(self, p_keys, t):
        if self.jumping:
            # Si on saute
            t -= self.t0  # On calcule le temps depuis le début du saut
            # On calcule la position du goal avec les équations horaires
            self.rect.x = self.vx * t + self.x0
            self.rect.y = 0.5 * GRAVITY * t ** 2 - self.vy * t + GOALKEEPER_START_Y
            if self.jumping_dir != 0:
                # Si on plonge on fais tourner le goal vers le bas
                self.angle += GOALKEEPER_TURN_SPEED

            if self.angle != 0 and self.r_rect.y >= GOALKEEPER_START_Y + GOALKEEPER_HEIGHT - GOALKEEPER_WIDTH:  # 207
                # Si le goal est tourné (l'angle n'est pas nul) et qu'il touche le sol on remet ses valeurs à 0 sauf x
                self.reset(False)
            elif self.jumping_dir == 0 and self.rect.y >= GOALKEEPER_START_Y:
                # Si le goal saute sur place et touche le sol on remet ses valeurs à 0 sauf x
                self.reset(False)

            return

        # En fonction des touches pressées par l'utilisateur
        if p_keys[pg.K_q]:
            # On va a gauche
            self.rect.x -= GOALKEEPER_SPEED
            self.jumping_dir = -1
        if p_keys[pg.K_d]:
            # On va a droite
            self.rect.x += GOALKEEPER_SPEED
            self.jumping_dir = 1
        if not p_keys[pg.K_q] and not p_keys[pg.K_d]:
            # On est immobile
            self.jumping_dir = 0
        if p_keys[pg.K_SPACE]:
            # On suate
            self.jumping = True
            self.t0 = t
            self.x0 = self.rect.x
            self.vx = self.jumping_dir * GOALKEEPER_JUMP_SPEED_X * cos(GOALKEEPER_JUMP_ANGLE)
            # Si on saute sur le coté on utilise les équations horaires
            self.vy = GOALKEEPER_JUMP_SPEED_Y * sin(GOALKEEPER_JUMP_ANGLE if self.jumping_dir != 0
                                                    else GOALKEEPER_VERTICAL_JUMP_SPEED)
            # Sinon on utilise simplement une constante

    def try_catching(self, ball):
        # Si on a une collision entre le goal et balle alors le goalk à attrapé la balle
        if self.r_rect.colliderect(ball.rect):
            ball.get_catched()
            return True

    def reset(self, reset_x=True):
        # On remet les valeurs à zero
        if reset_x:
            self.rect.x = GOALKEEPER_START_X
        self.rect.y = GOALKEEPER_START_Y
        self.r_rect = self.rect
        self.angle = 0
        self.jumping = False
        self.jumping_dir = 0
