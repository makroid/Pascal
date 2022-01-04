from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, \
    QApplication, QGraphicsPolygonItem, QFormLayout, QCheckBox, QLabel, \
    QSpinBox, QGraphicsSimpleTextItem, QComboBox
from PyQt5.QtCore import pyqtSignal, QPoint,  Qt
from PyQt5.QtGui import QColor, QPen, QBrush, QTransform, QFont, QFontMetrics

from gui_helpers import QHSeperationLine
from pascal_grid import Grid, GridTraverse, LinearFunction, Box

import sys


class GridViewer(QtWidgets.QGraphicsView):
    canvasClicked = pyqtSignal(QPoint)

    def __init__(self, parent):
        super(GridViewer, self).__init__(parent)
        self.parent = parent
        #self.config = parent.config
        self._zoom = 0
        self._scene = QtWidgets.QGraphicsScene(self)
        self._hasDrawing = False
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.grid = None


    def delete_items(self, item_type=None):
        for item in self.items():
            if item_type:
                if isinstance(item, item_type):
                    self._scene.removeItem(item)
            else:
                self._scene.removeItem(item)

    def draw_grid(self, init_delta, n_start, n_rows, ttype, param_A, param_B, modulo):
        self.delete_items()
        self._hasDrawing = True

        self.grid = Grid(n_start, n_rows, ttype)
        grid_params = {"canvas_width": self.width(),
                       "cell_padding_x": 6,
                       "cell_padding_y": 4,
                       "cell_width": 10}

        self.grid.update_layout(**grid_params)

        traverse = GridTraverse()
        traverse.traverse_stripe(self.grid, stripe=0, start=complex(1,0), delta=init_delta)

        linear_func = LinearFunction(param_A, param_B, modulo)

        traverse.traverse(self.grid, function=linear_func)

        for box in self.grid.get_boxes():
            polyItem = QGraphicsPolygonItem(box.contour)

            pen = QPen(Qt.blue, 2)
            if box.value == complex(0,0):
                brush = QBrush(Qt.black)
            else:
                brush = QBrush(Qt.white)
            polyItem.setPen(pen)
            polyItem.setBrush(brush)

            self._scene.addItem(polyItem)


    def draw_grid_values(self):

        self.delete_items(QGraphicsSimpleTextItem)

        font = QFont("Times")
        font.setPointSize(2)
        metrics = QFontMetrics(font)

        for box in self.grid.get_boxes():
            value = box.value
            value_str = str(value)
            value_str = value_str.strip("(")
            value_str = value_str.strip(")")
            str_width = metrics.horizontalAdvance(value_str)
            str_height = metrics.height()
            str_item = QGraphicsSimpleTextItem(value_str)
            str_item.setFont(font)

            b_rect = box.contour.boundingRect()
            x_pos = b_rect.left() + b_rect.width() // 2 - str_width // 2
            y_pos = b_rect.top() + 2

            str_item.setPos(x_pos, y_pos)
            self._scene.addItem(str_item)


    def hasDrawing(self):
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        return self._hasDrawing


    def wheelEvent(self, event):
        if self.hasDrawing():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1

            self.scale(factor, factor)


    def toggleDragMode(self):
        if not self.hasDrawing():
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_P:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)


    def mousePressEvent(self, event):
        if self.hasDrawing():
            self.canvasClicked.emit(self.mapToScene(event.pos()).toPoint())
        if event.button() == Qt.RightButton:
            p = QPoint(event.x(), event.y())
            p = self.mapToScene(p)
            item = self._scene.itemAt(p, QTransform())
            if item:
                if isinstance(item, QGraphicsPolygonItem):
                    self._scene.removeItem(item)
        super(GridViewer, self).mousePressEvent(event)

        self.parent.update_status()


    def mouseMoveEvent(self, event):
        super(GridViewer, self).mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        super(GridViewer, self).mouseReleaseEvent(event)
        self.parent.update_status()


    def show_items(self, item_type, visible=True):
        if not self.hasDrawing():
            return
        for item in self.items():
            if isinstance(item, item_type):
                if visible:
                    item.show()
                else:
                    item.hide()



