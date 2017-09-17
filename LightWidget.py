from PyQt5 import QtCore, QtGui, QtWidgets

class LightWidget(QtWidgets.QWidget):
    """
    Widget to control green / red light.
    """
    def __init__(self, size):
        """
        Args:
            size (int): Size of the light.
        """
        QtWidgets.QWidget.__init__(self)
        self.setFixedSize(size, size)
        self.brush = QtCore.Qt.red

        
    def turnOn(self):
        """Turn the light green"""
        self.brush = QtCore.Qt.green
        self.update()

        
    def turnOff(self):
        """Turn the light red"""
        self.brush = QtCore.Qt.red
        self.update()

        
    def paintEvent(self, event):
        """
        Args:
            event (QtGui.QPaintEvent): paint event
        """
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtGui.QBrush(self.brush))
        rect = QtCore.QRect(0, 0, 0.99*event.rect().width(), 0.99*event.rect().height())
        painter.drawEllipse(rect)
        painter.end()
