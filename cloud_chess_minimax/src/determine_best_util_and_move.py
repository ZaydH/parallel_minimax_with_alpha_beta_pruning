import pipeline


class DetermineBestUtilAndMove(pipeline.Pipeline):
    """
    Only called by the MakeMove class.  Once the utility of all of
    the second level nodes have had their utilities determined,
    this function selects the move that provides either the minimum
    or maximum utility and returns it.
    
    Params:
    is_max - Whether the current node is a min or max node.
    valid_moves - Set of valid moves for the root
    move_utilities - Utility associated with each of the moves.
    
    Returns: Tuple - Two element tuple representing the move with 
    the highest utility.
    """
    def run(self, is_max, valid_moves, *utilities_and_best_moves_out_of_states): # " * " means that it is a variable array.  Needed for JSON Serializability.
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
        # Return the move with the optimal utility.
        return best_util, best_move