class GridCanvasFrame(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        # = parent.config

        self.pascal_canvas = GridViewer(self)
        self.pascal_canvas.setMinimumSize(300, 300)

        grid_layout = QGridLayout(self)
        grid_layout.setSpacing(3)

        grid_layout.addWidget(self.pascal_canvas, 1, 0)

        self.statusLabel = QLabel("Status")

        grid_layout.addWidget(self.pascal_canvas, 1, 0)
        grid_layout.addWidget(self.statusLabel, 2, 0, Qt.AlignBottom)

        self.setLayout(grid_layout)


    def update_status(self):
        status = ""
        status += "Status"
        self.statusLabel.setText(status)
        self.parent.setWindowTitle("Pascal")


    def get_modulo(self):
        return self.parent.get_modulo()



class PascalViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.create_gui()


    def create_gui(self):
        self.canvas_frame = GridCanvasFrame(parent=self)
        self.create_control_panel()

        grid = QGridLayout(self)
        grid.setSpacing(3)

        grid.addWidget(self.control_panel, 1, 0)
        grid.addWidget(self.canvas_frame, 1, 1)

        self.setLayout(grid)
        self.update_status()

    def create_control_panel(self):
        self.control_panel = QWidget()

        self.draw_btn = QPushButton("Run")
        self.draw_btn.clicked.connect(self.update_draw_pascal_canvas)

        self.type_combo = QComboBox(self)
        self.type_combo.addItem('Triangle')
        self.type_combo.addItem('Square')

        self.nrows_spin = QSpinBox()
        self.nrows_spin.setMinimum(3)
        self.nrows_spin.setMaximum(256)
        self.nrows_spin.setValue(128)
        self.nrows_spin.setSingleStep(10)
        self.nrows_spin.valueChanged.connect(self.update_draw_pascal_canvas)

        self.nstart_boxes_spin = QSpinBox()
        self.nstart_boxes_spin.setMinimum(1)
        self.nstart_boxes_spin.setMaximum(100)
        self.nstart_boxes_spin.setValue(1)
        self.nstart_boxes_spin.valueChanged.connect(self.update_draw_pascal_canvas)

        self.show_values_box = QCheckBox("Show values")
        self.show_values_box.setChecked(True)

        self.init_delta_real_spin = QSpinBox()
        self.init_delta_real_spin.setMinimum(-10)
        self.init_delta_real_spin.setMaximum(10)
        self.init_delta_real_spin.setValue(0)

        self.init_delta_imag_spin = QSpinBox()
        self.init_delta_imag_spin.setMinimum(-10)
        self.init_delta_imag_spin.setMaximum(10)
        self.init_delta_imag_spin.setValue(0)


        self.modulo_real_spin = QSpinBox()
        self.modulo_real_spin.setMinimum(2)
        self.modulo_real_spin.setMaximum(1000)
        self.modulo_real_spin.setValue(1)
        self.modulo_real_spin.valueChanged.connect(self.update_draw_pascal_canvas)

        self.modulo_imag_spin = QSpinBox()
        self.modulo_imag_spin.setMinimum(0)
        self.modulo_imag_spin.setMaximum(20)
        self.modulo_imag_spin.setValue(0)
        self.modulo_imag_spin.valueChanged.connect(self.update_draw_pascal_canvas)

        self.param_a_real_spin = QSpinBox()
        self.param_a_real_spin.setMinimum(-20)
        self.param_a_real_spin.setMaximum(20)
        self.param_a_real_spin.setValue(1)
        self.param_a_real_spin.valueChanged.connect(self.update_draw_pascal_canvas)

        self.param_a_imag_spin = QSpinBox()
        self.param_a_imag_spin.setMinimum(-20)
        self.param_a_imag_spin.setMaximum(20)
        self.param_a_imag_spin.setValue(0)
        self.param_a_imag_spin.valueChanged.connect(self.update_draw_pascal_canvas)

        self.param_b_real_spin = QSpinBox()
        self.param_b_real_spin.setMinimum(-20)
        self.param_b_real_spin.setMaximum(20)
        self.param_b_real_spin.setValue(1)
        self.param_b_real_spin.valueChanged.connect(self.update_draw_pascal_canvas)

        self.param_b_imag_spin = QSpinBox()
        self.param_b_imag_spin.setMinimum(-20)
        self.param_b_imag_spin.setMaximum(20)
        self.param_b_imag_spin.setValue(0)
        self.param_b_imag_spin.valueChanged.connect(self.update_draw_pascal_canvas)

        control_layout = QFormLayout()
        control_layout.addRow("Draw", self.draw_btn)
        control_layout.addRow("", self.show_values_box)

        control_layout.addRow("Type", self.type_combo)
        control_layout.addRow("Rows", self.nrows_spin)
        control_layout.addRow("Nstart", self.nstart_boxes_spin)

        control_layout.addRow("", self.show_values_box)

        control_layout.addRow(QHSeperationLine())
        control_layout.addRow("Init_d real", self.init_delta_real_spin)
        control_layout.addRow("Init_d imag", self.init_delta_imag_spin)

        control_layout.addRow(QHSeperationLine())
        control_layout.addRow("Modulo real", self.modulo_real_spin)
        control_layout.addRow("Modulo imag", self.modulo_imag_spin)

        control_layout.addRow(QHSeperationLine())
        control_layout.addRow("A real", self.param_a_real_spin)
        control_layout.addRow("A imag", self.param_a_imag_spin)

        control_layout.addRow("B real", self.param_b_real_spin)
        control_layout.addRow("B imag", self.param_b_imag_spin)

        self.show_values_box.stateChanged.connect(self.show_box_values)

        self.control_panel.setMaximumWidth(200)
        self.control_panel.setLayout(control_layout)


    def show_box_values(self):
        is_checked = self.show_values_box.isChecked()
        self.canvas_frame.pascal_canvas.show_items(QGraphicsSimpleTextItem, is_checked)


    def update_draw_pascal_canvas(self):
        grid_params = self.get_grid_params()
        self.canvas_frame.pascal_canvas.draw_grid(grid_params["init_delta"],
                                                  grid_params["n_start"],
                                                  grid_params["n_rows"],
                                                  grid_params["type"],
                                                  self.get_param_A(),
                                                  self.get_param_B(),
                                                  self.get_modulo())
        self.canvas_frame.pascal_canvas.draw_grid_values()
        self.show_box_values()


    def update_status(self):
        self.canvas_frame.update_status()


    def get_modulo(self):
        return complex(self.modulo_real_spin.value(), self.modulo_imag_spin.value())

    def get_param_A(self):
        return complex(self.param_a_real_spin.value(), self.param_a_imag_spin.value())

    def get_param_B(self):
        return complex(self.param_b_real_spin.value(), self.param_b_imag_spin.value())

    def get_grid_params(self):
        n_start = self.nstart_boxes_spin.value()
        n_rows = self.nrows_spin.value()
        ttype = self.type_combo.currentText()
        init_d_real = self.init_delta_real_spin.value()
        init_d_inag = self.init_delta_imag_spin.value()

        return {"n_start": n_start,
                "n_rows": n_rows,
                "init_delta": complex(init_d_real, init_d_inag),
                "type": ttype}


if __name__ == "__main__":

    app = QApplication(sys.argv)

    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    av = PascalViewer()

    av.resize(800, 800)
    av.show()
    app.exec_()


