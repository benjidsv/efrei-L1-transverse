from constants import *


def function(x):
    return -0.01 * x**2 + 4 * x


boardx, boardy = int(WIDTH/4), int(HEIGHT/4)
boardw, boardh = int(WIDTH/2), int(HEIGHT/2)
drawstep = 1


class TestScreen:
    def __init__(self):
        self.win = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Projet Transverse Test")
        self.running = False
        self.clock = pg.time.Clock()

    def draw_window(self, background, board):
        pg.draw.rect(self.win, BLACK, background)
        pg.draw.rect(self.win, WHITE, board)

        for x in range(drawstep, boardw, drawstep):
            current_y = -function(x)
            if current_y > 0:
                break

            if current_y + boardh > 0:
                pg.draw.line(self.win, RED, (x - drawstep + boardx,
                                            -function(x - drawstep) + boardy + boardh),
                                            (x + boardx, current_y + boardy + boardh), 2)

        pg.display.update()

    def run(self):
        background = pg.Rect(0, 0, WIDTH, HEIGHT)
        board = pg.Rect(boardx, boardy, boardw, boardh)
        while True:
            self.clock.tick(GAME_FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    return

            pressed_keys = pg.key.get_pressed()

            self.draw_window(background, board)


def main():
    pg.init()

    test_screen = TestScreen()
    test_screen.run()

    pg.quit()

if __name__ == "__main__":
    main()
