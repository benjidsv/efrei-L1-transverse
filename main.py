from drawables import *


class Game:
    def __init__(self):
        # Création et paramétrage de la fen^^re
        self.win = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Projet Transverse Prototype")

        # Initialisation des variables
        self.running = False
        self.clock = pg.time.Clock()
        self.background = GameBackground()
        self.ball = Ball(self)
        self.gk = GoalKeeper(self)
        self.goal = Goal()
        self.score = 0

    def draw_window(self, *drawables):
        # Appel de la fonction draw des objets à dessiner
        for d in drawables:
            d.draw(self.win)

        pg.display.update()

    def check_goal(self):
        if self.gk.try_catching(self.ball):
            print("catch")
        else:
            if self.goal.rect.colliderect(self.ball.rect):
                print("goal")
                self.score += 1
            else:
                print("no goal")

    def main_menu(self):
        bg = GameBackground()
        button = Button(WIDTH/2 - 323/2, HEIGHT/2 - 50, 323, 100, "S T A R T")
        while True:
            self.clock.tick(MENU_FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    mx, my = pg.mouse.get_pos()
                    if button.check_click(mx, my):
                        self.run()
                        return

            self.draw_window(bg, button)

    def pause_menu(self):
        button = Button(WIDTH/2 - 323/2, HEIGHT/2 - 50, 323, 100, "R E S U M E")
        while True:
            self.clock.tick(MENU_FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    return
                if event.type == pg.MOUSEBUTTONDOWN:
                    mx, my = pg.mouse.get_pos()
                    if button.check_click(mx, my):
                        return

            pressed_keys = pg.key.get_pressed()
            if pressed_keys[pg.K_ESCAPE] or pressed_keys[pg.K_TAB]:
                return

            self.draw_window(self.background, self.goal, self.gk, self.ball, button)

    def run(self):
        click_start = 0
        m_hold = False
        loading_bar = LoadingBar(0, 0, 200, 50, WHITE, RED, optimal_value=0.5)
        side_view = SideView(self.ball)
        self.running = True
        while self.running:
            # Régule l'éxecution de la boucle à 60 fois par seconde
            self.clock.tick(GAME_FPS)
            m = pg.Vector2(pg.mouse.get_pos())
            t = pg.time.get_ticks() * MS_TO_S

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    click_start = t
                    m_hold = True
                if event.type == pg.MOUSEBUTTONUP and m_hold:
                    m_hold = False
                    loading_bar.val = 0
                    self.ball.shoot(m, t, min(t - click_start, MAX_SHOOT_HOLD_TIME) * BALL_TIME_S_TO_STRENTGH)

            pressed_keys = pg.key.get_pressed()
            if pressed_keys[pg.K_a]:
                self.ball.reset()
                self.gk.reset()
            if pressed_keys[pg.K_ESCAPE] or pressed_keys[pg.K_TAB]:
                self.pause_menu()

            self.gk.handle_movement(pressed_keys, t)
            self.ball.handle_physics(t)

            if m_hold:
                loading_bar.val = min(t - click_start, MAX_SHOOT_HOLD_TIME)

            self.draw_window(self.background, self.goal, self.gk, self.ball, loading_bar, side_view)


def main():
    pg.init()

    game = Game()
    game.main_menu()

    pg.quit()


if __name__ == '__main__':
    main()
