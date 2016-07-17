'''
Created on Mar 20, 2015

@author: dsmith
@author: ggarg
@author: zhammoud

'''

import os
import sys
import urllib, urllib2
import threading
import Queue
import time
#import codecs 
#reload(sys)  # Needed to set default encoding
#sys.setdefaultencoding('utf-8')  # @UndefinedVariable
#print sys.stdout.encoding

from chess_utils import PlayerType
from chess_utils import ChessUtils
from chess_utils import ChessPiece


#server_url = "http://localhost:9999"
server_url = "http://cs218-team2-chess-minimax.appspot.com"
two_player_debug = False
tree_max_depth = 2
batch_size = 30
rationality_prob = 0.80
use_expectimax = False
print_move_time = False
    
def parse_board(lines):
    '''
    Parse the board from the input file. and return board 
    and the current player
    
    Returns: Type - Tuple
        * Index 0: Current Player (0 or 1)
        * Index 1: Board List of lists.
    
    
    >>> parse_board(["0","0,5,0","11,13, 4"])
    Traceback (most recent call last):
     ...
    ValueError: Invalid board size. It should be a square
    
    >>> parse_board(["0","0,5,0","11,13, 4","0,0,0"])
    Traceback (most recent call last):
     ...
    ValueError: Invalid board. Each player must have exactly one king.
    
    >>> parse_board(["0","0,5,6","11,13, 4","6,0,0"])
    Traceback (most recent call last):
     ...
    ValueError: Invalid board. Each player must have exactly one king.
    
    >>> parse_board(["0","0,5,0","11,13, 4","16,0,0"])
    Traceback (most recent call last):
     ...
    ValueError: Invalid board. Each player must have exactly one king.
    
    >>> parse_board(["0","0,5,16","11,13, 4","16,0,0"])
    Traceback (most recent call last):
     ...
    ValueError: Invalid board. Each player must have exactly one king.
    >>> parse_board(["2","0,5,16","11,13, 4","16,0,0"])
    Traceback (most recent call last):
     ...
    ValueError: File error: Starting player value must be either 0 or 1
    
    >>> parse_board(["2","0,5,6","11,13, 4","16,0,0"])
    Traceback (most recent call last):
     ...
    ValueError: File error: Starting player value must be either 0 or 1

    >>> parse_board(["0","0,5,6","11,13, 4","16,test,0"])
    Traceback (most recent call last):
     ...
    ValueError: The string: "test" could not be converted to an integer for a chess piece.
   
    >>> parse_board(["0","0,5,6","11,13, 4","16,0,0"])
    (0, [[0, 5, 6], [11, 13, 4], [16, 0, 0]])
   
    >>> parse_board(["0","0,5,6","11,13, 4","16,0,0"])
    (0, [[0, 5, 6], [11, 13, 4], [16, 0, 0]])
    
    '''
    try:
        current_player = int(lines[0])
    except ValueError:
        raise ValueError("The string: \"" + lines[0] + "\" could not be converted to an integer for player type.")
        
    if(current_player != PlayerType.BLACK and current_player != PlayerType.WHITE):
        raise ValueError("File error: Starting player value must be either 0 or 1")
    
    
    row = len(lines)-1
    kw = 0
    kb = 0
    board = []
    for line in lines[1:]:
        pieces = line.split(",")
        
        if len(pieces) != row:
            raise ValueError("Invalid board size. It should be a square")

        # Append to the integers to the board but ensure they can be casted correctly.
        try:
            board.append([int(x) for x in pieces]) 
        except ValueError:
            raise ValueError("The string: \"" + x + "\" could not be converted to an integer for a chess piece.")
        
        for piece_player in pieces:

            piece = ChessUtils.get_piece(int(piece_player))
            player = ChessUtils.get_player(int(piece_player))
                
            if player == PlayerType.WHITE and piece == ChessPiece.KING:
                kw += 1
            if player == PlayerType.BLACK and piece == ChessPiece.KING:
                kb += 1

    # Error Check
    if kb != 1 or kw != 1:
        raise ValueError("Invalid board. Each player must have exactly one king.")
        
    return current_player, board
    
    
    
    
