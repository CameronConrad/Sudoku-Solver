import json
import sys
import argparse


class Board:
    def __init__(self, grid: list[list[int]] = [[0 for i in range(9)] for j in range(9)]):
        self.grid = grid
        self.__size = len(grid)
        self.__box_size = self.__size // 3
        if not self.check_if_valid():
            raise Exception("Invalid board")
    
    @classmethod
    def initialize_grid(cls, size: int):
        grid = []
        for i in range(size):
            grid.append([0 for i in range(size)])
        return grid
    
    def check_if_valid(self):
        # Check if the board is a square
        valid = True
        for row in self.grid:
            if len(row) != self.__size:
                valid = False
                break
        
        # If the board is not a square divisible by 3, it is not valid
        if self.__size % 3 != 0:
            valid = False
        
        # Check if the board is valid
        for row in range(self.__size):
            for col in range(self.__size):
                # If the number is not 0, check if it is valid
                if self.grid[row][col] != 0:
                    temp = self.grid[row][col]
                    self.grid[row][col] = 0
                    if not self.check_if_number_valid(row, col, temp):
                        valid = False
                        print("Invalid number at row", row, "column", col)
                    self.grid[row][col] = temp
                    if not valid:
                        break

        return valid
    
    def get_size(self) -> int:
        return self.__size
    
    def get_number(self, row: int, col: int) -> int:
        return self.grid[row][col]
    
    def get_row(self, row: int) -> [int]:
        return self.grid[row]

    def get_column(self, col: int) -> [int]:
        column = []
        for row in self.grid:
            column.append(row[col])
        return column
    
    def get_box(self, row: int, col: int) -> [[int]]:
        box = []
        startRow = (row // self.__box_size) * self.__box_size
        startCol = (col // self.__box_size) * self.__box_size
        endRow = startRow + self.__box_size
        endCol = startCol + self.__box_size
        for i in range(startRow, endRow):
            for j in range(startCol, endCol):
                box.append(self.grid[i][j])
        return box

    def get_board(self) -> [[int]]:
        return self.grid

    def display_board(self):
        for row in self.grid:
            print(row)
    
    def check_if_number_valid(self, row: int, col: int, number: int) -> bool:
        valid = False
        if number not in self.get_row(row) and number not in self.get_column(col) and number not in self.get_box(row, col):
            valid = True
        return valid


class Solver:
    def __init__(self, board: Board):
        self.board = board
        self.possible_numbers = [[[i + 1 for i in range(self.board.get_size())] 
                                    for i in range(self.board.get_size())] 
                                    for j in range(self.board.get_size())]
        for row in range(len(self.possible_numbers)):
            for col in range(len(self.possible_numbers[row])):
                if self.board.get_number(row, col) != 0:
                    self.possible_numbers[row][col] = [self.board.get_number(row, col)]
        self.solved = False
    
    def check_if_solved(self) -> bool:
        solved = True
        for row in self.board.get_board():
            if 0 in row:
                solved = False
                break
        return solved
    
    def get_remaining_spaces(self) -> int:
        remaining = 0
        for row in self.board.get_board():
            for col in row:
                if col == 0:
                    remaining += 1
        return remaining
    
    def solve(self, terminalDisplay: bool = False, debugDisplay: bool = False) -> bool:
        """
        Each time this function is called, it will solve the board as much as possible in 
        one iteration of the squares. This function will return three values: progress,
        added, and removed. Progress will be True if the function made any progress, and
        False if it did not. Added will be True if the function added a number to the board,
        and False if it did not. Removed will be True if the function removed a possibility
        from a square, and False if it did not.
        
        Parameters
        terminalDisplay: bool
        debugDisplay: bool

        Returns
        progress: bool
        added: bool
        removed: bool
        """
        progress = False
        added = False
        removed = False

        # Eliminate impossible numbers
        for y in range(len(self.board.get_board())):
            for x in range(len(self.board.get_board())):
                # If there is no number in the cell, get the possible numbers
                if self.board.get_number(y, x) == 0:
                    # Create a copy of the possible numbers for backtracking
                    possible_numbers_copy = self.possible_numbers[y][x][:]

                    # Loop through possible numbers
                    for number in possible_numbers_copy:
                        # Check if the possibility is invalid
                        if not self.board.check_if_number_valid(y, x, number):
                            self.possible_numbers[y][x].remove(number)
                            if debugDisplay:
                                print(f"Removed {number} from row {y} column {x}")
                            progress = True

                    # If there is only one possible number left, add it to the board
                    if len(self.possible_numbers[y][x]) == 1 and self.board.get_number(y, x) == 0:
                        self.board.grid[y][x] = self.possible_numbers[y][x][0]
                        if debugDisplay:
                            print(f"Added {self.possible_numbers[y][x][0]} to row {y} column {x}")
                        added = True
                        progress = True

        # Find numbers that are only possible in one square
        for y in range(len(self.possible_numbers)):
            for x in range(len(self.possible_numbers[y])):
                for num in self.possible_numbers[y][x]:
                    # Look through the possible numbers in the row
                    essential = True
                    for item_x in range(len(self.possible_numbers[y])):
                        if num in self.possible_numbers[y][item_x] and item_x != x:
                            essential = False
                            break

                    # Look through the possible numbers in the column
                    if not essential:
                        essential = True
                        for item_y in range(len(self.possible_numbers)):
                            if num in self.possible_numbers[item_y][x] and item_y != y:
                                essential = False
                                break

                    # Look through the possible numbers in the box
                    if not essential:
                        essential = True
                        startRow = (y // 3) * 3
                        startCol = (x // 3) * 3
                        for i in range(startRow, startRow + 3):
                            for j in range(startCol, startCol + 3):
                                if num in self.possible_numbers[i][j] and (i != y or j != x):
                                    essential = False
                                    break

                    # If the number is essential, add it to the board
                    if essential and self.board.get_number(y, x) == 0:
                        self.board.grid[y][x] = num
                        self.possible_numbers[y][x] = [num]
                        if debugDisplay:
                            print(f"Added {num} to row {y} column {x}")
                        added = True
                        progress = True

        # Update main board    
        for y in range(len(self.possible_numbers)):
            for x in range(len(self.possible_numbers[y])):
                # If there is only one possible number, add it to the board
                if len(self.possible_numbers[y][x]) == 1 and self.board.get_number(y, x) == 0:
                    self.board.grid[y][x] = self.possible_numbers[y][x][0]
                    if debugDisplay:
                        print(f"Added {self.possible_numbers[y][x][0]} to row {y} column {x}")

        # Display board and possible numbers in the terminal
        if terminalDisplay:
            self.board.display_board()
            print()
        if debugDisplay:
            for row in self.possible_numbers:
                print(row)

        # Check if board is valid
        if not self.board.check_if_valid():
            raise Exception("Invalid board")

        # Check if the board has been solved
        if self.check_if_solved():
            self.solved = True
        
        return progress, added, removed

    def get_board(self) -> Board:
        return self.board.get_board()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sudoku Solver")
    parser.add_argument("-p", "--progress", help="Display progress in terminal", action="store_true", default=False)
    parser.add_argument("-d", "--debug", help="Display debug information", action="store_true", default=False)
    parser.add_argument("-f", "--file", help="File to load board from", type=str, default="board.json")

    args = parser.parse_args()

    grid = []
    with open(args.file, "r") as f:
        grid = json.load(f)
    board = Board(grid)
    solver = Solver(board)
    while not solver.check_if_solved():
        solver.solve(args.progress, args.debug)
    board.display_board()
    
