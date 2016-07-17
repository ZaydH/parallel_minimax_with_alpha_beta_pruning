# -*- coding: utf-8 -*-
from __future__ import with_statement

#cloud_chess-minimax
import webapp2 #@UnresolvedImport
import time
import sys #@UnusedImport

from chess_utils import PlayerType
from chess_utils import ChessUtils

import pipeline
from pipeline import common
from google.appengine.api import memcache



class DetermineBestUtilAndMove(pipeline.Pipeline):
    """
    Only called by the MakeMove class.  Once the utility of all of
    the second level nodes have had their utilities determined,
    this function selects the move that provides either the minimum
    or maximum utility and returns it.
    
    Params:
    is_max - Whether the current node is a min or max node.
    current_best_util_and_move - Two index tuple of the best move and utility so far.
    valid_moves - Set of valid moves for the root
    utilities_and_moves_out_of_states - Utility associated with each of the moves.
    
    Returns: Tuple - Two element tuple representing the move with 
    the highest utility.
    """
    def run(self, is_max, current_best_util_and_move, valid_moves, 
            *utilities_and_moves_out_of_states): # " * " means that it is a variable array.  Needed for JSON Serializability.
        
        
        # Extract head of the list and use for comparison.
        best_move = valid_moves[0]
        best_util = utilities_and_moves_out_of_states[0][0]

        # Iterate through and find the best move.
        for i in xrange(1, len(valid_moves)):
            utility = utilities_and_moves_out_of_states[i][0]

            # Determine if best move needs to be updated
            if((is_max and utility > best_util) 
               or ((not is_max) and utility < best_util)):
                
                best_move = valid_moves[i]
                best_util = utility
        
        # Compare these new values to the best value so far.
        cur_best_util, cur_best_move = current_best_util_and_move
        if ((is_max and cur_best_util > best_util) 
           or ((not is_max) and cur_best_util < best_util)):
            best_move = cur_best_move
            best_util = cur_best_util
    
        # Return the move with the optimal utility.
        return best_util, best_move






class AddToMemCache(pipeline.Pipeline):
    """
    Pipeline Subtask to Add to Memcache
    
    To improve the efficiency of the program, write to memcache
    using a Pipeline API task.  That prevents writing to memcache
    being on the critical path.
    
    Params: 
    key - Memcache key for the board and player combination.
    utility_and_move - Two index Tuple.
                       Index 0: Utility of this state and move
                       Index 1: Move associated with the Utility
    current_depth - Current depth in the tree.
    
    Returns: None. 
    """
    def run(self, key, utility_and_move, current_depth):
        memcache_val = memcache.get(key) #@UndefinedVariable
        
        # Put into memcache only if the current depth is higher in the tree
        # than the value already in memcache.
        if(not memcache_val or memcache_val[1] > current_depth):
            memcache.add(key, (utility_and_move, current_depth)) #@UndefinedVariable


