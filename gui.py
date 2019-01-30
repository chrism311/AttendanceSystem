import sys
import os
import cv2
import datetime
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
		self.newCourse = QPushButton("Create New Course")
		self.newCourse.clicked.connect(self.courseInfo)
		layout.addWidget(self.newCourse, 1, 1)

		#'Add Student' button
		self.addStud = QPushButton("Add Student")
		self.addStud.clicked.connect(self.studentWindow)
		layout.addWidget(self.addStud, 1, 2)


		#Creates dropbox with items being the course directories
		self.db = QComboBox()
		dir_list = ['--Select Course--']
		for i in os.listdir("./ids/"):
			dir_list.append(i)
		self.db.addItems(dir_list)
		self.db.activated[str].connect(self.courseVar)
		layout.addWidget(self.db, 0, 1, 1, 2)

		#Cosmetic changes to window
		self.setLayout(layout)						
		self.setWindowTitle("Attendance System")
		self.setGeometry(300, 300, 300, 200)

	#Assigns course selected in dropbox to variable				
	def courseVar(self):
		self.course = self.db.currentText()
		mainWindow.current_dir = os.getcwd() + '/ids/' + self.course

	#Window to enter course info
	def courseInfo(self):
		course_name, ok = QInputDialog.getText(self, 'New Course', 'Course Name:')
		self.whole_path = os.getcwd()
		mainWindow.current_dir = self.whole_path + '/ids/' + course_name

		#If 'Ok' is clicked, student window is opened to gather their info	
		if ok:
			os.mkdir(mainWindow.current_dir)
			self.course = course_name
			self.studentWindow()
			self.db.clear()
			self.db.addItems(os.listdir("./ids/"))
		#	print(mainWindow.current_dir)

	#Wrapper function for student profile
	def studentWindow(self):
		self.dialog = studProfile()
		self.dialog.show()

		#print(self.course)
		#print(mainWindow.current_dir)
		
	#Wrapper function for main program with 'id' path tied to dropbox	
	def program(self):							
		self.id_path = './ids/'+ self.db.currentText()			
		self.args = arguments('./model/20170512-110547/20170512-110547.pb', self.id_path, '1.0')
		main(self.args)

#Window to create student profile
class studProfile(QWidget):
	def __init__(self, parent = None):
		super(studProfile, self).__init__(parent)
	
		layout = QGridLayout()

		#Text boxes for student info
		self.firstName = QLineEdit()
		self.lastName = QLineEdit()
		self.fnameLabel = QLabel()
		self.lnameLabel = QLabel()
		self.fnameLabel.setText('First Name:')
		self.lnameLabel.setText('Last Name:')
		layout.addWidget(self.firstName, 0, 1)
		layout.addWidget(self.lastName, 1, 1)
		layout.addWidget(self.fnameLabel, 0, 0)
		layout.addWidget(self.lnameLabel, 1, 0)

		#'Continue' button that brings up camera
		self.contBtn = QPushButton('Continue')
		self.contBtn.clicked.connect(self.cont)
		layout.addWidget(self.contBtn, 2,0)

		self.cnlBtn = QPushButton('Cancel')
		self.cnlBtn.clicked.connect(self.close)
		layout.addWidget(self.cnlBtn, 2, 1)

		self.setLayout(layout)
		self.setWindowTitle('Adding Student')
		self.setGeometry(300, 300, 300, 150)

	#Wrapper function for the camera window
	def cont(self):
		student_dir = self.firstName.text() + ' ' + self.lastName.text()
		os.mkdir(mainWindow.current_dir + '/' + student_dir)
		self.dialog = cam()
		self.dialog.show()
		self.close()
		print(mainWindow.current_dir)

#Window for the camera
class cam(QWidget):
	def __init__(self):
		super().__init__()
	
		self.title = 'PyQt5 Video'
		self.setWindowTitle(self.title)
		self.setGeometry(50,50,50, 50)
		self.resize(800, 600)
		label = QLabel(self)
		label.move(80, 35)
		label.resize(640, 480)
		self.th = Thread(self)
		self.th.changePixmap.connect(label.setPixmap)
		self.th.start()

	def closeEvent(self, event):
		self.th.stop()
		QWidget.closeEvent(self, event)

#Camera is under a separate thread
class Thread(QThread):
	changePixmap = pyqtSignal(QPixmap)

	#Initiates thread
	def __init__(self, parent=None):
		QThread.__init__(self, parent=parent)
		self.isRunning = True
	
	#Runs camera with OpenCV
	def run(self):
		cap = cv2.VideoCapture(0)
		while self.isRunning:
			ret, frame = cap.read()
			rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
			convertToQtFormat = QPixmap.fromImage(convertToQtFormat)
			p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
			p = frame.scaled(640, 480, Qt.KeepAspectRatio)
			self.changePixmap.emit(p)

	def stop(self):
		self.isRunning = False
		self.quit()
		self.wait()


####################################################
###################################################
def gui():
	app = QApplication(sys.argv)						
	win = mainWindow()
	win.show()
	sys.exit(app.exec_())

################################################
##############################################
if __name__ == '__main__':
	gui()
