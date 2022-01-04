import math
from PyQt5.QtGui import QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import QPointF

def complex_modulo(a, b):
    x = a / b
    x = math.floor(x.real) + (math.floor(x.imag) * 1j)
    z = x * b
    return a - z


class LinearFunction:

    def __init__(self, a=complex(1,0), b=complex(1,0), modulo=complex(3.0)):
        self._a = a
        self._b = b
        self._modulo = modulo

    def update_modulo(self, modulo:complex):
        self._modulo = modulo

    def update_param_A(self, a: complex):
        self._a = a

    def update_param_B(self, b: complex):
        self._b = b

    def __call__(self, x: complex, y:complex):
        linear_comb = self._a * x + self._b * y
        return complex_modulo(linear_comb, self._modulo)


class GridTraverse:

    def __init__(self):
        pass

    def traverse(self, grid, function=None):
        for n_row, n_col, n_cols in grid.grid_idx:
            if n_row>0 and n_col>0 and n_col<n_cols-1:
                box1 = grid.get_box(n_row-1, n_col-1)
                box2 = grid.get_box(n_row-1, n_col)
                if box1 and box2:
                    if function is None:
                        new_value = complex_modulo(box1.value + box2.value, complex(3,0))
                    else:
                        new_value = function(box1.value, box2.value)
                    grid.set_box_value(n_row, n_col, new_value)


    def traverse_stripe(self, grid, stripe=0, start=complex(1,0), delta=complex(0,0)):
        grid.update_stripe(stripe, start, delta)


class Box:

    def __init__(self, row: int, column: int, contour: QPolygonF, value=complex(0,0)):
        self.row = row
        self.column = column
        self.contour = contour
        self.value = value


class Grid:

    def __init__(self, n_start, n_rows, type="Triangle"):
        self.n_start = n_start
        self.n_rows = n_rows
        self.type = type
        self.data = {}
        self.grid_idx = []


    def update_grid_idx(self):
        self.grid_idx = []
        for n_row in range(self.n_rows):
            if self.type == "Triangle":
                n_cols = self.n_start + n_row
            else:
                n_cols = self.n_start + (n_row % 2==1)

            for n_col in range(n_cols):
                self.grid_idx.append((n_row, n_col, n_cols))


    def update_stripe(self, stripe=0, start=complex(1,0), delta=complex(0,0)):
        self.update_grid_idx()
        for n_row, n_col, n_cols in self.grid_idx:
            if n_row==stripe or n_col==stripe or n_cols-n_col-1==stripe:
                self.data[n_row][n_col].value = start + n_row * delta


    def update_layout(self, **params):
        canvas_width = params.get("canvas_width")
        cell_width = params.get("cell_width")
        cell_padding_x = params.get("cell_padding_x")
        cell_padding_y = params.get("cell_padding_y")

        self.data = {}
        self.update_grid_idx()

        for n_row, n_col, n_cols in self.grid_idx:

            x_start = canvas_width // 2 - (n_cols*cell_width + (n_cols-1)*cell_padding_x) // 2 + n_col*(cell_width+cell_padding_x)
            y_start = 20 + n_row*cell_width + (n_row-1) * cell_padding_y + cell_padding_y

            x_min = x_start
            y_min = y_start
            x_max = x_min + cell_width
            y_max = y_min + cell_width

            x_start += cell_width + cell_padding_x

            box_contour = QPolygonF()
            box_contour.append(QPointF(x_min, y_min))
            box_contour.append(QPointF(x_max, y_min))
            box_contour.append(QPointF(x_max, y_max))
            box_contour.append(QPointF(x_min, y_max))

            if n_row not in self.data:
                self.data[n_row] = {}
            if n_col not in self.data[n_row]:
                self.data[n_row][n_col] = None

            self.data[n_row][n_col] = Box(n_row, n_col, box_contour)

    def get_box(self, row, col):
        if row in self.data:
            if col in self.data[row]:
                return self.data[row][col]
        return None

    def set_box_value(self, row, col, value):
        if row in self.data:
            if col in self.data[row]:
                self.data[row][col].value = value

    def get_boxes(self):
        for r,c,_ in self.grid_idx:
            yield self.data[r][c]

    def get_contours(self):
        for r,c,_ in self.grid_idx:
            yield self.data[r][c].contour