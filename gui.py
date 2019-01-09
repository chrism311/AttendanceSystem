import sys
from main import main, arguments
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def window():
	app = QApplication([])
	win = QDialog()
	win.setGeometry(100,100,400,200)

	button = QPushButton(win)
	button.setText("Start Program")
	button.move(150,70)
	button.clicked.connect(program)

	q_button = QPushButton(win)
	q_button.setText("Quit Program")
	q_button.move(153,105)
	q_button.clicked.connect(quit)

	win.setWindowTitle("Attendance System")
	win.show()
	sys.exit(app.exec_())

def program():
	main(args)


if __name__ == '__main__':
	args = arguments('./model/20170512-110547/20170512-110547.pb', './ids', '1.0')
	
	window()
