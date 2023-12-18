import pygame
from solver import Board, Solver
import json
import sys
import argparse

class Display:
    def __init__(self, tile_size, gridFileName: str = "board.json"):
        pygame.init()

        self.__tile_size = tile_size
        self.__width = tile_size * 9
        self.__height = tile_size * 9
        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        self.__screen.fill((255, 255, 255))
        self.__board = None
        self.__selected_coors = [0, 0]
        self.gridFileName = gridFileName
        if self.gridFileName != None:
            with open(self.gridFileName, "r") as f:
                grid = json.load(f)
                self.__board = Board(grid)
        else:
            self.__board = Board()
        self.__solver = Solver(self.__board)
        pygame.display.set_caption("Sudoku Solver")

        # Create invalid board text
        self.invalid = False
        font = pygame.font.SysFont("Arial", 30)
        text = font.render("Invalid board", True, (255, 0, 0))
        self.__invalid_text = pygame.transform.rotate(text, 45)
        self.__invalid_text_rect = self.__invalid_text.get_rect()
        self.__invalid_text_rect.center = (self.__width // 2, self.__height // 2)
    
    def draw_board(self):
        # Draw square where selected coordinates are
        pygame.draw.rect(self.__screen, (0, 255, 0), (self.__selected_coors[0] * self.__tile_size, self.__selected_coors[1] * self.__tile_size, self.__tile_size, self.__tile_size), 3)

        for row in range(len(self.__board.get_board())):
            for col in range(len(self.__board.get_board()[row])):
                if self.__board.get_number(row, col) != 0:
                    self.__draw_number(row, col, self.__board.get_number(row, col))

        self.__draw_lines()

        if self.invalid:
            self.__screen.blit(self.__invalid_text, self.__invalid_text_rect)
    
    def __draw_number(self, row, col, number):
        font = pygame.font.SysFont("Arial", 30)
        text = font.render(str(number), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (col * self.__tile_size + self.__tile_size // 2, row * self.__tile_size + self.__tile_size // 2)
        self.__screen.blit(text, text_rect)


    def __draw_lines(self):
        for i in range(len(self.__board.get_board())):
            if i % 3 == 0:
                pygame.draw.line(self.__screen, (0, 0, 0), (0, i * self.__tile_size), (self.__width, i * self.__tile_size), 3)
                pygame.draw.line(self.__screen, (0, 0, 0), (i * self.__tile_size, 0), (i * self.__tile_size, self.__height), 3)
            else:
                pygame.draw.line(self.__screen, (0, 0, 0), (0, i * self.__tile_size), (self.__width, i * self.__tile_size), 1)
                pygame.draw.line(self.__screen, (0, 0, 0), (i * self.__tile_size, 0), (i * self.__tile_size, self.__height), 1)
    
    def check_events(self, progress=False, debug=False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    added = False
                    progress = True
                    while not added and progress:
                        try:
                            progress, added, removed = self.__solver.solve(progress, debug)
                            self.invalid = False
                        except Exception:
                            self.invalid = True
                            break
                elif event.key == pygame.K_s:
                    if self.gridFileName != None:
                        self.save_board(self.gridFileName)
                elif event.key == pygame.K_l:
                    if self.gridFileName != None:
                        self.load_board(self.gridFileName)
                elif event.key == pygame.K_c:
                    self.__board = Board()
                    self.__solver = Solver(self.__board)
                elif event.unicode in "123456789" and event.unicode != "":
                    self.__board.grid[self.__selected_coors[1]][self.__selected_coors[0]] = int(event.unicode)
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE or event.key == pygame.K_SPACE:
                    self.__board.grid[self.__selected_coors[1]][self.__selected_coors[0]] = 0
                    self.__solver.possible_numbers[self.__selected_coors[1]][self.__selected_coors[0]] = [i for i in range(1, 10)]
                elif event.key == pygame.K_UP:
                    self.move_coors(0, -1)
                elif event.key == pygame.K_DOWN:
                    self.move_coors(0, 1)
                elif event.key == pygame.K_LEFT:
                    self.move_coors(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_coors(1, 0)
                
            self.check_mouse_click(event)
    
    def check_mouse_click(self, event):
        # If the mouse clicks on a square and releases, increase the square's number
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.__width and mouse_pos[1] < self.__height:
                row = mouse_pos[1] // self.__tile_size
                col = mouse_pos[0] // self.__tile_size
                self.__selected_coors = [col, row]
    
    def move_coors(self, x_move, y_move):
        x = self.__selected_coors[0] + x_move
        if x < 0:
            x = 8
        elif x > 8:
            x = 0
        y = self.__selected_coors[1] + y_move
        if y < 0:
            y = 8
        elif y > 8:
            y = 0
        self.__selected_coors = [x, y]
    
    def save_board(self, fileName: str):
        with open(fileName, "w") as f:
            json.dump(self.__board.get_board(), f)
    
    def load_board(self, fileName: str):
        with open(fileName, "r") as f:
            grid = json.load(f)
            self.__board = Board(grid)
            self.__solver = Solver(self.__board)

    def run(self, progress=False, debug=False):
        running = True
        while running:

            self.__screen.fill((255, 255, 255))

            self.check_events(progress, debug)
            
            self.draw_board()

            pygame.display.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sudoku Solver GUI")
    parser.add_argument("-p", "--progress", help="Display progress in terminal", action="store_true", default=False)
    parser.add_argument("-d", "--debug", help="Display debug information", action="store_true", default=False)
    parser.add_argument("-f","--file", help="Path to the grid file", type=str, default=None)
    args = parser.parse_args()

    display = Display(50)
    if args.file != None:
        display = Display(50, args.file)
    else:
        display = Display(50, "board.json")
    display.run(args.progress, args.debug)