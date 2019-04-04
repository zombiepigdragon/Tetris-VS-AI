import random

class Point:
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        value = int(value)
        if value > Point.min_x and value < Point.max_x:
            self._x = value
        else:
            raise ValueError()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        value = int(value)
        if value > Point.min_y and value < Point.max_y:
            self._y = value
        else:
            raise ValueError()

    def __init__(self, x, y, combined=None):
        self.x = x
        self.y = y
        if combined is not None:
            if len(combined) != 2:
                raise ValueError()
            else:
                self.x = combined[0]
                self.y = combined[1]

class Tetris_Game:
    def __init__(self, color_count, board_size, num_boards):
        boards = []
        Point.max_x, Point.max_y = board_size
        for _ in range(num_boards):
            b = Tetris_Board(board_size, color_count)
            boards.append(b)
        self.boards = boards

    def start(self, level):
        self.level = level
        self.score = 0
        self.current_time = 0
        for b in self.boards:
            b.time_since_last_move_down = 0
            b.set_next_piece()

    def update(self):
        for b in self.boards:
            b.move_piece_down_if_time(self.get_drop_time(self.level), b.current_piece)

    def add_delta_time(self, millis):
        self.current_time += millis
        for b in self.boards:
            b.time_since_last_move_down += millis

    def get_drop_time(self, level):
        return int(1000 / level)

class Tetris_Board:
    def __init__(self, size, color_count):
        self.width, self.height = size
        #Make a width by height grid of 0s
        self.grid = [[0 for x in range(self.width)] for y in range(self.height)]
        self.color_count = color_count
        self.time_since_last_move_down = 0

    def set_next_piece(self):
        print("Setting piece")
        pattern = random.choice(Tetris_Piece.Patterns)
        color = random.randrange(0, self.color_count)
        position = Point(int(self.width / 2), 0)
        p = Tetris_Piece(pattern, position, color)
        for i in range(5):
            try:
                self.transform_piece(Point(0, 0), p)
                i = -1
                break
            except PieceOutOfBoundsException:
                try:
                    self.transform_piece(Point(0, 1), p, True)
                except PieceCantMoveException:
                    raise GameOverException()
            except PieceCantMoveException:
                raise GameOverException()
        if i != -1:
            raise GameOverException()
        self.current_piece = p

    def merge_piece(self, piece):
        print("Merging piece")
        piece_pattern = piece.get_world_pattern()
        for point in piece_pattern:
            self.grid[point.y][point.x] = piece.color
        self.set_next_piece()

    def move_piece_down_if_time(self, threshold, piece):
        if self.time_since_last_move_down > threshold:
            self.time_since_last_move_down = 0
            self.move_piece_down(piece)

    def move_piece_down(self, piece):
        try:
            self.transform_piece(Point(0, 1), piece)
        except PieceCantMoveException:
            self.merge_piece(piece)
        except PieceOutOfBoundsException:
            self.merge_piece(piece)

    def transform_piece(self, distance, piece, ignore_outofbounds=False):
        #Check if transform valid
        pattern = piece.get_world_pattern()
        for point in pattern:
            new_point = Point(point.x + distance.x, point.y + distance.y)
            if self.grid[new_point.y][new_point.x] != 0:
                raise PieceCantMoveException()
        piece.position = Point(piece.position.x + distance.y, piece.position.x + distance.y)

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

    Point.min_x = -3
    Point.max_x = 3
    Point.min_y = -3
    Point.max_y = 3

    for pattern in Patterns:
        for index, pos in enumerate(pattern):
            pattern[index] = Point(pos[0], pos[1])

    def __init__(self, pattern, position, color):
        self.pattern = pattern
        self.position = position
        self.color = color
    
    def get_world_pattern(self):
        w_pattern = self.pattern.copy()
        for index, point in enumerate(w_pattern):
            w_pattern[index] = Point(point.x + self.position.x, point.y + self.position.y)
        return w_pattern

    def get_rotated_pattern(self, direction):
        pattern = self.pattern.copy()
        for index, old_point in enumerate(pattern):
            new_point = (-direction * old_point.y, direction * old_point.x)
            pattern[index] = new_point
        return pattern

class PieceCantMoveException(Exception):
    def __init__(self):
        print("Piece can't move")

class PieceOutOfBoundsException(Exception):
    def __init__(self):
        print("Piece out of bounds")

class GameOverException(Exception):
    def __init__(self):
        print("Game over")