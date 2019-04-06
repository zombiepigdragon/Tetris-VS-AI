import random
from enum import Enum
from pygame.time import get_ticks

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
        if value >= Point.min_x and value < Point.max_x:
            self._x = value
        else:
            raise ValueError()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        value = int(value)
        if value >= Point.min_y and value < Point.max_y:
            self._y = value
        else:
            raise ValueError()

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __repr__(self):
        return "Point(" + str(self.x) + ", " + str(self.y) + ")"

    def __init__(self, x, y, combined=None, ignore_limits=False):
        if ignore_limits:
            self._x = x
            self._y = y
        else:
            self.x = x
            self.y = y
        if combined is not None:
            if len(combined) != 2:
                raise ValueError()
            else:
                if ignore_limits:
                    self._x = combined[0]
                    self._y = combined[1]
                else:
                    self.x = combined[0]
                    self.y = combined[1]
                

class Actions(Enum):
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    HARD_DROP = 4
    ROTATE_CW = 5
    ROTATE_CCW = 6

class TetrisGame:
    def __init__(self, color_count, board_size, num_boards):
        boards = []
        Point.max_x, Point.max_y = board_size
        for _ in range(num_boards):
            b = TetrisBoard(board_size, color_count)
            boards.append(b)
        self.boards = boards

    def start(self):
        self.score = 0
        self.current_time = 0
        self.level = 0
        for b in self.boards:
            b.time_since_last_move_down = 0
            b.cleared_lines = 0
            b.set_next_piece()

    def update(self):
        self.level = self.calculate_level()
        drop_time = self.get_drop_time(self.level)
        for b in self.boards:
            b.move_piece_down_if_time(drop_time, b.current_piece)
            b.clear_lines()

    def calculate_level(self):
        total_lines = 0
        for b in self.boards:
            total_lines += b.cleared_lines
        level = int(total_lines / 10) + 1
        if self.level != level:
            print("New level:", level)
        return level

    def get_drop_time(self, level):
        return int(1000 / level)

    def handle_event(self, event, board_index):
        board = self.boards[board_index]
        piece = board.current_piece
        try:
            if event is Actions.MOVE_DOWN:
                board.move_piece_down(piece)
            elif event is Actions.MOVE_LEFT:
                board.transform_piece(Point(-1, 0, ignore_limits=True), piece)
            elif event is Actions.MOVE_RIGHT:
                board.transform_piece(Point(1, 0, ignore_limits=True), piece)
            elif event is Actions.HARD_DROP:
                board.hard_drop_piece(piece)
            elif event is Actions.ROTATE_CW:
                board.rotate_piece(1, piece)
            elif event is Actions.ROTATE_CCW:
                board.rotate_piece(-1, piece)
        except PieceCantMoveException:
            pass
        except PieceOutOfBoundsException:
            pass

class TetrisBoard:
    def __init__(self, size, color_count):
        self.width, self.height = size
        #Make a width by height grid of 0s
        self.grid = [[0 for x in range(self.width)] for y in range(self.height)]
        self.color_count = color_count
        self.cleared_lines = 0

    def set_next_piece(self):
        pattern = random.choice(TetrisPiece.Patterns)
        color = random.randrange(1, self.color_count)
        position = Point(int(self.width / 2), 0)
        p = TetrisPiece(pattern, position, color)
        try:
            self.transform_piece(Point(0, 0), p)
        except PieceCantMoveException:
            raise GameOverException()
        self.current_piece = p
        self.last_down_time = get_ticks()

    def merge_piece(self, piece):
        piece_pattern = piece.get_world_pattern()
        for point in piece_pattern:
            self.grid[point.y][point.x] = piece.color
        self.set_next_piece()

    def move_piece_down_if_time(self, threshold, piece):
        if get_ticks() - self.last_down_time > threshold:
            self.move_piece_down(piece)

    def move_piece_down(self, piece):
        try:
            self.transform_piece(Point(0, 1), piece)
        except PieceCantMoveException:
            self.merge_piece(piece)
        except PieceOutOfBoundsException:
            self.merge_piece(piece)
        self.last_down_time = get_ticks()

    def hard_drop_piece(self, piece):
        can_lower = True
        while can_lower:
            try:
                self.transform_piece(Point(0, 1), piece)
            except PieceCantMoveException:
                can_lower = False
            except PieceOutOfBoundsException:
                can_lower = False
        self.merge_piece(piece)

    def transform_piece(self, distance, piece):
        #Check if transform valid
        pattern = piece.get_world_pattern()
        for point in pattern:
            try:
                new_point = Point(point.x + distance.x, point.y + distance.y)
            except ValueError:
                raise PieceOutOfBoundsException()
            if self.grid[new_point.y][new_point.x] != 0:
                raise PieceCantMoveException()
        piece.position = Point(piece.position.x + distance.x, piece.position.y + distance.y)

    def rotate_piece(self, direction, piece):
        assert(direction == 1 or direction == -1)
        try:
            pattern = piece.get_rotated_pattern(direction)
            w_pattern = piece.get_world_pattern(pattern)
            for point in w_pattern:
                if self.grid[point.y][point.x] != 0:
                    raise PieceCantMoveException()
        except ValueError:
            raise PieceCantMoveException()
        piece.pattern = pattern

    def clear_lines(self):
        for index, row in enumerate(self.grid):
            for value in row:
                if value == 0:
                    break
            else:
                del self.grid[index]
                self.grid.insert(0, [0 for x in range(self.width)])
                self.cleared_lines += 1

class TetrisPiece:

    Patterns = (
        [(-1, 0), (0, 0), (1, 0), (2, 0)],  #I
        [(0, 1), (0, 0), (1, 0), (2, 0)],   #J
        [(0, 1), (0, 0), (-1, 0), (-2, 0)], #L
        [(0, 0), (1, 0), (0, 1), (1, 1)],   #O
        [(-1, 0), (0, 0), (0, 1), (1, 1)],  #S
        [(-1, 0), (0, 0), (1, 0), (0, 1)],  #T
        [(-1, 0), (0, 0), (0, 1), (1, 1)]   #Z
    )

    for pattern in Patterns:
        for index, pos in enumerate(pattern):
            pattern[index] = Point(pos[0], pos[1], ignore_limits=True)
    del index, pos, pattern

    def __init__(self, pattern, position, color):
        self.pattern = pattern
        self.position = position
        assert(color > 0)
        self.color = color
    
    def get_world_pattern(self, pattern=None):
        if pattern == None:
            pattern = self.pattern
        w_pattern = pattern.copy()
        for index, point in enumerate(w_pattern):
            w_pattern[index] = Point(point.x + self.position.x, point.y + self.position.y)
        return w_pattern

    def get_rotated_pattern(self, direction):
        pattern = self.pattern.copy()
        for index, old_point in enumerate(pattern):
            new_point = Point(-direction * old_point.y, direction * old_point.x, ignore_limits=True)
            pattern[index] = new_point
        return pattern

class PieceCantMoveException(Exception):
    pass

class PieceOutOfBoundsException(Exception):
    pass

class GameOverException(Exception):
    def __init__(self):
        print("Game over")