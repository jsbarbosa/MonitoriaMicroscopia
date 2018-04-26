import os
import sys
import lib
import config
import constants
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets

import correo
from windows import MainWindow

PREPARE = False

if os.path.isdir(constants.OLD_DIR): pass
else: os.makedirs(constants.OLD_DIR)

if os.path.isdir(constants.PDF_DIR): pass
else: os.makedirs(constants.PDF_DIR)

app = QtWidgets.QApplication(sys.argv)
QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion')) # <- Choose the style

icon = QtGui.QIcon('icon.ico')
app.setWindowIcon(icon)
# app.processEvents()

# splash_pix = QtGui.QPixmap('logo.png').scaledToWidth(600)
# splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
# splash.show()

icon = QtGui.QIcon('icon.ico')
app.setWindowIcon(icon)
app.processEvents()

if PREPARE:
    print("Starting email...")
    correo.initCorreo()
    print("Email done")

# main = CotizacionWindow()
main = MainWindow()
main.setWindowIcon(icon)
# splash.close()
main.show()
app.exec_()
