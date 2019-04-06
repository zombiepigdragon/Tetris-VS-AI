from tetris_core import Actions, Translation
import random
from pygame.time import get_ticks

class BasicTetrisAI:
    def __init__(self, board, difficulty):
        self.board = board
        self.last_time = get_ticks()
        self.difficulty = difficulty
        self.set_next_move_time()

    def set_next_move_time(self):
        raw_time = 1000 / self.difficulty
        offset = raw_time / 10
        min_time = raw_time - offset
        max_time = raw_time + offset
        self.next_move_time = random.randrange(min_time, max_time)

    def run(self):
        if get_ticks() - self.last_time > self.next_move_time:
            #Check for next move set, then execute or share
            self.last_time = get_ticks()
            self.set_next_move_time()

    def set_next_move(self):
        pass #Find the ideal moves for current piece, then save them

    class Move:
        def __init__(self, roatations_needed, translations_needed):
            if roatations_needed > 0:
                self.move = Actions.ROTATE_CCW
                roatations_needed -= 1
            elif roatations_needed < 0:
                self.move = Actions.ROTATE_CW
                roatations_needed += 1
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