import sys
import os
from main import main, arguments
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class mainWindow(QWidget):
	def __init__(self, parent = None):
		super(mainWindow, self).__init__(parent)

		#Establishes layouts for main window
		layout = QGridLayout()

		#Creates 'Start Program" button and connects signal to an event				
		self.btnStrt = QPushButton("Start Program")
		self.btnStrt.clicked.connect(self.program)				#Event for start button is the main program
		layout.addWidget(self.btnStrt, 0, 0, 2, 1)

		#'Quit Program' button
		self.btnStop = QPushButton("Quit Program")
		self.btnStop.clicked.connect(self.close)
		layout.addWidget(self.btnStop, 1, 1, 2, 1)

		#'Create New Class' button
		self.newClass = QPushButton("Create New Class")
		self.newClass.clicked.connect(self.classInfo)
		layout.addWidget(self.newClass, 1, 1)

		#'Add Student' button
		self.addStud = QPushButton("Add Student")
		self.addStud.clicked.connect(self.studentWindow)
		layout.addWidget(self.addStud, 1, 2)


		#Creates dropbox with items being the classroom directories
		self.db = QComboBox()						
		self.db.addItems(os.listdir("./ids/"))
		layout.addWidget(self.db, 0, 1, 1, 2)

		#Cosmetic changes to window
		self.setLayout(layout)						
		self.setWindowTitle("Attendance System")
		self.setGeometry(300, 300, 300, 200)

	#Window to enter classroom info
	def classInfo(self):
		class_name, ok = QInputDialog.getText(self, 'New Class', 'Class Name:')

	#Wrapper function for student profile
	def studentWindow(self):
		dialog = studProfile(self)
		dialog.show()
		
	#Wrapper function for main program with 'id' path tied to dropbox	
	def program(self):							
		self.path = './ids/'+ self.db.currentText()			
		self.args = arguments('./model/20170512-110547/20170512-110547.pb', self.path, '1.0')
		main(self.args)

#Window to create student profile
class studProfile(QWidget):
	def __init__(self, parent = None):
		super(studProfile, self).__init__(parent)
	
		layout = QGridLayout()
		self.button = QPushButton('button')
		layout.addWidget(self.button, 0,0)

	
def gui():
	app = QApplication(sys.argv)						
	win = mainWindow()
	win.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	gui()
