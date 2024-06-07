import numpy as np
import tkinter as tk
import random

class ShapeInput:
    def __init__(self, master, shape_id):
        self.master = master
        self.shape_id = shape_id
        self.shape = np.zeros((4, 4), dtype=int)
        self.buttons = [[None for _ in range(4)] for _ in range(4)]
        self.frame = tk.Frame(master)
        self.frame.grid(row=shape_id // 4, column=shape_id % 4, padx=5, pady=5)
        tk.Label(self.frame, text=f"Shape {shape_id + 1}").grid(row=0, columnspan=4)
        for i in range(4):
            for j in range(4):
                btn = tk.Button(self.frame, width=2, height=1, command=lambda i=i, j=j: self.toggle_cell(i, j))
                btn.grid(row=i+1, column=j)
                self.buttons[i][j] = btn

    def toggle_cell(self, i, j):
        if self.shape[i, j] == 0:
            self.shape[i, j] = 1
            self.buttons[i][j].configure(bg='black')
        else:
            self.shape[i, j] = 0
            self.buttons[i][j].configure(bg='white')

    def get_shape(self):
        return self.shape

    def get_trimmed_shape(self):
        rows = np.any(self.shape, axis=1)
        cols = np.any(self.shape, axis=0)
        if np.any(rows) and np.any(cols):
            min_row, max_row = np.where(rows)[0][[0, -1]]
            min_col, max_col = np.where(cols)[0][[0, -1]]
            trimmed_shape = self.shape[min_row:max_row+1, min_col:max_col+1]
            return trimmed_shape
        else:
            return np.zeros((0, 0), dtype=int)

class BoardInput:
    def __init__(self, master):
        self.master = master
        self.board = np.zeros((7, 7), dtype=int)
        self.buttons = [[None for _ in range(7)] for _ in range(7)]
        self.frame = tk.Frame(master)
        self.frame.grid(row=0, column=0, columnspan=7)
        tk.Label(self.frame, text="Define Board").grid(row=0, columnspan=7)
        for i in range(7):
            for j in range(7):
                btn = tk.Button(self.frame, width=2, height=1, command=lambda i=i, j=j: self.toggle_cell(i, j))
                btn.grid(row=i+1, column=j)
                self.buttons[i][j] = btn
                if 1 <= i < 6 and 1 <= j < 6:  # Pre-select inner 5x5 cells
                    self.board[i, j] = 1
                    self.buttons[i][j].configure(bg='black')
                else:
                    self.board[i][j] = 0
                    self.buttons[i][j].configure(bg='white')

    def toggle_cell(self, i, j):
        if self.board[i, j] == 0:
            self.board[i, j] = 1
            self.buttons[i][j].configure(bg='black')
        else:
            self.board[i, j] = 0
            self.buttons[i][j].configure(bg='white')

    def get_trimmed_board(self):
        rows = np.any(self.board, axis=1)
        cols = np.any(self.board, axis=0)
        if np.any(rows) and np.any(cols):
            min_row, max_row = np.where(rows)[0][[0, -1]]
            min_col, max_col = np.where(cols)[0][[0, -1]]
            trimmed_board = self.board[min_row:max_row+1, min_col:max_col+1]
            return trimmed_board
        else:
            return np.zeros((0, 0), dtype=int)

def get_shapes():
    shapes = []
    for si in shape_inputs:
        shape = si.get_trimmed_shape()
        if shape.size > 0:  # Include only if there's at least one filled cell
            shapes.append((shape, chr(65 + len(shapes))))
    return shapes

def submit_shapes():
    shapes = get_shapes()
    if len(shapes) > 0:
        shape_window.destroy()
        main(shapes, board)
    else:
        tk.Label(shape_window, text="Please define at least one shape", fg='red').grid(row=5, column=0, columnspan=4)

def open_shape_window(board):
    global shape_window, shape_inputs
    shape_window = tk.Tk()
    shape_window.title("Define Shapes")
    shape_inputs = [ShapeInput(shape_window, i) for i in range(12)]
    submit_button = tk.Button(shape_window, text="Submit Shapes", command=submit_shapes)
    submit_button.grid(row=4, column=0, columnspan=4, pady=10)
    shape_window.mainloop()

def submit_board():
    global board
    board = board_input.get_trimmed_board()
    if board.size > 0:
        board_window.destroy()
        open_shape_window(board)
    else:
        tk.Label(board_window, text="Please define a valid board", fg='red').grid(row=8, column=0, columnspan=4)

def main(shapes, board):
    color_map = generate_color_map(len(shapes))
    inventory = Inventory(board.shape[1], board.shape[0], board)
    if solve(inventory, shapes):
        display_grid(inventory.get_grid(), color_map)
    else:
        print("No solution found")

class Inventory:
    def __init__(self, width, height, board):
        self.width = width
        self.height = height
        self.grid = np.where(board == 1, '.', '#')

    def can_place(self, shape, top_left):
        shape_height, shape_width = shape.shape
        x, y = top_left
        if x + shape_height > self.height or y + shape_width > self.width:
            return False
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i, j] == 1 and self.grid[x + i, y + j] != '.':
                    return False
        return True

    def place_shape(self, shape, top_left, shape_char):
        if not self.can_place(shape, top_left):
            return False
        shape_height, shape_width = shape.shape
        x, y = top_left
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i, j] == 1:
                    self.grid[x + i, y + j] = shape_char
        return True

    def remove_shape(self, shape, top_left):
        shape_height, shape_width = shape.shape
        x, y = top_left
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i, j] == 1:
                    self.grid[x + i, y + j] = '.'

    def get_grid(self):
        return self.grid

def solve(inventory, shapes, index=0):
    if index == len(shapes):
        return True
    shape, shape_char = shapes[index]
    for i in range(inventory.height):
        for j in range(inventory.width):
            if inventory.place_shape(shape, (i, j), shape_char):
                if solve(inventory, shapes, index + 1):
                    return True
                inventory.remove_shape(shape, (i, j))
    return False

def generate_color_map(num_shapes):
    colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'lime', 'gray', 'orange', 'purple', 'pink', 'brown']
    random.shuffle(colors)
    color_map = {chr(65 + i): colors[i % len(colors)] for i in range(num_shapes)}
    color_map['.'] = 'black'
    color_map['#'] = 'white'  # To represent deselected board parts
    return color_map

def display_grid(grid, color_map):
    window = tk.Tk()
    window.title("Inventory Grid")
    cell_size = 50
    canvas = tk.Canvas(window, width=cell_size*len(grid[0]), height=cell_size*len(grid))
    canvas.pack()

    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            color = color_map[cell]
            canvas.create_rectangle(
                j*cell_size, i*cell_size, 
                (j+1)*cell_size, (i+1)*cell_size,
                fill=color, outline="white"
            )

    window.mainloop()

if __name__ == "__main__":
    # First window to define the board
    board_window = tk.Tk()
    board_window.title("Define Board")
    board_input = BoardInput(board_window)
    submit_board_button = tk.Button(board_window, text="Submit Board", command=submit_board)
    submit_board_button.grid(row=8, column=0, columnspan=7, pady=10)
    board_window.mainloop()
