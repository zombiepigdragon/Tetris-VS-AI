import tetris_core
import os, pygame

class Tetris_Board_Renderer:
    def __init__(self, board, size, background_image, tiles):
        self.board = board
        self.size = size
        self.background_image = background_image
        self.tiles = tiles

    def render(self):
        surface = pygame.Surface(self.size)
        surface.fill((255, 255, 255))
        surface.blit(self.background_image, (0, 0))
        for y, row in enumerate(self.board.grid):
            for x, value in enumerate(row):
                if value > 0:
                    surface.blit(tiles[value - 1], (x *32, y * 32))
        try:
            piece = self.board.current_piece
            value = piece.color
            for x, y in piece.get_world_pattern():
                surface.blit(tiles[value - 1], (x * 32, y * 32))
        except:
            pass
        return surface

tiles = []
for file in os.listdir("Assets/Tiles/"):
    tiles.append(pygame.image.load("Assets/Tiles/" + file))
background_image = pygame.image.load("Assets/grid.png")

def main():
    game = tetris_core.Tetris_Game(7, (12, 20), 1)
    board = Tetris_Board_Renderer(game.boards[0], (12 * 32, 20 * 32), background_image, tiles)
    running = True
    pygame.init()
    screen = pygame.display.set_mode((12 * 32, 20 * 32))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        display = board.render()
        screen.blit(display, (0,0))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()