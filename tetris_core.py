import random

class Tetris_Game:
    def __init__(self, color_count):
        self.color_count = color_count

class Tetris_Board:
    def __init__(self, size, color_count):
        self.width, self.height = size
        #Make a width by height grid of 0s
        self.grid = [[0 for x in range(self.width)] for y in range(self.height)]
        self.color_count = color_count

    def set_next_piece(self):
        pattern = random.choice(Tetris_Piece.Patterns)
        color = random.randrange(0, self.color_count)
        position = (self.width / 2, 0)
        p = Tetris_Piece(pattern, position, color)
        while True:
            try:
                self.transform_piece((0, 1), p)
                break
            except PieceOutOfBoundsException:
                pass
            except PieceCantMoveException:
                raise GameOverException()
        
        self.current_piece = p

    def merge_piece(self, piece):
        piece_pattern = piece.get_world_pattern()
        for point in piece_pattern:
            self.grid[point[1]][point[0]] = piece.color

    def move_piece_down(self, piece):
        try:
            self.transform_piece((0, 1), piece)
        except PieceCantMoveException:
            self.merge_piece(piece)

    def transform_piece(self, distance, piece):
        #Check if transform valid
        pattern = piece.get_world_pattern()
        for point in pattern:
            new_point = (point[0] + distance[0], point[1], distance[1])
            if point[0] < 0 or point[1] < 0:
                raise PieceOutOfBoundsException()
            if self.grid[new_point[1]][new_point[0]] != 0:
                raise PieceCantMoveException()
        piece.position = (piece.position[0] + distance[0], piece.position[1] + distance[1])

    def rotate_piece(self, direction, piece):
        assert(direction == 1 or direction == -1)
        piece.pattern = piece.get_rotated_pattern(direction)


class Tetris_Piece:

    Patterns = (
        [(-1, 0), (0, 0), (1, 0), (2, 0)],  #I
        [(0, 1), (0, 0), (1, 0), (2, 0)],   #J
        [(0, 1), (0, 0), (-1, 0), (-2, 0)], #L
        [(0, 0), (1, 0), (0, 1), (1, 1)],   #O
        [(-1, 0), (0, 0), (0, 1), (1, 1)],  #S
        [(-1, 0), (0, 0), (1, 0), (0, 1)],  #T
        [(-1, -1), (0, -1), (0, 0), (1, 0)] #Z
    )

    def __init__(self, pattern, position, color):
        self.pattern = pattern
        self.position = position
        self.color = color
    
    def get_world_pattern(self):
        w_pattern = self.pattern.copy()
        for index, point in enumerate(w_pattern):
            w_pattern[index] = (point[0] + self.position[0], point[1] + self.position[1])
        return w_pattern

    def get_rotated_pattern(self, direction):
        pattern = self.pattern.copy()
        for i in range(0, len(pattern)):
            old_point = pattern[i]
            new_point = (-direction * old_point[1], direction * old_point[0])
            pattern[i] = new_point
        return pattern

class PieceCantMoveException(Exception):
    pass
class PieceOutOfBoundsException(Exception):
    pass
class NewPieceException(Exception):
    pass
class GameOverException(Exception):
    pass