#def execute_server_command(current_player, board, queue, tree_max_depth, batch_size, rationality_prob, use_expectimax):
def execute_server_command(current_player, board, queue, tree_max_depth, batch_size):
    """
    Execute server command is a dedicated function to make an HTTP
    post request of the server and then wait for its response.  It is placed
    in a dedicated function so that a thread can be used.  While waiting for the server
    response, the client will display asterisks to the screen to let the user know
    that the process is not dead.
    
    Params:
    current_player: Integer - Current player's turn.
    board: List of list of integers - Current board.
    queue: Used to pass the results of the thread back to the main process.
    
    Returns: Nothing directly.  The computer move is pushed onto the queue.
    """
    
    
    # This data is passed to the Google App Engine Server via a post.
    board_data_dict = {'current_player': str(current_player),
                       'board' : str(board),
                       'tree_max_depth': str(tree_max_depth),
                       #'rationality_prob': str(rationality_prob),
                       #'use_expectimax': use_expectimax,
                       'batch_size': str(batch_size)}
    # Encode the board data for sending to the server.
    post_board_data = urllib.urlencode(board_data_dict)
    # Build the server request.
    server_request = urllib2.Request(server_url, post_board_data)
    
    # Make the request and wait for a response.
    try:
        t0 = time.time()
        server_response = urllib2.urlopen(server_request)
        if(print_move_time): print "\nThe computer took %.1f seconds to make its move.\n" % (time.time() - t0)
    except Exception as e:
        print "\n\nNetwork communication error {0}.  Exiting...".format(repr(e))
        sys.exit(0)
        
    # Get the server request
    unparsed_move = server_response.read()
    parsed_move = unparsed_move.split(",")
    computer_move = (int(parsed_move[0]), int(parsed_move[1])) #@UnusedVariable
    
    # Put the move onto the queue.
    queue.put(computer_move)
    
        
def query_server(current_player, board):
    """
    Makes a request of the server to get the computer's
    move. 
    
    Params:
    current_player : Integer - 0 for white and 1 for black.
    board - List of list of integers of the pieces on the board.
    
    Returns: Tuple of two integers.  Index 0 in the Tuple is the 
    current (i.e. source) location of the piece to be moved
    while index 1 is the new (i.e. destination) location of the piece.
    """
    
    sys.stdout.write("The computer is thinking about its move  ")
    
    # Create a queue to get the computers move.
    moveQueue = Queue.Queue()

    # Use a thread to get the player's move.
    #server_thread = threading.Thread(target=execute_server_command, args=(current_player, board, moveQueue, tree_max_depth, batch_size, rationality_prob, use_expectimax))
    server_thread = threading.Thread(target=execute_server_command, args=(current_player, board, moveQueue, \
                                                                          tree_max_depth, batch_size))
    
    server_thread.start()
    # Wait for the thread to finish
    while(server_thread.is_alive()):
        sys.stdout.write("*****")
        time.sleep(1)
    sys.stdout.write("\n\n")
    
    # Handle the error case where the network communication crashed.
    if(moveQueue.empty()):
        sys.exit()
    
    computer_move = moveQueue.get(True)
    
    # Allow for two player debug
    if(two_player_debug):
        _, valid_moves = ChessUtils.get_valid_moves(current_player, board)
        computer_move = make_player_move(False, valid_moves, board) # Use player make move as a placeholder.
    return computer_move




   
def make_player_move(check, valid_moves, board):
    """
    Handles the error checking and printing associated with a player
    making a move.
    
    Params:
    current_player : Integer - 0 for white and 1 for black.
    board - List of list of integers of the pieces on the board.
    
    Returns: Tuple of two integers.  Index 0 in the Tuple is the 
    current (i.e. source) location of the piece to be moved
    while index 1 is the new (i.e. destination) location of the piece.
    """
    
    # Keep looping until a valid move is entered.
    next_move = (-1, -1)
    while(next_move not in valid_moves):
        
        next_move = (-1, -1) # Reset next move to a dummy value
        
        if check:
            print "You are in check.  You must enter a move to exit check.\n"
        else:
            print "Its your turn.\n"
        print "Your move should be in the format of two integers separated by a comma."
        print "The first number is the current location of the piece you want to move,"
        print "and the second number is the new location of the piece after the move.\n"
        print "Enter your move: ",
        
        # Get the user text.
        move_text = sys.stdin.readline().strip()
        
        # Split move on comma.
        temp_move = move_text.replace(" ","").split(",")

        # Parse the move.
        if(len(temp_move) == 2):
            try:
                source_loc = int(temp_move[0])
                dest_loc = int(temp_move[1])
                next_move = (source_loc, dest_loc)
                valid_move_text = True
            except:
                # Unable to parse to integer
                valid_move_text = False
        else:
            valid_move_text = False 
        
        # Print messages if the moves are not valid
        if(not valid_move_text):
            print "\nIt does not appear the entered move \"" + move_text + "\" is in the correct format.  Please try again...\n\n"
            ChessUtils.print_board(board)
        # Verify the move is in the move array.
        elif(next_move not in valid_moves):
            print "\nThe specified is not allowed given the current board.  Check your move and try again.\n"
            ChessUtils.print_board(board)   

    # Return the move.
    return next_move 
        
    
        