class MakeMoveIter(pipeline.Pipeline):
    """
    This pipeline will calculate all the utilities of the moves present in the vaid_moves.
    First It will iterate to all the elements of the batch size, and then make call to itself(same_function)
    and execute them while updating the value of alpha and beta. It will prune wherever it would be applicable.    
    
    By calling  DetermineBestUtilAndMove and then return the one with maximum utility
    and the move corresponding to it. 

    Also, it makes use of memcache. If the utility value of a specific child is already computed, then it would
    take that value from memcache instead of computing all over again.
   
    params:

    player - Player that is making the next move.
    board - Current board state.  List of list of integers.
    current_depth - The level at which the current child is at.
    tree_max_depth - Maximum level of the tree.
    use_memcache - If program uses memcache or not.
    alpha, beta - Range for Alpha beta pruning
    batch_size - size of batch of valid_moves computed before next batch is computed.
    best_util_and_move - Tuple of the best move and the utility for the current board/player so far.
    valid_moves - Set of unexplored valid chess moves for the current board and player.
    
    Returns: Two index tuple.
        Index 0: Utility of the best move.
        Index 1: Tuple of the best move.
    """
    def run(self, player, board, current_depth, is_max, tree_max_depth, use_memcache, alpha, beta, 
            batch_size, best_util_and_move, valid_moves):

        # Build the board tuple only once
        next_player = 1 - player      
        if(use_memcache):
            board_tuple = tuple([tuple(row) for row in board]) 

        # Update alpha or beta.
        if is_max:
            alpha = max(alpha, best_util_and_move[0])
        else:
            beta = min(beta, best_util_and_move[0])

        # Determine if the tree can be pruned.
        if(beta <= alpha or not valid_moves or \
           (use_memcache and MakeMoveIter.check_memcache_for_pruning(next_player, board_tuple, is_max, \
                                                                     valid_moves, current_depth, alpha, beta))):
            
            # Fan in as no more nodes can/should be explored.
            yield common.Return(best_util_and_move)
    
        # Tree cannot be pruned yet so do the next batch_size of children.
        else:

            # Select the next set of moves to explore.
            end_index = min(batch_size, len(valid_moves))
            valid_moves_batch = valid_moves[:end_index]
            all_utils_and_moves = []

            # Iterate through the moves in this batch.
            for new_move in valid_moves_batch:

                generate_move_children = True # By default expand the move's children.

                # If using memcache, try to extract a value.                
                if use_memcache:
                    tuple_of_args = (next_player, tuple(new_move), board_tuple, not is_max)
                    args_hash = str(hash(tuple_of_args))
                    #get the utility from the memcache.
                    utility_move_and_subtree_depth = memcache.get(args_hash) #@UndefinedVariable

                    # If utility and move are valid, then store the values and do not expand.
                    if(utility_move_and_subtree_depth and utility_move_and_subtree_depth[1] <= current_depth):
                        
                        utility_and_move = utility_move_and_subtree_depth[0]
                        all_utils_and_moves.append(utility_and_move)
                        generate_move_children = False
                
                # If selected, expand the move's children.
                if(generate_move_children):
                    utility_and_move = yield(InnerMakeMove(next_player, \
    	                                                   new_move, \
    	                                                   board, \
    	                                                   current_depth + 1, \
    	                                                   not is_max,
    	                                                   tree_max_depth, 
    	                                                   use_memcache,
    	                                                   alpha,
    	                                                   beta,
    	                                                   batch_size))
                    # Add to memcache
                    if use_memcache:
                        yield AddToMemCache(args_hash, utility_and_move, current_depth)
                    all_utils_and_moves.append(utility_and_move)
                    
            # Combine best move so far with newly expanded nodes.
            best_util_and_move = yield DetermineBestUtilAndMove(is_max, best_util_and_move, 
                                                                valid_moves_batch, *all_utils_and_moves)
            
            # Build the remaining portion of the tree.
            remaining_valid_moves = valid_moves[end_index:] # Select the unsearched moves and build the remaining tree.
            yield MakeMoveIter(player, board, current_depth, is_max, tree_max_depth, use_memcache, 
                               alpha, beta, batch_size, best_util_and_move, remaining_valid_moves)
    
    @staticmethod
    def check_memcache_for_pruning(next_player, board_tuple, is_max, valid_moves, current_depth,
                                   alpha, beta):
        """
        Iterate through the remaining moves in memcache.  If the tree can be pruned,
        then return true for the valid pruning. Otherwise, return false.
        
        next_player: Player whose turn is next.
        board_tuple: Tuple of the board used in hash for memcache
        is_max: True if the current player is max, false otherwise.
        valid_moves: Set of remaining valid moves for this state.
        current_depth: Current location in the tree. 
        alpha: Value of alpha in alpha-beta pruning.
        beta: Value of alpha in alpha-beta pruning.
        
        Returns: True if the prune can be pruned based off memcache.  False otherwise.
        """
    
        # Iterate through all the moves.
        for temp_move in valid_moves:
            
            # Build the args hash.
            tuple_of_args = (next_player, tuple(temp_move), board_tuple, not is_max)
            args_hash = str(hash(tuple_of_args))
            
            #get the utility from the memcache.
            util_and_depth = memcache.get(args_hash) #@UndefinedVariable

            if(util_and_depth is not None and util_and_depth[1] <= current_depth):
                
                # Update alpha or beta.
                if is_max:
                    alpha = max(alpha, util_and_depth[0][0])
                else:
                    beta = min(beta, util_and_depth[0][0])
                    
                # Check if you can prune.
                if(alpha >= beta):
                    return True
        # No good depth found so cannot prune.
        return False


class MakeMove(pipeline.Pipeline):
    """
    Constitutes the root of the Minimax decision tree.  It spawns 
    the successor tasks at depth 1 of the decision tree.  This class 
    returns a move which is a two element Tuple.
    
    Params:
    player - Player that is making the next move.
    board - Current board state.  List of list of integers.
    tree_max_depth - Maximum level of the tree.
    use_memcache - If "True", program uses memcache.  It does not use it otherwise,
    alpha, beta - Range for Alpha beta pruning
    Batch_size - size of batch of valid_moves computed before next batch is computed
    
    Returns: Two element Tuple for a move.  Format of the a move is:
    (SourceLocation, DestinationLocation)
    """
    def run(self, player, board, tree_max_depth, use_memcache, alpha, beta, batch_size):
        
        # Extract the set of possible moves for this level of the board.
        is_check, valid_moves = ChessUtils.get_valid_moves(player, board)
        
        # Check that the game did not start in an invalid condition.
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

            # Define the best move and util so far.
            best_util_so_far = alpha if is_max else beta
            best_util_and_move = (best_util_so_far, None)

            # Generate the Minimax tree.
            yield MakeMoveIter(player, board, 1, is_max, tree_max_depth, use_memcache,
                               alpha, beta, batch_size, best_util_and_move, valid_moves)


