import math
from PyQt5.QtGui import QColor, QPen, QBrush, QPolygonF, QTransform, QFont, QFontMetrics

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

def complex_modulo(a, b):
    x = a / b
    x = math.floor(x.real) + (math.floor(x.imag) * 1j)
    z = x * b
    return a - z


def test_1():
    a = complex(7,0)
    b = complex(4,0)

    c = complex_modulo(a, b)
    print(f"c={c}")

    a = complex(7, 0)
    b = complex(7, 0)

    c = complex_modulo(a, b)
    print(f"c={c}")

    print(f"equal={c==complex(0,0)}")


def test_2():
    font = QFont("Helvetica")
    print(font.family())
    #font.setPointSize(10)
    metrics = QFontMetrics(font)

    print("ok")

    btn = QPushButton("Button")
    font_btn = btn.font()

    txt = "Test"
    #txt_width = metrics.width(txt)
    #txt_height = metrics.boundingRect(txt).width()

    print(f"width={txt_height}")


if __name__ == "__main__":
    test_2()