def play_game(current_player, human_player, board):
    '''
    
    Params:
    current_player: Integer - 0 or 1 to indicate whether it is 
    white's or black's turn to start the game.
    
    human_player: Integer - 0 or 1 indicates whether the human player
    is white or black.  This value should not change.
    
    board: List of lists of integers.  It contains the current board.
    It will be updated at the end of each turn.
    
    Returns: 
    This function runs and never returns.  The program exits directly 
    from this function.
    ''' 
    while(True):
        
        check, valid_moves = ChessUtils.get_valid_moves(current_player, board)
        # Check if the game is over.
        if check and len(valid_moves) == 0:
            ChessUtils.print_board(board)
            print "\nCheckmate!"
            if current_player == human_player:
                print "The computer won!  You lose!"
            else:
                print "You win!"
            sys.exit(0)

        # Check if the game is over due to stalemate.
        elif(not check and len(valid_moves) == 0):
            print "\nStalemate!\n"
            print "No moves possible so its a draw!"
            sys.exit(0)
        
        # Print the current board
        print "\n\nCurrent Board:"
        ChessUtils.print_board(board)
        
        # Human's turn.
        if(current_player == human_player):
            # Keep loop until the user enters a valid move.
            next_move = make_player_move(check, valid_moves, board)

        # Computer's turn.
        else:
            if check:
                print "The computer is in check.  It must enter a move to exit check:\n"
            else:
                print "Its the computer's turn.  It is deciding on its move.\n"
            
            next_move = query_server(current_player, board)
            
            # Print the computer's move.
            print "The computer's move is:  (" + str(next_move[0]) + \
                                              ", " + str(next_move[1]) + ")\n"
        
        board = ChessUtils.make_move(next_move, board) # Apply the move.
        current_player = 1 - current_player # update the player
        
    pass       

def main():
    """
    Main client function.  All subsequent calls are made from this function 
    or from functions called by this function.
    
    Params: None
    
    Returns: This function never returns.  Either sys.exit is called directly
    by this function or by one of its subfunctions.
    """
    
    print "\n\nWelcome to the CS218 Spring 2015 Team #2 Chess Playing Program"
    print "\nTeam Members: David Smith, Geetika Garg, and Zayd Hammoudeh\n\n"
    print "Loading the board file...\n\n"
        
    # Error check the inputs.  Ensure a board file was specified.
    if(len(sys.argv) == 1):
        print "No board file was specified.  Exiting."
        sys.exit(0)
        
    # Error check the inputs.  Ensure a board file was specified.
    elif(len(sys.argv) > 2):
        print "Invalid input arguments.  Only a single board file can be specified. Exiting."
        sys.exit(0)
    # Error check the board file exists.
    elif(not os.path.isfile(sys.argv[1])):
        print "The specified board file: \"" + sys.argv[1] + "\" does not appear to exist.  Please check your system and try again."
        sys.exit(0)
    
    # Load the board.
    file_name = sys.argv[1]
    lines = open(file_name).readlines()
    current_player, board =  parse_board(lines)
    print "Board file successfully loaded.\n"
    print "The starting board is:"
    ChessUtils.print_board(board)
    print "\n\n"
    
    # Let the human select whether they are playing black or white.
    human_player = ""
    while(human_player != "0" and human_player != "1"):
        print "Select whether you are playing white or black."
        print "Enter \"0\" for white or \"1\" for black:  ",
        human_player = sys.stdin.readline().strip().replace(" ","") # Take trailing characters and new line off.
        
        if(human_player != "0" and human_player != "1"):
            print "\nInvalid input: \"" + human_player + "\""
            print "A valid input for player color is required before continuing.\n"

    # Convert the string version of player to the integer version. 
    human_player = int(human_player)
    if(human_player == PlayerType.WHITE):
        print "\nYou selected to play as white."
    else:
        print "\nYou selected to play as black."
    print "Starting the game...\n"
    
    # Run the game.
    play_game(current_player, human_player, board)



# Execute the main function.
if(len(sys.argv) == 2 and sys.argv[1] == "doctest"):  
    import doctest
    doctest.testmod()
else:
    main() 
