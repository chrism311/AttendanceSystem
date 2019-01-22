import sys
import os
from main import main, arguments
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class window(QWidget):
	def __init__(self, parent = None):
		super(window, self).__init__(parent)

		layout = QHBoxLayout()						#Establishes layout for the main window
		self.btnStrt = QPushButton("Start Program")			#Creates 'Start Program' button and connects signal to event
		self.btnStrt.clicked.connect(self.program)			#Event for start button is the main program
		layout.addWidget(self.btnStrt)

		self.btnStop = QPushButton("Quit Program")
		self.btnStop.clicked.connect(self.close)
		layout.addWidget(self.btnStop)

		self.db = QComboBox()						#Creates dropbox with items being the class directories
		self.db.addItems(os.listdir("./ids/"))
		layout.addWidget(self.db)

		self.setLayout(layout)						#Cosmetic changes to window
		self.setWindowTitle("Attendance System")
		self.setGeometry(300, 300, 300, 150)
	
	def program(self):							#Wrapper function for main program with 'id' path tied to dropbox
		self.path = './ids/'+ self.db.currentText()			
		self.args = arguments('./model/20170512-110547/20170512-110547.pb', self.path, '1.0')
		main(self.args)
	
def gui():
	app = QApplication(sys.argv)						
	win = window()								#Main window instance
	win.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	gui()
