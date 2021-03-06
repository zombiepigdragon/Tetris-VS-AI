import tetris_core
from ai import BasicTetrisAI
from tetris_core import Actions
import os, pygame

class TetrisBoardRenderer:
    def __init__(self, board, size, background_image, tiles):
        self.board = board
        self.size = size
        self.background_image = background_image
        self.tiles = tiles
        self.cached = None

    def render(self):
        if self.board.changed:
            surface = pygame.Surface(self.size)
            surface.fill((255, 255, 255))
            surface.blit(self.background_image, (0, 0))
            for y, row in enumerate(self.board.grid):
                for x, value in enumerate(row):
                    if value > 0:
                        surface.blit(tiles[value - 1], (x *32, y * 32))
            self.cached = surface
            self.board.changed = False
        else:
            surface = self.cached
        try:
            surface = surface.copy()
            piece = self.board.current_piece
            value = piece.color
            for point in piece.get_world_pattern():
                x = point.x
                y = point.y
                surface.blit(tiles[value - 1], (x * 32, y * 32))
        except:
            pass
        return surface

tiles = []
for file in os.listdir("Assets/Tiles/"):
    tiles.append(pygame.image.load("Assets/Tiles/" + file))
background_image = pygame.image.load("Assets/grid.png")

def main():
    game = tetris_core.TetrisGame(7, (12, 20), 2)
    playerboard = TetrisBoardRenderer(game.boards[0], (12 * 32, 20 * 32), background_image, tiles)
    aiboard = TetrisBoardRenderer(game.boards[1], (12 * 32, 20 * 32), background_image, tiles)
    ai = BasicTetrisAI(game, 1, 7)
    running = True
    game_over = False
    pygame.init()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28)
    screen = pygame.display.set_mode((12 * 32 * 2 + 20, 20 * 32))
    game.start()
    while running:
        try:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and not game_over:
                    if event.key == pygame.K_s:
                        game.handle_event(Actions.MOVE_DOWN, 0)
                    elif event.key == pygame.K_a:
                        game.handle_event(Actions.MOVE_LEFT, 0)
                    elif event.key == pygame.K_d:
                        game.handle_event(Actions.MOVE_RIGHT, 0)
                    elif event.key == pygame.K_w:
                        game.handle_event(Actions.HARD_DROP, 0)
                    elif event.key == pygame.K_q:
                        game.handle_event(Actions.ROTATE_CCW, 0)
                    elif event.key == pygame.K_e:
                        game.handle_event(Actions.ROTATE_CW, 0)
            if not game_over:
                ai.run()
                game.update()
            pdisplay = playerboard.render()
            screen.blit(pdisplay, (0,0))
            aidisplay = aiboard.render()
            screen.blit(aidisplay, (12 * 32 + 20, 0))
            fpscounter = font.render(str(clock.get_fps()), True, (0,0,0))
            screen.blit(fpscounter, (10, 10))
            if game_over:
                game_over = font.render("Game Over", True, (255,0,0), (255,255,255))
                screen.blit(game_over, ((12 * 32 * 2 + 20) / 2, (20 * 32) / 2))
            pygame.display.flip()
        except tetris_core.GameOverException:
            game_over = True
            print("Game over")
    pygame.quit()

if __name__ == "__main__":
    main()