class InnerMakeMove(pipeline.Pipeline):
    """
    An inner processing class.  It is performs the �Terminal-Test� described in classic
    Minimax Algorithm from Russell and Norvig.  If the test returns true, it runs the 
    �Utility� function to determine the state�s utility, Otherwise, it generates 
    the successor objects of type �MakeMoveIter�.
    
    Params:
    player - Player that is making to make the move in this turn.
    move - Queued move to be made.
    last_board - Current board state.  List of list of integers. Note move has not been applied
    to this object. 
    tree_level - Depth in the tree. This is used to prevent the tree getting too large.
    is_max - Whether the current node is a min or max node.
    tree_max_depth - Maximum level till which tree can grow.
    use_memcache - If we want to use memcache or not.
    alpha - Max parameter for Alpha-beta Pruning
    beta - Min parameter of Alpha-beta Pruning
    batch_size - size of batch of valid_moves computed before next batch is computed
    
    Returns: Integer representing the utility of this node/state and a tuple of move having this utility.
    """
    def run(self, player, move, last_board, tree_level, is_max, tree_max_depth, use_memcache, alpha, beta, batch_size):
        new_board = ChessUtils.make_move(move, last_board)

        # Extract the set of possible moves for this level of the board.
        is_check, valid_moves = ChessUtils.get_valid_moves(player, new_board)
        
        # By default, continue recursing.
        end_recursion = False 
        # Two recursion stop conditions.
        #------- Condition #1: Recursion Depth of maximum_depth of the tree.
        #------- Condition #2: No more valid player moves.
        if tree_level >= tree_max_depth or len(valid_moves) == 0: 
            end_recursion = True
        
        
        # Ensure only one yield is generated in the case of recursions end so exit.
        if(end_recursion):
            yield common.Return((ChessUtils.get_state_utility(new_board, player, is_max,
		                                                      is_check, valid_moves), None))
        # If child modes will be generated, then generate them as a fan-out then fan them back in.
        else:
            best_util_so_far = alpha if is_max else beta
            best_util_and_move = (best_util_so_far, None)
            yield MakeMoveIter(player, new_board, tree_level, is_max, tree_max_depth, use_memcache, 
                               alpha, beta, batch_size, best_util_and_move, valid_moves)


class MainPage(webapp2.RequestHandler):   
    """
    Inherits the Google App Engine webapp2 class which is a 
    lightweight web server.  This class is the sole interface between
    the client application and the Pipeline API.  It only supports
    HTTP POST requests.  The response to the POST request is then a move
    which is a two element tuple in the form:
    
    Returns: A two integer comma separated string of the best move.
    """
    # Process the client POST command.
    def post(self):
        
        # Extract the POST information from the client.
        current_player = int(self.request.POST.get("current_player"))
        board_str = self.request.POST.get("board")
        tree_max_depth = int(self.request.POST.get("tree_max_depth", 2))         
        use_memcache = (self.request.POST.get("use_memcache", "True") == "True")  
        # Default batch size is fully parallel 
        batch_size = int(self.request.POST.get("batch_size", sys.maxint))        
        
        # Rebuild the board from the string passed in the message.
        split_on_header = board_str.split("[[")
        board_row_strings = split_on_header[1].replace("]]","").split("], [")
        board = []
        # Parse the rows
        for row_string in board_row_strings:
            split_row = row_string.split(", ")
            new_row = []
            # Parse the individual cells in a row.
            for cell in split_row:
                new_row.append(int(cell))
            board.append(new_row)
        
        # Define alpha and beta starting values for alpha beta pruning.
        alpha = -sys.maxint
        beta = sys.maxint
        
        # Define the Minimax setup.
        best_move_job = MakeMove(current_player, board, tree_max_depth,
                                 use_memcache, alpha, beta, batch_size)
        
        # Start the best move job.
        best_move_job.start()
        
        # Get the Job ID for later rechecking.
        best_move_job_id = best_move_job.pipeline_id
        
        # Essentially a Do-While.  Wait for job to finish.
        while True:
                       
            # Extract the job information, specifically if it is completed
            best_move_job = MakeMove.from_id(best_move_job_id)
            
            # If the job is done, stop looping.
            if(best_move_job.has_finalized):
                break 
            else:
                time.sleep(1)
        
        _, best_move = best_move_job.outputs.default.value # Only care about the move in the return.
        
        # Return the best move to the client.
        self.response.write(str(best_move[0]) + "," + str(best_move[1]))


# Runs the webserver through the "MainPage" class.
application = webapp2.WSGIApplication( [('/', MainPage),], debug=False)
