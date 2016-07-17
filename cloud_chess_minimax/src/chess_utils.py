'''
Created on Mar 27, 2015

'''


import random #@UnusedImport
import sys #@UnusedImport
import copy


class PlayerType:
    WHITE = 0 # White colored pieces move first in class.
    BLACK = 1
    
class ChessPiece:
    BLANK= 0
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6


class ChessUtils():
    
    @staticmethod
    def print_board(board):
        '''
        Prints the board
        
        Params:
        board - List of list of integers of the board pieces.
        
        Returns: None
        
        >>> ChessUtils.print_board([[0, 1], [21, 1]])
        Traceback (most recent call last):
         ...
        ValueError: The number "21" does not correspond to a valid color.
        
        >>> ChessUtils.print_board([[0, 1], [7, 1]])
        Traceback (most recent call last):
         ...
        ValueError: The number "7" does not correspond to a valid piece.
        '''
        break_string = ""
        print "" # Insert a blank line.
        for row_cnt in xrange(0, len(board)):
            break_string = "\t" + "+"
            row_string = "\t" + '|'
            for number in board[row_cnt]:
                cur_piece = ChessUtils.get_piece(number)
                cur_color = ChessUtils.get_player(number)
                
                # Set utf code offset for king.
                utf_code = 9812
                unicode_char = ""
                if(cur_color == PlayerType.BLACK):
                    utf_code += 6
                    unicode_char = "B"
                else:
                    unicode_char = "W"
                # Increment UTF code ID for piece type
                if(cur_piece == ChessPiece.KING):
                    utf_code += 0
                    unicode_char += "K"
                elif(cur_piece == ChessPiece.QUEEN):
                    utf_code += 1
                    unicode_char += "Q"
                elif(cur_piece == ChessPiece.ROOK):
                    utf_code += 2
                    unicode_char += "R"
                elif(cur_piece == ChessPiece.BISHOP):
                    utf_code += 3
                    unicode_char += "B"
                elif(cur_piece == ChessPiece.KNIGHT):
                    utf_code += 4
                    unicode_char += "N"
                elif(cur_piece == ChessPiece.PAWN):
                    utf_code += 5
                    unicode_char += "P"
                elif(cur_piece != ChessPiece.BLANK):
                    raise ValueError("Invalid piece \"" + number + "\" in board print.")
                
                #unicode_char = unichr(utf_code) 
                
                if(number == ChessPiece.BLANK):
                    row_string += "\t" +'|'
                else:
                    row_string += '  ' + unicode_char +"\t" +'|'
                break_string += "------\t+"
            print break_string
            print row_string
        print break_string + "\n"


    @staticmethod
    def make_move(move, board):
        '''
        This function takes a board and move, and updates the board 
        to reflect the effects of the move.
        
        Creates a new board. This purposely doesn't modify the original board so that the 
        new board can be used for purposes of testing check

        Params:
        move - Tuple of two integers showing move in the format (SourceLocation, DestinationLocation)
        board - List of list of integers of the pieces on the board.
        
        Returns: Deep copy of the original board with the move applied.
        
        >>> ChessUtils.make_move((0,3), [[1,0],[0,0]])
        [[0, 0], [0, 1]]
        >>> ChessUtils.make_move((7,8), [[1,0,5,6],[0,0,3,4],[11,4,12,13],[11,4,12,13]])
        [[1, 0, 5, 6], [0, 0, 3, 0], [4, 4, 12, 13], [11, 4, 12, 13]]
        >>> ChessUtils.make_move((15,8), [[1,0,5,6],[0,0,3,4],[11,4,12,13],[11,4,12,13]])
        [[1, 0, 5, 6], [0, 0, 3, 4], [13, 4, 12, 13], [11, 4, 12, 0]]
        
        >>> ChessUtils.make_move((1,3), [[1,0],[0,0]])
        Traceback (most recent call last):
         ...
        ValueError: There is not a source piece at the location: 1
        
        >>> ChessUtils.make_move((-1,3), [[1,0],[0,0]])
        Traceback (most recent call last):
         ...
        ValueError: The move source location "-1" is invalid.  Valid move is from 0 to 3
        
        >>> ChessUtils.make_move((-1,4), [[1,0],[0,0]])
        Traceback (most recent call last):
         ...
        ValueError: The move source location "-1" is invalid.  Valid move is from 0 to 3
        
        >>> ChessUtils.make_move((2,4), [[1,0],[0,0]])
        Traceback (most recent call last):
         ...
        ValueError: The move destination location "4" is invalid.  Valid move is from 0 to 3
        
        >>> ChessUtils.make_move((2,2), [[1,0],[0,0]])
        Traceback (most recent call last):
         ...
        ValueError: The move source and destination locations cannot be the same.
        '''
        board_len = len(board)
    
        # Verify a valid move
        if(move[0] < 0 or move[0] >= board_len*board_len):
            raise ValueError("The move source location \"" + str(move[0]) + "\" is invalid.  Valid move is from 0 to " \
                             + str(board_len * board_len -1)) 
        if(move[1] < 0 or move[1] >= board_len*board_len):
            raise ValueError("The move destination location \"" + str(move[1]) + "\" is invalid.  Valid move is from 0 to " \
                             + str(board_len * board_len -1)) 
        if(move[0]==move[1]):
            raise ValueError("The move source and destination locations cannot be the same.")
    
        # Get the source and destination rows and columns 
        row_s = move[0] // board_len
        col_s = move[0] % board_len
        row_d = move[1] // board_len
        col_d = move[1] % board_len
        
        # Verify a valid move
        if( board[row_s][col_s] == 0 ):
            raise ValueError("There is not a source piece at the location: " + str(move[0]))
        
        # Make a deep copy of the original board.
        new_board = copy.deepcopy(board)
        
        # Store the piece set its location to zero and then place in destination
        new_board[row_d][col_d] = new_board[row_s][col_s]
        new_board[row_s][col_s] = 0
        
        return new_board

        
    @staticmethod
    def in_bounds(spot, board):
        """
        Determines if a spot is in the bounds of the board
        
        Params:
        spot - an (x,y) tuple
        board - Current board state.
        
        Returns:
        True if the spot is in the bounds of the board
        
        >>> ChessUtils.in_bounds((0,0),[[0,0],[0,1]])
        True
        
        >>> ChessUtils.in_bounds((0,2),[[0,0],[0,1]])
        False
    
        >>> ChessUtils.in_bounds((0,2),[[0,0,0],[0,1,0],[0,3,4]])
        True
        
        >>> ChessUtils.in_bounds((-1,3),[[0,0,0],[0,1,0],[0,3,4]])
        False
        """
        x = spot[0];
        y = spot[1];
        if ((x < 0) or (y < 0)):
            return False
        if ((y >= len(board)) or (x >= len(board[0]))):
            return False
        return True
        
    @staticmethod
    def in_check(current_player, board):        
        """
        Finds the King of current_player and determines if it is in check
        
        Params:
        current_player - Current player's turn
        board - Current board state.
        
        Returns:
        True if in check and False otherwise
        
        >>> ChessUtils.in_check(0, [[6, 0, 0], [0, 0, 0], [16, 0, 15]])
        True
        
        >>> ChessUtils.in_check(0, [[6, 0, 0], [0, 0, 0], [0, 16, 15]])
        True
        
        >>> ChessUtils.in_check(1, [[0,2,0,6],[0,0,0,0],[0,0,0,0],[12,0,16,0]])
        False
        
        >>> ChessUtils.in_check(1, [[0,0,2,6],[0,0,0,0],[0,0,0,0],[12,0,16,0]])
        True
        
        >>> ChessUtils.in_check(1, [[0,2,0,6],[0,0,0,0],[3,0,0,0],[12,0,16,0]])
        True
        
        >>> ChessUtils.in_check(0, [[0,2,0,6],[0,0,0,0],[0,15,0,0],[12,0,16,0]])
        True
        
        """
        
        #note: assumes pawns of player WHITE can only move down
        #and pawns of player BLACK can only move up
        #but that can be changed here:
        downpawn = PlayerType.WHITE
        uppawn = PlayerType.BLACK
        
        opponent = abs(current_player - 1);
        
        #find the location of king of current_player on the board:
        height = len(board);
        width = len(board[0]);
        k_x = 0; # for holding x coordinate of the king
        k_y = 0; # for holding y coordinate of the king
        notfound = True;
        our_king = current_player*10 + ChessPiece.KING;
        while (notfound and (k_y < height)):
            while (notfound and (k_x < width)):
                if (board[k_y][k_x] == our_king):
                    notfound = False;
                else:
                    k_x = k_x + 1;
            if (notfound):
                k_x = 0;
                k_y = k_y + 1;
        
        #find the values of the opponent players:
        pawn = opponent*10 + ChessPiece.PAWN;
        rook = opponent*10 + ChessPiece.ROOK;
        knight = opponent*10 + ChessPiece.KNIGHT;
        bishop = opponent*10 + ChessPiece.BISHOP;
        queen = opponent*10 + ChessPiece.QUEEN;
        king = opponent*10 + ChessPiece.KING;
        
        #systematically check around the king to see if it's in check
        
        #first, check for knights of the opposing player:
        #kn_spots is spots where the knight would put the king in check
        kn_spots = [(-1,-2),(-2,-1),(1,-2),(2,-1),(2,1),(1,2),(-1,2),(-2,1)]
        for kn in kn_spots:
            test_spot = [kn[0] + k_x, kn[1] + k_y];
            if (ChessUtils.in_bounds(test_spot, board)):
                test_piece = board[test_spot[1]][test_spot[0]];
                if (test_piece == knight):
                    return True;       
                
        #now check in the eight directions around the king for other players:
        
        #left 
        x = k_x - 1;
        y = k_y;
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == king)):
            return True;
        while (ChessUtils.in_bounds((x,y),board) and board[y][x] == 0):
            x -= 1;
        if (ChessUtils.in_bounds((x,y), board)):
            if ((board[y][x] == rook) or (board[y][x] == queen)):
                return True;
        
        #up left
        x = k_x - 1;
        y = k_y - 1;
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == king)):
            return True;
        #pawns attack diagonally
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == pawn) and opponent == downpawn):
            return True;
        while (ChessUtils.in_bounds((x,y),board) and board[y][x] == 0):
            x -= 1;
            y -= 1;
        if (ChessUtils.in_bounds((x,y), board)):
            if ((board[y][x] == bishop) or (board[y][x] == queen)):
                return True;
            
        #up 
        x = k_x;
        y = k_y - 1;
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == king)):
            return True;
        while (ChessUtils.in_bounds((x,y),board) and board[y][x] == 0):
            y -= 1;
        if (ChessUtils.in_bounds((x,y), board)):
            if ((board[y][x] == rook) or (board[y][x] == queen)):
                return True;
            
        #up right
        x = k_x + 1;
        y = k_y - 1;
        #check in_bounds first so it can short circuit if need be
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == king)):
            return True;
        #diagonal pawn
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == pawn) and opponent == downpawn):
            return True;
        while (ChessUtils.in_bounds((x,y),board) and board[y][x] == 0):
            x += 1;
            y -= 1;
        if (ChessUtils.in_bounds((x,y), board)):
            if ((board[y][x] == bishop) or (board[y][x] == queen)):
                return True;
        
        #right 
        x = k_x + 1;
        y = k_y;
        if (ChessUtils.in_bounds((x,y), board) 
            and (board[y][x] == king)):
            return True;
        while (ChessUtils.in_bounds((x,y),board) and board[y][x] == 0):
            x += 1;
        if (ChessUtils.in_bounds((x,y), board)):
            if ((board[y][x] == rook) or (board[y][x] == queen)):
                return True;
        
        #down right
        x = k_x + 1;
        y = k_y + 1;
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == king)):
            return True;
        #pawns attack diagonally
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == pawn) and opponent == uppawn):
            return True;
        while (ChessUtils.in_bounds((x,y),board) and board[y][x] == 0):
            x += 1;
            y += 1;
        if (ChessUtils.in_bounds((x,y), board)):
            if ((board[y][x] == bishop) or (board[y][x] == queen)):
                return True;
            
        #down 
        x = k_x;
        y = k_y + 1;
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == king)):
            return True;
        while (ChessUtils.in_bounds((x,y),board) and board[y][x] == 0):
            y += 1;
        if (ChessUtils.in_bounds((x,y), board)):
            if ((board[y][x] == rook) or (board[y][x] == queen)):
                return True;
            
        #down left
        x = k_x - 1;
        y = k_y + 1;
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == king)):
            return True;
        #diagonal pawn
        if (ChessUtils.in_bounds((x,y), board) and (board[y][x] == pawn) and opponent == uppawn):
            return True;
        while (ChessUtils.in_bounds((x,y),board) and board[y][x] == 0):
            x -= 1;
            y += 1;
        if (ChessUtils.in_bounds((x,y), board)):
            if ((board[y][x] == bishop) or (board[y][x] == queen)):
                return True;      
                
        
        #otherwise not in check
        return False;
    
    @staticmethod
    def get_valid_moves(current_player, board):
        """
        Iterates through a game board and determines the set of valid moves.
        
        Params:
        current_player - Current player's turn
        board - Current board state.
        
        Returns:
        List of valid moves for the specified player and game board.
        Format is a list of Tuples from From to To.
        
        >>> ChessUtils.get_valid_moves(0, [[5,2,0,6],[0,0,0,0],[0,0,0,0],[0,14,0,16]])
        (False, [(0, 5), (0, 10), (0, 15), (0, 4), (0, 8), (0, 12), (1, 2), (1, 5), (1, 9), (1, 13), (3, 6), (3, 2)])
        
        >>> ChessUtils.get_valid_moves(0, [[0,6,2,0],[0,0,3,0],[0,0,0,0],[0,12,0,16]])
        (True, [(1, 4), (1, 0), (6, 13)])
        
        >>> ChessUtils.get_valid_moves(0,[[0,6,0,0],[11,0,0,1],[0,0,0,0],[0,11,0,16]])
        (True, [(1, 6), (1, 4), (1, 2), (1, 5), (1, 0)])
        
        >>> ChessUtils.get_valid_moves(0,[[0,6,0,0],[11,0,0,1],[0,11,0,0],[0,11,0,16]])
        (True, [(1, 2), (1, 5), (1, 0)])
        
        >>> ChessUtils.get_valid_moves(0,[[0,6,0,0,0],[0,0,0,1,0],[0,11,0,0,0],[0,0,0,0,15],[0,11,0,16,0]])
        (True, [(1, 2), (1, 6), (1, 0), (8, 13)])
        
        >>> ChessUtils.get_valid_moves(0,[[0,0,0,0,0],[0,6,0,1,0],[0,0,0,3,0],[0,0,0,0,0],[0,11,0,16,15]])
        (True, [(6, 2), (6, 10), (6, 1), (6, 7), (6, 11), (6, 5), (13, 24)])
        
        >>> ChessUtils.get_valid_moves(0,[[0,0,0,0,0,0,0,0],[0,6,0,1,0,0,0,0],[0,0,0,3,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,3,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,11,0,16,15,0,0,0]])
        (False, [(9, 0), (9, 2), (9, 18), (9, 16), (9, 1), (9, 10), (9, 17), (9, 8), (19, 2), (19, 4), (19, 13), (19, 29), (19, 36), (19, 34), (19, 25), (35, 18), (35, 25), (35, 20), (35, 29), (35, 45), (35, 52), (35, 50), (35, 41)])
        
        >>> ChessUtils.get_valid_moves(0,[[2,3,4,5,6,4,3,2],[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[11,11,11,11,11,11,11,11],[12,13,14,15,16,14,13,12]])
        (False, [(1, 18), (1, 16), (6, 23), (6, 21), (8, 16), (8, 24), (9, 17), (9, 25), (10, 18), (10, 26), (11, 19), (11, 27), (12, 20), (12, 28), (13, 21), (13, 29), (14, 22), (14, 30), (15, 23), (15, 31)])

        >>> ChessUtils.get_valid_moves(0,[[3,0,0,0],[5,6,0,0],[0,0,0,0],[4,15,12,16]]) # Demo board move #1
        (True, [(0, 9), (4, 9), (12, 9)])

        >>> ChessUtils.get_valid_moves(1,[[0,0,0,0],[5,6,0,0],[0,3,0,0],[4,15,12,16]]) # Demo board move #2
        (True, [(13, 9), (15, 11)])
        
        >>> ChessUtils.get_valid_moves(0,[[0,0,0,0],[5,6,0,0],[0,1,0,0],[4,15,12,16]]) # Demo board move #2 variant for testing
        (False, [(4, 1), (4, 0), (4, 8), (5, 0), (5, 1)])

        >>> ChessUtils.get_valid_moves(0,[[0,0,0,0],[5,6,0,0],[0,3,0,16],[4,15,12,0]]) # Demo board move #3
        (False, [(4, 1), (4, 0), (4, 8), (5, 0), (5, 1)])
        
        >>> ChessUtils.get_valid_moves(1,[[0,5,0,0],[0,6,0,0],[0,3,0,16],[4,15,12,0]]) # Demo board move #4
        (True, [(14, 6)])
        
        >>> ChessUtils.get_valid_moves(0,[[0,5,0,0],[0,6,12,0],[0,3,0,16],[4,15,0,0]]) # Demo board move #5
        (True, [(1, 6), (5, 0)])
        
        >>> ChessUtils.get_valid_moves(1,[[0,0,0,0],[0,6,5,0],[0,3,0,16],[4,15,0,0]]) # Demo board move #6
        (True, [])
        
        >>> ChessUtils.get_valid_moves(0,[[3,0,0,0],[5,6,0,0],[0,4,15,0],[0,0,12,16]]) # Demo board derivative
        (True, [(5, 8), (5, 1)])
        
        >>> ChessUtils.get_valid_moves(0,[[3,0,0,0],[5,0,0,0],[6,4,15,0],[12,0,0,16]]) # Demo board derivative
        (True, [(8, 12)])
        """
        
        #note: assumes pawns of player WHITE can only move down
        #and pawns of player BLACK can only move up
        #but that can be changed here:
        downpawn = PlayerType.WHITE
        uppawn = PlayerType.BLACK
        
        opponent = abs(current_player - 1);
        height = len(board);
        width = len(board[0]);
        pawn = current_player*10 + ChessPiece.PAWN;
        rook = current_player*10 + ChessPiece.ROOK;
        knight = current_player*10 + ChessPiece.KNIGHT;
        bishop = current_player*10 + ChessPiece.BISHOP;
        queen = current_player*10 + ChessPiece.QUEEN;
        king = current_player*10 + ChessPiece.KING;
        
        #start with an empty list
        valid_moves = []
        
        #scan through the board:
        for y in range(len(board)):
            for x in range(len(board[0])):
                if ((board[y][x] != 0) and (board[y][x]//10 == current_player)):
                    # we found a piece that belongs to the current player
                    piece = board[y][x];
                    spot = y * width + x;
                    
                    #enumerate through the piece types
                    
                    #pawn can only move forward one space if nothing is there,
                    #or two if nothing is there and it's in its starting spot
                    #or diagonal on a kill move               
                    
                    if (piece == pawn):
                        #pawn can only move in one direction
                        if (current_player == downpawn):
                            pdir = 1;
                            multiplier = downpawn
                        else:
                            pdir = -1;
                            multiplier = uppawn
                            
                        #first check for normal non-killing moves.
                        #ordinarily, pawn can only move in one direction, one space
                        #and only if it doesn't make a kill doing so
                        if (ChessUtils.in_bounds((x,y+pdir), board)
                            and board[y + pdir][x] == 0):
                            newspot = (y + pdir) * width + x;
                            nb = ChessUtils.make_move((spot, newspot), board)
                            if not ChessUtils.in_check(current_player, nb):
                                valid_moves.append((spot,newspot))
                                
                        #it is possible for a pawn to move two spaces, but three
                        #conditions must be met. the board must be at least 5x5,
                        #the pawn must be on its starting row and the pawn needs
                        #a clear path to that spot
                        if (width >= 5
                            and y == ((height-1) * multiplier + pdir)
                            and board[y + pdir][x] == 0
                            and board[y + pdir*2][x] == 0):
                            newspot = (y + pdir*2) * width + x;
                            nb = ChessUtils.make_move((spot, newspot), board)
                            if not ChessUtils.in_check(current_player, nb):
                                valid_moves.append((spot,newspot))
                                
                        #now check for pawn killing moves, diagonal only:
                        p_spots = [[1,pdir], [-1,pdir]] #killing moves pawn can make
                        for p in p_spots:
                            if (ChessUtils.in_bounds((x+p[0], y + p[1]), board)
                                and (board[y + p[1]][x + p[0]]) != 0
                                and (board[y + p[1]][x + p[0]])//10 == opponent):
                                newspot = (y + p[1]) * width + x + p[0];
                                nb = ChessUtils.make_move((spot, newspot), board)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot))
                                
                    #rook can move up, right, down, left direction many spaces
                    if (piece == rook):
                        r_dirs = [[0,-1],[1,0],[0,1],[-1,0]]
                        for n in r_dirs:
                            xn = x + n[0];
                            yn = y + n[1];
                            while (ChessUtils.in_bounds((xn, yn), board)
                                and (board[yn][xn] == 0)):
                                newspot = yn * width + xn
                                nb = ChessUtils.make_move((spot, newspot), board)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot))
                                xn += n[0]
                                yn += n[1]
                            if (ChessUtils.in_bounds((xn, yn), board)
                                # and (board[yn][xn] != 0)
                                and (board[yn][xn]//10 == opponent)):
                                newspot = yn * width + xn
                                nb = ChessUtils.make_move((spot, newspot), board)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot))
                                    
                    #knight can move in an L shape, eight spots
                    if (piece == knight):
                        kn_spots = [(-1,-2),(-2,-1),(1,-2),(2,-1),(2,1),(1,2),(-1,2),(-2,1)]
                        for n in kn_spots:
                            xn = x + n[0];
                            yn = y + n[1];
                            if (ChessUtils.in_bounds((xn, yn), board)
                                and ((board[yn][xn]//10 == opponent)
                                     or board[yn][xn] == 0)):
                                newspot = yn * width + xn
                                nb = ChessUtils.make_move((spot, newspot), board)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot))
                            
                    #bishop can move any diagonal many spaces
                    if (piece == bishop):
                        b_dirs = [[-1,-1],[1,-1],[1,1],[-1,1]]
                        for n in b_dirs:
                            xn = x + n[0];
                            yn = y + n[1];
                            while (ChessUtils.in_bounds((xn, yn), board)
                                and (board[yn][xn] == 0)):
                                newspot = yn * width + xn
                                nb = ChessUtils.make_move((spot, newspot), board)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot))
                                xn += n[0]
                                yn += n[1]
                            if (ChessUtils.in_bounds((xn, yn), board)
                                and (board[yn][xn]//10 == opponent)):
                                newspot = yn * width + xn
                                nb = ChessUtils.make_move((spot, newspot), board)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot))   
                                    
                    #queen can move any direction many spaces
                    if (piece == queen):
                        q_dirs = [[-1,-1],[1,-1],[1,1],[-1,1],[0,-1],[1,0],[0,1],[-1,0]]
                        for n in q_dirs:
                            xn = x + n[0];
                            yn = y + n[1];
                            while (ChessUtils.in_bounds((xn, yn), board)
                                and (board[yn][xn] == 0)):
                                newspot = yn * width + xn
                                nb = ChessUtils.make_move((spot, newspot), board)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot))
                                xn += n[0]
                                yn += n[1]
                            if (ChessUtils.in_bounds((xn, yn), board)
                                and (board[yn][xn]//10 == opponent)):
                                newspot = yn * width + xn
                                nb = ChessUtils.make_move((spot, newspot), board)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot)) 
                                    
                    #king can move in any direction but only one space
                    if (piece == king):
                        k_dirs = [[-1,-1],[1,-1],[1,1],[-1,1],[0,-1],[1,0],[0,1],[-1,0]]
                        for n in k_dirs:
                            xn = x + n[0];
                            yn = y + n[1];
                            if (ChessUtils.in_bounds((xn, yn), board)
                                and ((board[yn][xn]//10 == opponent)
                                     or board[yn][xn] == 0)):
                                # print "king goes ", xn, " ", yn
                                newspot = yn * width + xn
                                nb = ChessUtils.make_move((spot, newspot), board)
                                # ChessUtils.print_board(nb)
                                if not ChessUtils.in_check(current_player, nb):
                                    valid_moves.append((spot,newspot))
                    
                    #remove this note before submitting to Li if it's never addressed
                    """In theory, there are two castle moves which would require
                    verifying a proper board, such as the 8x8 board, as well as
                    verifying the position of the king and the rook in question
                    in relation to the size of the board.
                    It's possible that a history may be needed.
                    
                    It's not just a simple issue of moving one piece from one
                    spot to another. It requires moving two pieces which changes
                    our idea of the (to,from) move tuple.
                    
                    We can choose not to include the castle moves if it complicates
                    things too much which I'm fine with."""
        
        #return the tuple with if the board is in check, and valid moves
        return ((ChessUtils.in_check(current_player, board), valid_moves))

    
    @staticmethod
    def get_piece(piece_player_num):
        """
        Given the specified piece number, this function returns whether it
        belongs to white or black.
        
        Param: Integer - Piece number that includes player and field combined
        
        Returns: Piece ID number (integer) as defined by the ChessPiece Class
        
        >>> ChessUtils.get_piece(17)
        Traceback (most recent call last):
         ...
        ValueError: The number "17" does not correspond to a valid piece.
        
        >>> ChessUtils.get_piece(-1)
        Traceback (most recent call last):
         ...
        ValueError: The number "-1" does not correspond to a valid piece.
        
        >>> ChessUtils.get_piece(11)
        1
        >>> ChessUtils.get_piece(5)
        5
        >>> ChessUtils.get_piece(10)
        0
        >>> ChessUtils.get_piece(0)
        0
        >>> ChessUtils.get_piece(16)
        6
        """
        
        piece_id = piece_player_num % 10
        
        # Ensure the piece ID is valid.
        if(piece_id == ChessPiece.BLANK or piece_id == ChessPiece.PAWN or piece_id == ChessPiece.KNIGHT \
           or piece_id == ChessPiece.BISHOP or piece_id == ChessPiece.ROOK or piece_id == ChessPiece.QUEEN \
           or piece_id == ChessPiece.KING):
        
            return piece_id
     
        # Raise an exception that the piece is invalid.
        else:
            raise ValueError( "The number \"" + str(piece_player_num) + "\" does not correspond to a valid piece.")
    
    @staticmethod
    def get_player(piece_player_num):
        """
        Given the specified piece number, this function returns whether it
        belongs to white or black.
        
        Param: 
        piece_player_num - Integer - Piece number that includes player and field combined 
        
        Returns: Color corresponding to the piece with number "piece_player_numb".
        
        >>> ChessUtils.get_player(0)
        0
        >>> ChessUtils.get_player(10)
        1
        >>> ChessUtils.get_player(19)
        1
        
        >>> ChessUtils.get_player(20)
        Traceback (most recent call last):
         ...
        ValueError: The number "20" does not correspond to a valid color.
        
        >>> ChessUtils.get_player(-1)
        Traceback (most recent call last):
         ...
        ValueError: The number "-1" does not correspond to a valid color.
        """
        
        player_color = piece_player_num // 10
        
        if(player_color == PlayerType.WHITE or player_color == PlayerType.BLACK):
            
            return player_color
        
        else:
            raise ValueError( "The number \"" + str(piece_player_num) + "\" does not correspond to a valid color." )

    
    @staticmethod
    def get_state_utility(board, current_player, is_max, is_check, valid_moves):
        """
        Given a specified chess board, this static method determines and returns
        the utility.  Note that no player is specified for the function.  Player 0
        is the reference (max) in this function.
        
        Returns:
        Int - Utility of the current board for the current player.
        
        >>> ChessUtils.get_state_utility( [], PlayerType.WHITE, True, False, [] ) # Empty board so state value is empty
        0
        >>> ChessUtils.get_state_utility( [[0,1,2]], PlayerType.WHITE, True, False, [] ) # Draw board since no move is possible
        0
        >>> ChessUtils.get_state_utility( [[0,1,2]], PlayerType.WHITE, True, False, [(0,1), (2,0)] ) # One pawn and one rook for white
        6
        >>> ChessUtils.get_state_utility( [[0,1,2]], PlayerType.BLACK, True, False, [(0,1), (2,0)] ) # One pawn and one rook for white
        -6
        >>> ChessUtils.get_state_utility( [[0,1,2],[0,0,0],[0,1,2]], PlayerType.BLACK, True, False, [(0,1), (2,0)] ) # Two pawns and two rooks for white
        -12
        >>> ChessUtils.get_state_utility( [[0,1,2],[0,0,0],[0,11,2]], PlayerType.BLACK, True, False, [(0,1), (2,0)] ) # Two pawns and two rooks for white, one pawn for black
        -10
        >>> ChessUtils.get_state_utility( [[0,3,14]], PlayerType.BLACK, True, False, [(0,1), (2,0)] ) # One knight white and one bishop for black.
        0
        >>> ChessUtils.get_state_utility( [[0,3,14],[15,0,15]], PlayerType.BLACK, True, False, [(0,1), (2,0)] ) # One knight white and one bishop for black.
        18
        >>> ChessUtils.get_state_utility( [[0,1,2],[0,11,12]], PlayerType.WHITE, True, False, [(0,1), (2,0)] ) # Board with alternate pieces
        0
        >>> ChessUtils.get_state_utility( [], PlayerType.WHITE, True, True, [] ) # Checkmate and current player is max
        -2147483646
        >>> ChessUtils.get_state_utility( [], PlayerType.BLACK, True, True, [] ) # Checkmate and current player is max
        -2147483646
        >>> ChessUtils.get_state_utility( [], PlayerType.BLACK, False, True, [] ) # Checkmate and current player is min
        2147483647
        >>> ChessUtils.get_state_utility( [], PlayerType.WHITE, True, True, [(0,1)] ) # Check but move possible
        0
        """
        
        # If not in check and there are no valid moves, then the result is a draw.
        if(not is_check and len(valid_moves) == 0):
            return 0
         
        # Check if the current board is in checkmate.
        elif(is_check and len(valid_moves) == 0):
            # Current player is max and is in checkmate, then return negative max.
            if(is_max):
                return -(sys.maxint-1)
            # Current play is min and has lost so return positive max int.
            else:
                return sys.maxint 
         
        # Keep the scores of white and black respectively
        white_score = 0
        black_score = 0
         
        # iterate through all the board cells row by row
        for board_row in board:
            # Go column by column in the row
            for piece in board_row:
                 
                # Extract the piece ID
                piece_id = ChessUtils.get_piece(piece)
                piece_color = ChessUtils.get_player(piece)
                 
                # Go through all the possible pieces and assign a value
                if(piece_id == ChessPiece.BLANK): piece_value = 0
                elif(piece_id == ChessPiece.PAWN): piece_value = 1
                elif(piece_id == ChessPiece.ROOK): piece_value = 5
                elif(piece_id == ChessPiece.BISHOP): piece_value = 3
                elif(piece_id == ChessPiece.KNIGHT): piece_value = 3
                elif(piece_id == ChessPiece.QUEEN): piece_value = 9
                elif(piece_id == ChessPiece.KING): piece_value = 0
                else:
                    raise ValueError("Invalid board piece: " + str(piece_id))
                 
                if(piece_color == PlayerType.WHITE):
                    white_score += piece_value
                elif(piece_color == PlayerType.BLACK):
                    black_score += piece_value
                else:
                    raise ValueError("Invalid board piece color: " + str(piece_id))
         
        # Determine how to take the difference between the white and black scores.
        if((is_max and current_player == PlayerType.WHITE) \
           or (not is_max and current_player == PlayerType.BLACK) ):
            return (white_score - black_score)
        else:
            return (black_score - white_score)



# Support the use of doctest if this module is the main.
if(__name__ == "__main__"):
    """
    This section is included to allow for automatic unit testing of the file 
    using the Python doctest utility.
    """
    import doctest
    doctest.testmod()
