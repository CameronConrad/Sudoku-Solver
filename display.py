import pygame
from solver import Board, Solver
import json
import sys

class Display:
    def __init__(self, tile_size, gridFileName: str = None):
        pygame.init()

        self.__tile_size = tile_size
        self.__width = tile_size * 9
        self.__height = tile_size * 9
        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        self.__screen.fill((255, 255, 255))
        self.__board = None
        self.__selected_coors = [0, 0]
        if gridFileName != None:
            with open(gridFileName, "r") as f:
                grid = json.load(f)
                self.__board = Board(grid)
        else:
            self.__board = Board()
        self.__solver = Solver(self.__board)
        pygame.display.set_caption("Sudoku Solver")
    
    def draw_board(self):
        # Draw square where selected coordinates are
        pygame.draw.rect(self.__screen, (0, 255, 0), (self.__selected_coors[1] * self.__tile_size, self.__selected_coors[0] * self.__tile_size, self.__tile_size, self.__tile_size), 3)

        for row in range(len(self.__board.get_board())):
            for col in range(len(self.__board.get_board()[row])):
                if self.__board.get_number(row, col) != 0:
                    self.__draw_number(row, col, self.__board.get_number(row, col))
        self.__draw_lines()
    
    def __draw_number(self, row, col, number):
        font = pygame.font.SysFont("Arial", 30)
        text = font.render(str(number), True, (0, 0, 0))
        self.__screen.blit(text, (col * self.__tile_size + 10, row * self.__tile_size + 10))

    def __draw_lines(self):
        for i in range(len(self.__board.get_board())):
            if i % 3 == 0:
                pygame.draw.line(self.__screen, (0, 0, 0), (0, i * self.__tile_size), (self.__width, i * self.__tile_size), 3)
                pygame.draw.line(self.__screen, (0, 0, 0), (i * self.__tile_size, 0), (i * self.__tile_size, self.__height), 3)
            else:
                pygame.draw.line(self.__screen, (0, 0, 0), (0, i * self.__tile_size), (self.__width, i * self.__tile_size), 1)
                pygame.draw.line(self.__screen, (0, 0, 0), (i * self.__tile_size, 0), (i * self.__tile_size, self.__height), 1)
    
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    added = False
                    progress = True
                    while not added and progress:
                        progress, added, removed = self.__solver.solve(True, True)
                elif event.unicode in "123456789" and event.unicode != "":
                    self.__board.grid[self.__selected_coors[0]][self.__selected_coors[1]] = int(event.unicode)
            self.check_mouse_click(event)
    
    def check_mouse_click(self, event):
        # If the mouse clicks on a square and releases, increase the square's number
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.__width and mouse_pos[1] < self.__height:
                row = mouse_pos[1] // self.__tile_size
                col = mouse_pos[0] // self.__tile_size
                self.__selected_coors = [row, col]

    def run(self):
        running = True
        while running:

            self.__screen.fill((255, 255, 255))

            self.check_events()
            
            self.draw_board()

            pygame.display.update()


if __name__ == "__main__":
    display = Display(50)
    display.run()