#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore, QtNetwork
import serial
from serial.tools import list_ports
import binascii
import struct
from time import sleep
from LightWidget import LightWidget
from ParModel import ParModel
from About import About



class MainWidget(QtWidgets.QWidget):
    """Main window of the application."""
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        
        CONDOR_UDP_PORT = 55278
        DEFAULT_BAUDRATE = 9600
        
        self.settings = QtCore.QSettings('CondorUDP2COM', 'CondorUDP2COM')
        self.settings.beginGroup("CONNECTION_CONFIG")
        udpPort = self.settings.value("CONDOR_UDP_PORT", CONDOR_UDP_PORT)
        comPort = self.settings.value("SERIAL_PORT")
        baudRate = self.settings.value("SERIAL_BAUDRATE", DEFAULT_BAUDRATE)
        udpAuto = 2*int(self.settings.value("UDP_AUTO_CONNECT", 0))
        serialAuto = 2*int(self.settings.value("SERIAL_AUTO_CONNECT", 0))
        self.settings.endGroup()
        
        udpGroup = QtWidgets.QGroupBox('Condor UDP')
        portLabel = QtWidgets.QLabel('Port:')
        self.portInput = QtWidgets.QLineEdit()
        self.portInput.setText(str(udpPort))
        self.udpLight = LightWidget(20)
        self.udpStart = QtWidgets.QPushButton('START')
        self.udpStop = QtWidgets.QPushButton('STOP')
        self.udpStart.clicked.connect(self.openUDPConnection)
        self.udpStop.clicked.connect(self.udpStopAct)
        self.udpAutoCheck = QtWidgets.QCheckBox('Connect on startup')
        self.udpAutoCheck.setCheckState(udpAuto)
        self.udpAutoCheck.stateChanged.connect(self.udpAutoAct)
        if udpAuto: self.openUDPConnection()
        udpStartStopLayout = QtWidgets.QHBoxLayout()
        udpStartStopLayout.addWidget(self.udpStart)
        udpStartStopLayout.addWidget(self.udpStop)
        udpStartStopLayout.addWidget(self.udpLight)
        udpLayout = QtWidgets.QGridLayout()
        udpLayout.addWidget(portLabel, 0, 0)
        udpLayout.addWidget(self.portInput, 0, 1)
        udpLayout.addLayout(udpStartStopLayout, 1, 0, 1, 2)
        udpLayout.addWidget(self.udpAutoCheck, 2, 0, 1, 2)
        udpGroup.setLayout(udpLayout)
        
        serialGroup = QtWidgets.QGroupBox('Serial port')
        comLabel = QtWidgets.QLabel('Port:')
        self.comComboBox = QtWidgets.QComboBox()
        self.comComboBox.addItems(self.getCOMlist())
        if comPort:
            index = self.comComboBox.findText(comPort)
            if index >= 0:
                self.comComboBox.setCurrentIndex(index)
        baudLabel = QtWidgets.QLabel('Baudrate:')
        self.baudInput = QtWidgets.QLineEdit()
        self.baudInput.setText(str(baudRate))
        self.serialLight = LightWidget(20)
        self.serialStart = QtWidgets.QPushButton('START')
        self.serialStop = QtWidgets.QPushButton('STOP')
        self.serialStart.clicked.connect(self.serialStartAct)
        self.serialStop.clicked.connect(self.serialStopAct)
        self.serialAutoCheck = QtWidgets.QCheckBox('Connect on startup')
        self.serialAutoCheck.setCheckState(serialAuto)
        self.serialAutoCheck.stateChanged.connect(self.serialAutoAct)
        if serialAuto: self.serialStartAct()
        serialStartStopLayout = QtWidgets.QHBoxLayout()
        serialStartStopLayout.addWidget(self.serialStart)
        serialStartStopLayout.addWidget(self.serialStop)
        serialStartStopLayout.addWidget(self.serialLight)
        serialLayout = QtWidgets.QGridLayout()
        serialLayout.addWidget(comLabel, 0, 0)
        serialLayout.addWidget(self.comComboBox, 0, 1)
        serialLayout.addWidget(baudLabel, 1, 0)
        serialLayout.addWidget(self.baudInput, 1, 1)
        serialLayout.addLayout(serialStartStopLayout, 2, 0, 1, 2)
        serialLayout.addWidget(self.serialAutoCheck, 3, 0, 1, 2)
        serialGroup.setLayout(serialLayout)
        
        udpPreviewGroup = QtWidgets.QGroupBox('UDP Preview')
        self.model = ParModel(self)
        tableView = QtWidgets.QTableView()
        tableView.setModel(self.model)
        tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        udpPreviewLayout = QtWidgets.QGridLayout()
        udpPreviewLayout.addWidget(tableView, 0, 0)
        udpPreviewGroup.setLayout(udpPreviewLayout)
        
        serialPreviewGroup = QtWidgets.QGroupBox('Serial port preview (HEX)')
        self.serialPreviewText = QtWidgets.QPlainTextEdit()
        self.serialPreviewText.setReadOnly(True)
        serialPreviewGroupLayout = QtWidgets.QVBoxLayout()
        serialPreviewGroupLayout.addWidget(self.serialPreviewText)
        serialPreviewGroup.setLayout(serialPreviewGroupLayout)
        
        serialPreviewGroup2 = QtWidgets.QGroupBox('Serial port preview (values)')
        self.serialPreviewText2 = QtWidgets.QPlainTextEdit()
        self.serialPreviewText2.setReadOnly(True)
        serialPreviewGroupLayout2 = QtWidgets.QVBoxLayout()
        serialPreviewGroupLayout2.addWidget(self.serialPreviewText2)
        serialPreviewGroup2.setLayout(serialPreviewGroupLayout2)
        
        serialPreviewLayout = QtWidgets.QVBoxLayout()
        serialPreviewLayout.addWidget(serialPreviewGroup)
        serialPreviewLayout.addWidget(serialPreviewGroup2)
        
        spacer = QtWidgets.QSpacerItem(1, 1, vPolicy=QtWidgets.QSizePolicy.Expanding)
        
        aboutBtn = QtWidgets.QPushButton('About')
        aboutBtn.clicked.connect(self.aboutAct)
        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(udpGroup, 0, 0)
        layout.addWidget(serialGroup, 1, 0)
        layout.addItem(spacer, 2, 0)
        layout.addWidget(aboutBtn, 3, 0)
        layout.addWidget(udpPreviewGroup, 0, 1, 4, 1)
        layout.addLayout(serialPreviewLayout, 0, 2, 4, 1)
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)
        
        self.setWindowTitle('CondorUDP2COM')
        
        self.show()

        
    def udpStopAct(self):
        """Delete UDP socket and turn the light red."""
        if hasattr(self, 'udpSocket'): 
            del(self.udpSocket)
            self.udpLight.turnOff()

        
    def serialStopAct(self):
        """Delete serial port and turn the light red."""
        if hasattr(self, 'serial'):
            del(self.serial)
            self.serialLight.turnOff()

        
    def udpAutoAct(self, state):
        """
        Save auto-connect settings for UDP.
        
        Args:
            state (int): State of the check box.
        """
        self.settings.beginGroup("CONNECTION_CONFIG")
        self.settings.setValue("UDP_AUTO_CONNECT", state/2)
        self.settings.endGroup()

        
    def serialAutoAct(self, state):
        """
        Save auto-connect settings for UDP.
        
        Args:
            state (int): State of the check box.
        """
        self.settings.beginGroup("CONNECTION_CONFIG")
        self.settings.setValue("SERIAL_AUTO_CONNECT", state/2)
        self.settings.endGroup()

        
    def aboutAct(self):
        """Display info box."""
        #QtWidgets.QMessageBox.information(self, 'About', ABOUT)
        about = About(self)
        about.exec_()

        
    def openUDPConnection(self):
        """Open UDP connection, configure from settings and turn the light green."""
        self.udpSocket = QtNetwork.QUdpSocket()
        self.udpSocket.bind(QtNetwork.QHostAddress.LocalHost, int(self.portInput.text()))
        self.udpSocket.readyRead.connect(self.readFromCondor)
        self.settings.beginGroup("CONNECTION_CONFIG")
        self.settings.setValue("CONDOR_UDP_PORT", int(self.portInput.text()))
        self.settings.endGroup()
        self.udpLight.turnOn()

        
    def decodeFrame(self, frame):
        """Decode frame from hex to float"""
        smallFrames = [frame[i:i+6] for i in range(0, len(frame), 6)]
        decoded = ''
        smallFrames.pop(0)
        for i, sFrame in enumerate(smallFrames):
            decoded += chr(sFrame[0])+' '+str(sFrame[1])+' '
            num = sFrame[2:6]
            decoded += str(struct.unpack('f',num)[0]) + '\n'
        self.serialPreviewText2.setPlainText(decoded)

        
    def formatFrame(self):
        """
        Gathers data and encodes them in hex format
        
        Returns:
             bytes: Frame sutable to be sent over COM port.
        """
        start = int('78', 16)
        packedStart = 6*struct.pack('B', start)
        packedZ = bytes('z'.encode('UTF-8'))
        frame = packedStart
        for i,check in enumerate(self.model.checkList):
            if check:
                frame += packedZ
                packedInt = struct.pack('B', i)
                frame += packedInt
                packedFloat = struct.pack('f', self.model.valList[i])
                frame += packedFloat
        hexFrame = binascii.hexlify(frame).decode('UTF-8')
        strBytes = [hexFrame[i:i+2] for i in range(0, len(hexFrame), 2)]
        printHexFrame = ''
        while len(strBytes):
            for i in range(6): printHexFrame += ' '+strBytes.pop(0)
            printHexFrame += '\n'
        self.serialPreviewText.setPlainText(printHexFrame.upper())
        self.decodeFrame(frame)
        return frame
        
        
    def serialStartAct(self):
        """Reads COM port information from the GUI and opens COM port."""
        port = str(self.comComboBox.currentText())
        if not port: return
        baud = int(self.baudInput.text())
        if hasattr(self, 'serial'): del(self.serial)
        self.serial = serial.Serial(port=port, baudrate=baud, writeTimeout=0)
        self.settings.beginGroup("CONNECTION_CONFIG")
        self.settings.setValue("SERIAL_PORT", port)
        self.settings.setValue("SERIAL_BAUDRATE", baud)
        self.settings.endGroup()
        self.serialLight.turnOn()

        
    def getCOMlist(self):
        """
        Gets list of available COM ports.
        
        Returns:
             list of strings
        """
        comports = list_ports.comports()
        comportsList = []
        for port in comports:
            comportsList.append(port[0])
        return comportsList

        
    def readFromCondor(self):
        """Reads data from UDP socket and writes them to COM port."""
        data,_,_ = self.udpSocket.readDatagram(1024)
        lines = [line.strip().split('=') for line in data.decode('UTF-8').split('\n')]
        parList = []
        valList = []
        for line in lines:
            if line[0]:
                try:
                    parList.append(line[0])
                    valList.append(float(line[1]))
                except ValueError:
                    pass
        self.model.updateData(parList, valList)
        if hasattr(self, 'serial'):
            frame = self.formatFrame()
            self.serial.write(frame)
            
            
            
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    pixmap = QtGui.QPixmap()
    pixmap.load('ico.ico')
    app.setWindowIcon(QtGui.QIcon(pixmap))
    w = MainWidget()
    sys.exit(app.exec_())
