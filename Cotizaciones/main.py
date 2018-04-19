import os
import sys
import lib
import config
import constants
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets

import correo
from windows import MainWindow

thread = Thread(target = correo.initCorreo)
thread.setDaemon(True)
thread.start()

if os.path.isdir(constants.OLD_DIR): pass
else: os.makedirs(constants.OLD_DIR)

if os.path.isdir(constants.PDF_DIR): pass
else: os.makedirs(constants.PDF_DIR)

app = QtWidgets.QApplication(sys.argv)
QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion')) # <- Choose the style

# print(QtWidgets.QStyleFactory.keys())

# icon = QtGui.QIcon(':/abacus_small.ico')
# app.setWindowIcon(icon)
app.processEvents()

# main = CotizacionWindow()
main = MainWindow()
# main.setWindowIcon(icon)
main.show()
app.exec_()
