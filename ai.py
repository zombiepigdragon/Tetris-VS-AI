from tetris_core import Actions, Point, Translation, TetrisPiece, PieceCantMoveException, PieceOutOfBoundsException
import random
from pygame.time import get_ticks

class BasicTetrisAI:
    def __init__(self, game, board_index, difficulty):
        self.game = game
        self.board_index = board_index
        self.board = game.boards[board_index]
        self.last_time = get_ticks()
        self.difficulty = difficulty
        print("Difficulty:", difficulty)
        self.success = True
        self.next_move = None
        self.set_next_move_time()
        self.moves_remaining_before_mistake = self.calculate_mistake_moves(difficulty)

    def set_next_move_time(self):
        raw_time = 1000 / self.difficulty
        offset = raw_time / 10
        min_time = int(raw_time - offset)
        max_time = int(raw_time + offset)
        self.next_move_time = random.randrange(min_time, max_time)

    def run(self):
        if get_ticks() - self.last_time > self.next_move_time:
            self.last_time = get_ticks()
            self.set_next_move_time()
            if self.success:
                self.set_next_move()
            if self.next_move is not None:
                move = self.next_move.move
                if (self.moves_remaining_before_mistake == 0):
                    move = random.choice(list(Actions))
                    self.moves_remaining_before_mistake = self.calculate_mistake_moves(self.difficulty)
                else: 
                    self.moves_remaining_before_mistake -= 1
                self.success = self.game.handle_event(move, 1)
            else:
                self.success = True
                return None

    def set_next_move(self):
        if self.next_move is None:
            outcomes = self.PotientialOutcome.get_possible_outcomes(self.board)
            lowest_gap_count = min([outcome.gaps for outcome in outcomes])
            outcomes = [outcome for outcome in outcomes if outcome.gaps == lowest_gap_count]
            lowest_height = min([outcome.height for outcome in outcomes])
            outcomes = [outcome for outcome in outcomes if outcome.height == lowest_height]
            lowest_piece_y = max([outcome.final_position.y for outcome in outcomes])
            outcomes = [outcome for outcome in outcomes if outcome.final_position.y == lowest_piece_y]
            best_outcome = outcomes[0]
            self.next_move = BasicTetrisAI.Move(best_outcome.rotations_needed, best_outcome.translations_needed)
            self.next_move.outcome = best_outcome
            self.next_move_position = best_outcome.final_position
        else:
            self.next_move = self.next_move.next_move

    def calculate_mistake_moves(self, difficulty):
        if difficulty <= 0:
            return -1
        if difficulty > 10:
            difficulty = 10
        a = 15 #Probably there's a better way 
        b = 20
        minimum = difficulty + b
        maximum = a * difficulty * difficulty + b * difficulty + difficulty
        moves = random.randint(minimum, maximum)
        print(moves, "before mistake")
        return moves

    class PotientialOutcome():

        @staticmethod
        def get_possible_outcomes(board):
            rotated_pieces = []
            rotated_pieces.append(board.current_piece.copy())
            for i in range(3):
                p = rotated_pieces[i]
                rotated_pieces.append(TetrisPiece(p.get_rotated_pattern(1), p.position, p.color))
            possible_outcomes = []
            for r_index, r_piece in enumerate(rotated_pieces):
                for x in range(board.width):
                    p = r_piece.copy()
                    p.position = Translation(x, 0)
                    valid = True
                    for point in p.pattern:
                        def move_into_valid_y(pattern):
                            for point in pattern:
                                point.y += 1
                            for point in pattern:
                                if point.y < 0:
                                    move_into_valid_y(pattern)
                                    break
                        w_point = Translation(point.x + p.position.x, point.y + p.position.y)
                        if w_point.x < 0 or w_point.x >= board.width:
                            valid = False
                        if w_point.y < 0:
                            move_into_valid_y(p.pattern)
                    if not valid:
                        continue
                    b = board.copy()
                    b.hard_drop_piece(p)
                    move = BasicTetrisAI.PotientialOutcome(
                        b.count_gaps(), b.count_rows(), r_index, 
                        Translation(-(board.current_piece.position.x - p.position.x), 0), p.position)
                    possible_outcomes.append(move)
            return possible_outcomes

        def __init__(self, gaps, height, rotations_needed, translations_needed, final_position):
            self.gaps = gaps
            self.height = height
            self.rotations_needed = rotations_needed
            self.translations_needed = translations_needed
            self.final_position = final_position

        def __repr__(self):
            return "Outcome(gaps: " + str(self.gaps) + ", height: " + str(self.height) + ", rotations_needed: " + \
            str(self.rotations_needed) + ", translations_needed: " + str(self.translations_needed) + \
            ", final_position: " + str(self.final_position) + ")"

    class Move:
        def __init__(self, roatations_needed, translations_needed):
            if translations_needed.y > 0:
                self.move = Actions.MOVE_DOWN
                translations_needed.y -= 1
            elif roatations_needed < 0:
                self.move = Actions.ROTATE_CCW
                roatations_needed += 1
            elif roatations_needed > 0:
                self.move = Actions.ROTATE_CW
                roatations_needed -= 1
            elif translations_needed.x > 0:
                self.move = Actions.MOVE_RIGHT
                translations_needed.x -= 1
            elif translations_needed.x < 0:
                self.move = Actions.MOVE_LEFT
                translations_needed.x += 1
            else:
                self.move = Actions.HARD_DROP
                self.next_move = None
                return
            self.next_move = BasicTetrisAI.Move(roatations_needed, translations_needed)

        def __repr__(self):
            return "Move(" + str(self.move) + ((", " + repr(self.next_move) + ")") if self.next_move is not None else ")")