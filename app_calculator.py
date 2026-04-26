import sys
from PyQt5.QtWidgets import QApplication
from ui.calc_window import CalculatorWindow

def main():
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
