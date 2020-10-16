# python OpenCV QT player

import sys
import cv2
from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtGui import QImage
import time

class VideoCapture(QtWidgets.QWidget):
    def __init__(self, parent = None):
        # Use super() to call __init__() methods in the parent classes
        super(VideoCapture, self).__init__()

        # The instantiated QLabel object should belong to the 'self' QWidget object
        self.label = QtWidgets.QLabel(self) 

        # Set the QLabel geometry to fit the image dimension (640, 480)
        # The top left corner (0, 0) is the position within the QWidget main window
        self.label.setGeometry(0,0,640,480)

        # Instantiate a QThread object. No need to pass in the parent QWidget object.
        self.workThread = WorkThread()

        # Connect signal from self.workThread to the slot self.draw
        self.connect(self.workThread, QtCore.SIGNAL('update_Camera'), self.draw)

        self.workThread.start()

    def closeEvent(self, event):
        self.workThread.stop()
        event.accept()

    def draw(self, img):
        print("I should Redraw")
        height, width, channel = img.shape
        bpl = 3 * width
        self.qImg = QImage(img, width, height, bpl, QImage.Format_RGB888)
        pix = QtGui.QPixmap(self.qImg)
        self.label.setPixmap(pix)
        self.label.show()


class WorkThread(QtCore.QThread):
    def __init__(self):
        # Use super() to call __init__() methods in the parent classes
        super(WorkThread, self).__init__()

        # Place the camera object in the WorkThread
        self.camera = cv2.VideoCapture(0)

        # The boolean variable to break the while loop in self.run() method
        self.running = True

    def run(self):
        while self.running:

            # Read one frame
            b, self.frame = self.camera.read()
            
            yield self.frame

            # Emit self.frame to the QWidget object
            #self.emit(QtCore.SIGNAL('update_Camera'), self.frame)

    def stop(self):
        # Terminate the while loop in self.run() method
        self.running = False


app = QtWidgets.QApplication(sys.argv)
video_capture_widget = VideoCapture()
video_capture_widget.show()
sys.exit(app.exec_())
