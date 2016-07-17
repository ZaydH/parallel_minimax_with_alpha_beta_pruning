from chess_utils import PlayerType
from chess_utils import ChessUtils

from determine_best_util_and_move import DetermineBestUtilAndMove

import pipeline
import random

class ExpectiMaxMakeMove(pipeline.Pipeline):
    def run(self, player, board, depth_tree, batch_size, rationality_prob):
        # Extract the set of possible moves for this level of the board.
        is_check, valid_moves = ChessUtils.get_valid_moves(player, board)
        
        if(is_check and len(valid_moves) == 0):
            raise ValueError("Game starting in checkmate.  That is now allowed...")
        
        # If no moves were found to be valid, return an error message.
        if(len(valid_moves) == 0):
            yield common.Return("ERROR - NO VALID MOVES")
        # If only one move is possible, return that.
        elif(len(valid_moves) == 1):
            yield common.Return((0, valid_moves[0]))
        # If there are multiple valid moves, iterate through the possible valid moves.
        else:
            # Determine whether white or black is going first.
            if(player == PlayerType.WHITE):
                is_max = True
            else:
                is_max = False 
            yield InnerExpectiMaxMakeMove(player, None, board, 1, is_max, depth_tree, batch_size)


class InnerExpectiMaxMakeMove(pipeline.Pipeline):
    def run(self, player, move, board, tree_level, is_max, depth_tree, batch_size, rationality_prob):
        if move:
            board = ChessUtils.make_move(move, board)

        # Extract the set of possible moves for this level of the board.
        is_check, valid_moves = ChessUtils.get_valid_moves(player, board)

        # By default, continue recursing.
        end_recursion = False 
        # Two recursion stop conditions.
        #------- Condition #1: Recursion Depth of 6
        #------- Condition #2: No more valid player moves.
        if tree_level >= depth_tree or len(valid_moves) == 0: 
            end_recursion = True

        # Ensure only one yield is generated in the case of recursions end so exit.
        if end_recursion:
            yield common.Return((ChessUtils.get_state_utility(board, player, is_max, \
                                                              is_check, valid_moves), None))
            return

        if len(valid_moves) == 1:
            yield common.Return((ChessUtils.get_state_utility(board, player, is_max, \
                                                              is_check, valid_moves), valid_moves[0]))
            return

        next_player = 1 - player
        is_next_player_max = not is_max
        utilities_and_moves = []
        for new_move in valid_moves:
            utility_and_move = yield InnerExpectiMaxMakeMove(next_player, \
    	                                                     new_move, \
    	                                                     board, \
    	                                                     tree_level + 1, \
    	                                                     is_next_player_max,
    	                                                     depth_tree, # Required as part of the player increment.
    	                                                     batch_size,
                                                             rationality_prob)
            utilities_and_moves.append(utility_and_move)
        if tree_level == 2:
          yield DetermineExpectiMaxUtilAndMove(is_max, valid_moves, rationality_prob, *utilities_and_moves)
        else:
          yield DetermineBestUtilAndMove(is_max, valid_moves, *utilities_and_moves)


class DetermineExpectiMaxUtilAndMove(pipeline.Pipeline):
    def run(self, is_max, valid_moves, rationality_prob, *utilities_and_best_moves_out_of_states):
        # Extract head of the list and use for comparison.
        best_move = valid_moves[0]
        best_util = utilities_and_best_moves_out_of_states[0][0]

        # Iterate through and find the best move.
        for i in xrange(1, len(valid_moves)):
            utility = utilities_and_best_moves_out_of_states[i][0]
            # Determine if best move needs to be updated
            if((is_max and utility > best_util) 
               or ((not is_max) and utility < best_util)):
                best_move = valid_moves[i]
                best_util = utility

        rest_moves = []
        rest_util = 0
        for i, valid_move  in enumerate(valid_moves):
            utility = utilities_and_best_moves_out_of_states[i][0]
            if((is_max and utility < best_util) 
               or ((not is_max) and utility > best_util)):
                rest_moves.append(valid_move)
                rest_util += utility
        expected_utility = rationality_prob*best_util + ((1. - rationality_prob)*rest_util/(len(rest_moves)))
        chosen_move = None
        if random.random() <= rationality_prob:
          chosen_move = best_move
        else:
          chosen_move = random.choice(rest_moves)
        return expected_utility, chosen_move
