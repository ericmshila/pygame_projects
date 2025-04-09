import pygame
import sys


# GAME INITIALIZATION
pygame.init()

# Screen Dimensions 

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8,8
SQUARE_SIZE = WIDTH // COLS

# Colors 
RED = (255,0,0)
WHITE = (255,255,255)
BLACK =  (0,0,0)
BLUE = (0,0,255)
GREY = (128,128,128)

# Initialize the screen 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('CHECKERS_V1')

# CREATING THE BOARD
def draw_squares(screen):
    screen.fill(BLACK)
    for row in range(ROWS):
        for col in range(row % 2, COLS, 2 ):
            pygame.draw.rect(screen, WHITE, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# represent piece with location, color an whethere it is a king 
class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__ (self, row, col, color):
        self.row = row 
        self.col = col 
        self.color = color 
        self.king = False 

        if self.color == RED: 
            self.direction = -1
        else:
            self.direction = 1

        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        # draw piece and place it the centre of the square
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2 
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, screen):
        CROWN_WIDTH,CROWN_HEIGHT = 44,25
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(screen, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(screen, self.color, (self.x, self.y), radius)
        if self.king:
            crown = pygame.image.load('crown.png')
            crown = pygame.transform.scale(crown, (CROWN_WIDTH, CROWN_HEIGHT))
            screen.blit(crown, (self.x - crown.get_width()//2, self.y - crown.get_height()//2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()
# Board class to manage the game state
class Board:
    def __init__(self):
        self.board = [] 
        self.red_left = self.white_left = 12 # all pieces set to 12 initially 
        self.red_kings = self.white_kings = 0 # no kings initially 
        self.create_board()

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2): # ensure pieces are places on black squares only
                    if row < 3: # white pieces on first 3 rows
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4: # red pieces on last 3 rows
                        self.board[row].append(Piece(row, col, RED))
                    else: #empty middle rows 
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
    def get_piece(self, row, col):
        return self.board[row][col]

    def draw(self, screen):
        self.draw_squares(screen)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col] #retrieve piece at the current position
                if piece != 0:
                    piece.draw(screen)

    def draw_squares(self, screen):
        screen.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(screen, WHITE, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1
    
    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1
    def get_valid_moves(self, piece):
        """
        Returns a dictionary of valid moves for a piece. 
        The keys of the dictionary are the destination squares (row, col), 
        and the values are the pieces that need to be skipped (if any).
        """
        moves = {}
        directions = [-1, 1] if piece.color == RED else [1, -1]  # Movement directions for RED or WHITE

        # Check diagonal movement in both directions
        for direction in directions:
            for offset in [-1, 1]:
                new_row = piece.row + direction
                new_col = piece.col + offset

                if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] == 0:
                    moves[(new_row, new_col)] = None  # Valid move, no piece to skip

                # Check for capturing opponent's pieces
                else:
                    # Opponent's piece should be between the current and target position
                    capture_row = new_row + direction
                    capture_col = new_col + offset

                    if self.is_valid_position(capture_row, capture_col) and self.board[capture_row][capture_col] == 0:
                        # Check if there is an opponent's piece in between
                        middle_piece = self.board[new_row][new_col]
                        if middle_piece != 0 and middle_piece.color != piece.color:
                            moves[(capture_row, capture_col)] = middle_piece  # Capture move

        return moves

    def is_valid_position(self, row, col):
        """
        Checks if the given row and column are within the board boundaries.
        """
        return 0 <= row < ROWS and 0 <= col < COLS

# Handling User Input 
def get_row_col_from_mouse(pos):
    x,y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE  
    return row,col


class Game:
    def __init__(self, screen):
        self._init()
        self.screen = screen

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}

    def update(self):
        self.board.draw(self.screen)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove([skipped])
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.screen, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

# main function that runs the game
def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(screen)

    while run:
        clock.tick(60) # Limit frame rate to 60 FPS
        
        if game.turn == RED:
            print("Red's turn")
        else:
            print("White's turn")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        
        game.update()

    pygame.quit()
    sys.exit()
# run the game if the script is executed directly. not imported as a module
if __name__ == "__main__":
    main()








        