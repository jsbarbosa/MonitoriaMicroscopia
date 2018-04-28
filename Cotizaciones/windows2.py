import os
import codecs
import datetime
import traceback
import numpy as np
import pandas as pd
from time import sleep
from threading import Thread
from unidecode import unidecode
from PyQt5 import QtCore, QtGui, QtWidgets

import lib
import correo
import config
import constants

# def readDataFrames():
#     return pd.read_excel(constants.CLIENTES_FILE), pd.read_excel(constants.REGISTRO_FILE)
#
# CLIENTES_DATAFRAME, REGISTRO_DATAFRAME = readDataFrames()

class Table(QtWidgets.QTableWidget):
    HEADER = ['Código', 'Descripción', 'Cantidad', 'Precio Unitario', 'Precio Total']
    def __init__(self, parent, rows = 10, cols = 5):
        super(QtWidgets.QTableWidget, self).__init__(rows, cols)
        self.parent = parent
        self.n_rows = rows
        self.n_cols = cols
        self.setHorizontalHeaderLabels(self.HEADER)
        self.resizeRowsToContents()

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.clean()

        self.cellChanged.connect(self.handler)
        self.IS_CLEANING = False

    def handler(self, row, col):
        item = self.item(row, col)
        n = 1
        val = 0
        self.blockSignals(True)
        if not self.IS_CLEANING:
            try:
                if col == 0:
                    equipo = eval("constants.%s"%self.parent.equipo_widget.currentText())
                    interno = self.parent.interno_widget.checkState()
                    val = "Externo"
                    if interno: val = "Interno"
                    try: cod = int(str(int(item.text()))[-1])
                    except: cod = -1
                    t = []
                    try:
                        t = [self.item(i, 0).text() for i in range(self.n_rows)]
                        del t[row]
                    except:
                        pass

                    if str(cod) in t:
                        self.item(row, 0).setText('')
                        raise(Exception("Código %d ya se encuentra registrado."%cod))

                    line = equipo[equipo["Código"] == cod]
                    if line.shape[0] == 1:
                        d = line["Descripción"].values[0]
                        val = line[val].values[0]
                        self.item(row, 1).setText(d)
                        self.item(row, 3).setText("{:,}".format(val))
                        try:
                            n = round(float(self.item(row, 2).text().replace(",", "")), 1)
                        except:
                            n = 1
                        # self.item(row, 4).setText("{:,}".format(val * n))
                if col == 2:
                    try:
                        val = int(self.item(row, 3).text().replace(",", ""))
                        n = round(float(self.item(row, 2).text().replace(",", "")), 1)
                    except:
                        val = 0
                        n = 1
                if col == 4:
                    try:
                        total = int(self.item(row, 4).text().replace(",", ""))
                        val = int(self.item(row, 3).text(). replace(",", ""))
                        n = total / val
                        self.item(row, 2).setText("%.1f"%n)
                    except: pass
                try: self.item(row, 4).setText("{:,}".format(int(val * n)))
                except: pass
                total = self.getTotal()
                self.parent.total_widget.setText(total)

            except Exception as e:
                self.parent.errorWindow(e)

        self.blockSignals(False)

    def getTotal(self):
        total = 0
        for i in range(self.n_rows):
            try: text = self.item(i, 4).text().replace(",", "")
            except AttributeError: text = ""
            try:
                val = round(float(text), 1)
            except:
                val = 0
            total += val
        return "{:,}".format(int(total))

    def setCodigos(self, codigos):
        for i in range(len(codigos)):
            self.item(i, 0).setText(codigos[i])

    def setCantidades(self, cantidades):
        for i in range(len(cantidades)):
            try:
                val = float(cantidades[i])
                self.item(i, 2).setText("%.1f"%val)
            except: pass

    def getCodigos(self):
        return [self.item(i, 0).text() for i in range(self.n_rows)]

    def getCantidades(self):
        new = [""]*self.n_rows
        for i in range(self.n_rows):
            try:
                total = int(self.item(i, 4).text().replace(",", ""))
                price = int(self.item(i, 3).text().replace(",", ""))
                new[i] = "%f"%(total / price)
            except: pass
        return new

    def updateInterno(self):
        for i in range(self.n_rows):
            self.handler(i, 0)

    def clean(self):
        self.IS_CLEANING = True
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                item = QtWidgets.QTableWidgetItem("")
                self.setItem(r, c, item)
        self.readOnly()
        self.IS_CLEANING = False

    def readOnly(self):
        flags = QtCore.Qt.ItemIsEditable
        for r in range(self.n_rows):
            for c in [1, 3]:
                item = QtWidgets.QTableWidgetItem("")
                item.setFlags(flags)
                self.setItem(r, c, item)

class AutoLineEdit(QtWidgets.QLineEdit):
    AUTOCOMPLETE = ["Nombre", "Correo", "Documento", "Teléfono", "Cotización"]
    def __init__(self, target, parent, autochange = True):
        super(QtWidgets.QLineEdit, self).__init__()
        self.target = target
        self.parent = parent
        self.model = QtCore.QStringListModel()

        completer = QtWidgets.QCompleter()
        completer.setCaseSensitivity(False)
        completer.setModelSorting(0)
        completer.setModel(self.model)
        self.setCompleter(completer)

        self.update()

        if autochange: self.textChanged.connect(self.change)

    def change(self, value):
        global CLIENTES_DATAFRAME, REGISTRO_DATAFRAME
        if type(self.parent) is CotizacionWindow:
            dataframe = CLIENTES_DATAFRAME
            range_ = len(self.parent.FIELDS) -3
        else:
            dataframe = REGISTRO_DATAFRAME
            range_ = len(self.parent.FIELDS)

        try:
            df = dataframe.loc[dataframe[self.target] == value]
            rows = df.shape[0]
        except TypeError as e:
            rows = 0

        if (rows == 1) and (self.target in self.AUTOCOMPLETE):
            for i in range(range_):
                field = self.parent.FIELDS[i]
                widget = self.parent.WIDGETS[i]
                if field != self.target:
                    val = df[field].values[0]
                    if (val is np.nan) or (val == None):
                        val = ""
                    if widget != "interno":
                        eval("self.parent.%s_widget.setText('%s')"%(widget, val))

                    else:
                        if val == "Externo": self.parent.interno_widget.setCheckState(0)
                        else: self.parent.interno_widget.setCheckState(2)

    def update(self):
        if type(self.parent) is CotizacionWindow:
            dataframe = CLIENTES_DATAFRAME
            order = 1
        else:
            dataframe = REGISTRO_DATAFRAME
            order = -1
        data = list(set(dataframe[self.target].values.astype('str')))
        data = sorted(data)[::order]
        self.model.setStringList(data)

class ChangeCotizacion(QtWidgets.QDialog):
    FIELDS = ["Cotización", "Fecha", "Nombre", "Correo", "Equipo", "Valor"]
    WIDGETS = ["cotizacion", "fecha", "nombre", "correo", "equipo", "valor"]

    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__()
        self.setWindowTitle("Modificar cotización")

        self.parent = parent

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.form = QtWidgets.QFrame()
        self.form_layout = QtWidgets.QFormLayout(self.form)

        cotizacion_label = QtWidgets.QLabel("Cotización:")
        self.cotizacion_widget = AutoLineEdit("Cotización", self)

        fecha_label = QtWidgets.QLabel("Fecha:")
        self.fecha_widget = QtWidgets.QLabel("")

        nombre_label = QtWidgets.QLabel("Nombre:")
        self.nombre_widget = QtWidgets.QLabel("")

        correo_label = QtWidgets.QLabel("Correo:")
        self.correo_widget = QtWidgets.QLabel("")

        equipo_label = QtWidgets.QLabel("Equipo:")
        self.equipo_widget = QtWidgets.QLabel("")

        valor_label = QtWidgets.QLabel("Valor:")
        self.valor_widget = QtWidgets.QLabel("")

        self.form_layout.addRow(cotizacion_label, self.cotizacion_widget)
        self.form_layout.addRow(fecha_label, self.fecha_widget)
        self.form_layout.addRow(nombre_label, self.nombre_widget)
        self.form_layout.addRow(correo_label, self.correo_widget)
        self.form_layout.addRow(equipo_label, self.equipo_widget)
        self.form_layout.addRow(valor_label, self.valor_widget)

        self.layout.addWidget(self.form)

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)

        self.layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.accept2)
        self.buttons.rejected.connect(self.reject)

    def accept2(self):
        self.parent.loadCotizacion(self.cotizacion_widget.text())
        self.accept()

class CotizacionWindow(QtWidgets.QMainWindow):
    IGNORE = ["Proyecto", "Código"]
    FIELDS = ["Nombre", "Correo", "Teléfono", "Institución", "Documento", "Dirección", "Ciudad", "Interno", "Responsable", "Proyecto", "Código", "Muestra"]
    WIDGETS = ["nombre", "correo", "telefono", "institucion", "documento", "direccion", "ciudad", "interno", "responsable", "proyecto", "codigo", "muestra"]

    REGISTRO_FIELDS = ["Cotización", "Fecha", "Nombre", "Correo", "Teléfono", "Institución", "Interno", "Responsable", "Muestra", "Equipo", "Valor"]
    def __init__(self, parent = None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.setWindowTitle("Cotización")

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        self.resize(600, 570)

        self.verticalLayout = QtWidgets.QVBoxLayout(wid)

        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)

        self.cotizacion_frame = QtWidgets.QFrame()
        self.form_frame = QtWidgets.QFrame()
        self.button_frame = QtWidgets.QFrame()
        self.total_frame = QtWidgets.QFrame()

        self.cotizacion_frame_layout = QtWidgets.QHBoxLayout(self.cotizacion_frame)
        self.numero_cotizacion = QtWidgets.QPushButton()
        self.cotizacion_frame_layout.addWidget(self.numero_cotizacion)

        self.form_frame_layout = QtWidgets.QGridLayout(self.form_frame)

        nombre_label = QtWidgets.QLabel("Nombre:")
        self.nombre_widget = AutoLineEdit("Nombre", self)
        correo_label = QtWidgets.QLabel("Correo:")
        self.correo_widget = AutoLineEdit("Correo", self)

        institucion_label = QtWidgets.QLabel("Institución/Empresa:")
        self.institucion_widget = AutoLineEdit("Institución", self)
        documento_label = QtWidgets.QLabel("Nit/CC:")
        self.documento_widget = AutoLineEdit("Documento", self)

        direccion_label = QtWidgets.QLabel("Dirección:")
        self.direccion_widget = AutoLineEdit("Dirección", self)
        ciudad_label = QtWidgets.QLabel("Ciudad:")
        self.ciudad_widget = AutoLineEdit("Ciudad", self)

        telefono_label = QtWidgets.QLabel("Teléfono:")
        self.telefono_widget = AutoLineEdit("Teléfono", self)

        interno_label = QtWidgets.QLabel("Interno:")
        self.interno_widget = QtWidgets.QCheckBox()
        responsable_label = QtWidgets.QLabel("Responsable:")
        self.responsable_widget = AutoLineEdit("Responsable", self)

        proyecto_label = QtWidgets.QLabel("Nombre proyecto:")
        self.proyecto_widget = QtWidgets.QLineEdit()
        codigo_label = QtWidgets.QLabel("Código proyecto:")
        self.codigo_widget = QtWidgets.QLineEdit()

        muestra_label = QtWidgets.QLabel("Tipo de muestras:")
        self.muestra_widget = QtWidgets.QLineEdit()

        equipo_label = QtWidgets.QLabel("Equipo:")
        self.equipo_widget = QtWidgets.QComboBox()
        self.equipo_widget.addItems(config.EQUIPOS)

        self.form_frame_layout.addWidget(nombre_label, 0, 0)
        self.form_frame_layout.addWidget(self.nombre_widget, 0, 1)
        self.form_frame_layout.addWidget(correo_label, 0, 2)
        self.form_frame_layout.addWidget(self.correo_widget, 0, 3)

        self.form_frame_layout.addWidget(institucion_label, 1, 0)
        self.form_frame_layout.addWidget(self.institucion_widget, 1, 1)
        self.form_frame_layout.addWidget(documento_label, 1, 2)
        self.form_frame_layout.addWidget(self.documento_widget, 1, 3)

        self.form_frame_layout.addWidget(direccion_label, 2, 0)
        self.form_frame_layout.addWidget(self.direccion_widget, 2, 1)
        self.form_frame_layout.addWidget(ciudad_label, 2, 2)
        self.form_frame_layout.addWidget(self.ciudad_widget, 2, 3)

        self.form_frame_layout.addWidget(telefono_label, 3, 0)
        self.form_frame_layout.addWidget(self.telefono_widget, 3, 1)

        self.form_frame_layout.addWidget(responsable_label, 4, 0)
        self.form_frame_layout.addWidget(self.responsable_widget, 4, 1)
        self.form_frame_layout.addWidget(interno_label, 4, 2)
        self.form_frame_layout.addWidget(self.interno_widget, 4, 3)

        self.form_frame_layout.addWidget(proyecto_label, 5, 0)
        self.form_frame_layout.addWidget(self.proyecto_widget, 5, 1)
        self.form_frame_layout.addWidget(codigo_label, 5, 2)
        self.form_frame_layout.addWidget(self.codigo_widget, 5, 3)

        self.form_frame_layout.addWidget(muestra_label, 6, 0)
        self.form_frame_layout.addWidget(self.muestra_widget, 6, 1)
        self.form_frame_layout.addWidget(equipo_label, 6, 2)
        self.form_frame_layout.addWidget(self.equipo_widget, 6, 3)

        self.table = Table(self)

        self.button_frame_layout = QtWidgets.QHBoxLayout(self.button_frame)
        self.notificar_widget = QtWidgets.QCheckBox()
        self.notificar_widget.setCheckState(2)
        notificar = QtWidgets.QLabel("Notificar")
        self.guardar_button = QtWidgets.QPushButton("Guardar")
        self.limpiar_button = QtWidgets.QPushButton("Limpiar")

        self.button_frame_layout.addWidget(self.notificar_widget)
        self.button_frame_layout.addWidget(notificar)
        self.button_frame_layout.addWidget(self.guardar_button)
        self.button_frame_layout.addWidget(self.limpiar_button)

        self.total_frame_layout = QtWidgets.QHBoxLayout(self.total_frame)
        total_label = QtWidgets.QLabel("Total:")
        self.total_widget = QtWidgets.QLabel()

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.cotizacion_frame.setSizePolicy(sizePolicy)
        self.total_frame.setSizePolicy(sizePolicy)
        self.button_frame.setSizePolicy(sizePolicy)

        self.cotizacion_frame_layout.setAlignment(QtCore.Qt.AlignRight)
        self.total_frame_layout.setAlignment(QtCore.Qt.AlignRight)
        self.button_frame_layout.setAlignment(QtCore.Qt.AlignRight)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignRight)

        self.total_frame_layout.addWidget(total_label)
        self.total_frame_layout.addWidget(self.total_widget)

        self.verticalLayout.addWidget(self.cotizacion_frame)
        self.verticalLayout.addWidget(self.form_frame)
        self.verticalLayout.addWidget(self.table)
        self.verticalLayout.addWidget(self.total_frame)
        self.verticalLayout.addWidget(self.button_frame)

        self.interno_widget.setChecked(2)

        self.interno_widget.stateChanged.connect(self.internoHandler)
        self.guardar_button.clicked.connect(self.guardar)
        self.limpiar_button.clicked.connect(self.limpiar)

        self.CURRENT_INDEX_INIT = True

        self.numero_cotizacion.clicked.connect(self.changeCotizacion)
        self.equipo_widget.currentIndexChanged.connect(self.changeEquipo)

        self.changeEquipo(0)
        self.centerOnScreen()

        self.cotizacion = None

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def getFields(self):
        ans = []
        for item in self.FIELDS:
            ascii = unidecode(item.lower())
            if item != "Interno":
                val = eval("self.%s_widget.text()"%ascii)
            else:
                interno = eval("self.%s_widget.checkState()"%ascii)
                if interno == 2:
                    interno = True
                    val = "Interno"
                else:
                    interno = False
                    val = "Externo"
            if (item == "Responsable") and (not interno):
                val = None

            if (val == "") and not (item in self.IGNORE):
                raise(Exception("Se deben completar todos los campos"))
            ans.append(val)

        if ans[7] == None: ans[7] == ""
        return ans

    def changeCotizacion(self):
        temp = ChangeCotizacion(self)
        temp.exec_()

    def loadCotizacion(self, name):
        try:
            path = os.path.join(constants.OLD_DIR, name + ".py")
            c = lib.Cotizacion(path)
            for widget in self.WIDGETS:
                val = eval("c.%s"%widget)
                exec("self.%s_widget.setText('%s')"%(widget, val))

            self.table.setCodigos(c.codigos)
            self.table.setCantidades(c.cantidades)

            self.numero_cotizacion.setText(name)
            self.cotizacion = c
        except FileNotFoundError as e:
            self.errorWindow(e)

    def changeEquipo(self, index):
        self.updateCotizacionNumber()
        if not self.CURRENT_INDEX_INIT:
            self.table.clean()
        else:
            self.CURRENT_INDEX_INIT = not self.CURRENT_INDEX_INIT

    def updateCotizacionNumber(self):
        year = str(datetime.datetime.now().year)[-2:]
        last = self.getLastCotizacion()
        equipo = self.equipo_widget.currentText()[0]
        self.numero_cotizacion.setText("%s%s-%04d"%(equipo, year, last + 1))

    def getLastCotizacion(self):
        global REGISTRO_DATAFRAME
        try:
            equipo = self.equipo_widget.currentText()
            df = REGISTRO_DATAFRAME[REGISTRO_DATAFRAME["Equipo"] == equipo]
            val = df["Cotización"].values[0]
            cod, last = val.split("-")
        except Exception as e:
            return 0
        year = int(str(datetime.datetime.now().year)[-2:])
        if year > int(cod[1:]): print("Here"); return 0
        else: return int(last)

    def generatePDF(self, cotizacion):
        cotizacion = os.path.join(constants.OLD_DIR, cotizacion + ".py")
        cotizacion = lib.Cotizacion(cotizacion)
        lib.PDFCotizacion(cotizacion)

    def sendEmail(self, to, file):
        if self.notificar_widget.isChecked():
            thread = Thread(target = correo.sendCotizacion, args = (to, file))
            # thread.setDaemon(True)
            thread.start()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("El usuario no será notificado.")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()

    def guardar(self):
        global CLIENTES_DATAFRAME, REGISTRO_DATAFRAME
        try:
            fields = self.getFields()
            last = CLIENTES_DATAFRAME.shape[0]

            fields2 = fields[:4] + fields[7:]

            fecha = datetime.datetime.now().replace(microsecond = 0)
            equipo = self.equipo_widget.currentText()
            valor = int(self.total_widget.text().replace(",", ""))

            codigos = self.table.getCodigos()
            cantidades = self.table.getCantidades()

            if all(item == "" for item in codigos):
                raise(Exception("Ningún servicio ha sido cotizado."))

            for i in range(len(codigos)):
                if codigos[i] != "":
                    codigos[i] = codigos[i][-1]
                    if cantidades[i] == "": cantidades[i] = "1"
            codigos = str(codigos)
            cantidades = str(cantidades)

            CLIENTES_DATAFRAME.loc[last] = fields[:-3]
            CLIENTES_DATAFRAME = CLIENTES_DATAFRAME.drop_duplicates("Nombre", "last")
            CLIENTES_DATAFRAME = CLIENTES_DATAFRAME.sort_values("Nombre")
            CLIENTES_DATAFRAME.to_excel("Clientes.xlsx", index = False)

            last = self.numero_cotizacion.text()
            last_index = REGISTRO_DATAFRAME.shape[0]
            fields2 = [last, fecha] + fields2 + [equipo, valor]

            REGISTRO_DATAFRAME.loc[last_index] = fields2

            REGISTRO_DATAFRAME = REGISTRO_DATAFRAME.drop_duplicates("Cotización", "last")
            REGISTRO_DATAFRAME = REGISTRO_DATAFRAME.sort_values("Cotización", ascending = False)
            REGISTRO_DATAFRAME = REGISTRO_DATAFRAME.reset_index(drop = True)

            writer = pd.ExcelWriter("Registro.xlsx", engine='xlsxwriter',
                        datetime_format= "dd/mm/yy hh:mm")

            REGISTRO_DATAFRAME.to_excel(writer, index = False)

            registro = {}
            usos = None
            if self.cotizacion != None:
                registro = self.cotizacion.registro_cambios
                usos = self.cotizacion.usos
            fields.append(last)
            cot = lib.Cotizacion(fields, equipo, codigos, cantidades, usos = usos, cambios = registro)
            cot.save()
            self.generatePDF(cot.id)
            self.sendEmail(cot.correo, cot.id)
            self.nombre_widget.update()
            self.limpiar()

        except Exception as e:
            traceback.print_exc()
            self.errorWindow(e)

        self.changeEquipo(0)

    def limpiar(self):
        for item in self.WIDGETS:
            if item != "interno":
                eval('self.%s_widget.setText("")'%item)
            else:
                self.interno_widget.setChecked(2)
        self.table.clean()
        self.cotizacion = None

    def errorWindow(self, exception):
        error_text = str(exception)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(error_text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def internoHandler(self, state):
        if state == 2:
            self.responsable_widget.setEnabled(True)
            self.proyecto_widget.setEnabled(True)
            self.codigo_widget.setEnabled(True)
        else:
            self.responsable_widget.setEnabled(False)
            self.proyecto_widget.setEnabled(False)
            self.codigo_widget.setEnabled(False)
            self.responsable_widget.setText("")
            self.proyecto_widget.setText("")
            self.codigo_widget.setText("")

        self.table.updateInterno()

class DescontarWindow(QtWidgets.QMainWindow):
    FIELDS = ["Cotización", "Fecha", "Nombre", "Correo", "Equipo", "Valor"]
    WIDGETS = ["cotizacion", "fecha", "nombre", "correo", "equipo", "valor"]

    def __init__(self, parent = None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.setWindowTitle("Descontar servicios")

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)

        self.layout = QtWidgets.QVBoxLayout(wid)
        self.form = QtWidgets.QFrame()
        self.form_layout = QtWidgets.QFormLayout(self.form)
        cotizacion_label = QtWidgets.QLabel("Cotización:")
        self.cotizacion_widget = AutoLineEdit("Cotización", self)
        fecha_label = QtWidgets.QLabel("Fecha:")
        self.fecha_widget = QtWidgets.QLabel("")
        nombre_label = QtWidgets.QLabel("Nombre:")
        self.nombre_widget = QtWidgets.QLabel("")
        correo_label = QtWidgets.QLabel("Correo:")
        self.correo_widget = QtWidgets.QLabel("")
        equipo_label = QtWidgets.QLabel("Equipo:")
        self.equipo_widget = QtWidgets.QLabel("")
        valor_label = QtWidgets.QLabel("Valor:")
        self.valor_widget = QtWidgets.QLabel("")

        self.form_layout.addRow(cotizacion_label, self.cotizacion_widget)
        self.form_layout.addRow(fecha_label, self.fecha_widget)
        self.form_layout.addRow(nombre_label, self.nombre_widget)
        self.form_layout.addRow(correo_label, self.correo_widget)
        self.form_layout.addRow(equipo_label, self.equipo_widget)
        self.form_layout.addRow(valor_label, self.valor_widget)

        self.layout.addWidget(self.form)

        self.item_frame = QtWidgets.QFrame()
        self.item_frame.setFrameStyle(1)
        self.item_layout = QtWidgets.QGridLayout(self.item_frame)
        cod = QtWidgets.QLabel("Código")
        des = QtWidgets.QLabel("Descripción")
        n = QtWidgets.QLabel("Cantidad")
        self.item_layout.addWidget(cod, 0, 0)
        self.item_layout.addWidget(des, 0, 1)
        self.item_layout.addWidget(n, 0, 2)

        self.layout.addWidget(self.item_frame)

        self.buttons_frame = QtWidgets.QFrame()
        self.buttons_layout = QtWidgets.QHBoxLayout(self.buttons_frame)
        self.guardar_button = QtWidgets.QPushButton("Guardar")
        self.notificar_widget = QtWidgets.QCheckBox()
        self.notificar_widget.setCheckState(2)
        notificar = QtWidgets.QLabel("Notificar")

        self.buttons_layout.addWidget(self.notificar_widget)
        self.buttons_layout.addWidget(notificar)
        self.buttons_layout.addWidget(self.guardar_button)

        self.layout.addWidget(self.buttons_frame)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.buttons_frame.setSizePolicy(sizePolicy)
        self.buttons_layout.setAlignment(QtCore.Qt.AlignRight)

        self.cotizacion_widget.textChanged.connect(self.cotizacionChanged)
        self.guardar_button.clicked.connect(self.guardarHandler)

        self.floats_labels = []
        self.floats_spins = []
        self.cotizacion = None
        self.init_size = (400, 100)
        self.resize(*self.init_size)

    def updateDataFrames(self):
        self.cotizacion_widget.update()

    def guardarHandler(self):
        if self.cotizacion != None:
            vals = [spin.value() for spin in self.floats_spins]
            self.cotizacion.makeRegister(vals)
            lib.PDFReporte(self.cotizacion)
            self.sendEmail(self.cotizacion.correo, self.cotizacion.id)
            for widget in self.WIDGETS: exec("self.%s_widget.setText('')"%widget)

    def sendEmail(self, to, file):
        if self.notificar_widget.isChecked():
            thread = Thread(target = correo.sendRegistro, args = (to, file))
            # thread.setDaemon(True)
            thread.start()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("El usuario no será notificado.")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()

    def cotizacionChanged(self):
        n = 0
        text = self.cotizacion_widget.text()
        self.cleanWidgets()
        try:
            file = os.path.join(constants.OLD_DIR, text + ".py")
            self.cotizacion = lib.Cotizacion(file)
            table = self.cotizacion.descontarTable()
            n = table.shape[0]
        except: pass

        for i in range(n):
            cod = QtWidgets.QLabel(table[i, 0])
            dec = QtWidgets.QLabel(table[i, 1])
            paid = round(float(table[i, 2]), 1)
            used = round(float(table[i, 3]), 1)
            # spin = QtWidgets.QSpinBox()
            spin = QtWidgets.QDoubleSpinBox()
            total = QtWidgets.QLabel("%.1f/%.1f"%(used, paid))
            spin.setMinimum(0)
            spin.setDecimals(1)
            spin.setMaximum(paid - used)
            spin.setSingleStep(0.1)
            self.item_layout.addWidget(cod, i + 1, 0)
            self.item_layout.addWidget(dec, i + 1, 1)
            self.item_layout.addWidget(spin, i + 1, 2)
            self.item_layout.addWidget(total, i + 1, 3)
            self.floats_labels.append(cod)
            self.floats_labels.append(dec)
            self.floats_spins.append(spin)
            self.floats_labels.append(total)

    def cleanWidgets(self):
        for item in self.floats_labels:
            self.item_layout.removeWidget(item)
            item.deleteLater()
        for item in self.floats_spins:
            self.item_layout.removeWidget(item)
            item.deleteLater()
        self.floats_labels = []
        self.floats_spins = []
        self.cotizacion = None
        self.resize(*self.init_size)

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        self.headerdata = data.keys()

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.values[index.row()][index.column()]))
        return QtCore.QVariant()

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()

class BuscarWindow(QtWidgets.QMainWindow):
    WIDGETS = ["equipo", "nombre", "institucion", "responsable"]
    FIELDS = ["Equipo", "Nombre", "Institución", "Responsable"]
    def __init__(self, parent = None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.setWindowTitle("Buscar")

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)

        self.layout = QtWidgets.QVBoxLayout(wid)

        form = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(form)

        self.form1 = QtWidgets.QFrame()
        self.form1_layout = QtWidgets.QFormLayout(self.form1)
        self.form2 = QtWidgets.QFrame()
        self.form2_layout = QtWidgets.QFormLayout(self.form2)

        self.from_form = QtWidgets.QFrame()
        self.to_form = QtWidgets.QFrame()
        self.from_layout = QtWidgets.QHBoxLayout(self.from_form)
        self.to_layout = QtWidgets.QHBoxLayout(self.to_form)

        layout.addWidget(self.form1)
        layout.addWidget(self.form2)

        self.equipo_widget = AutoLineEdit('Equipo', self, False)
        self.nombre_widget = AutoLineEdit('Nombre', self, False)
        self.institucion_widget = AutoLineEdit("Institución", self, False)
        self.responsable_widget = AutoLineEdit("Responsable", self, False)
        # self.


        self.form1_layout.addRow(QtWidgets.QLabel('Equipo'), self.equipo_widget)
        self.form1_layout.addRow(QtWidgets.QLabel('Nombre'), self.nombre_widget)
        self.form2_layout.addRow(QtWidgets.QLabel('Institución'), self.institucion_widget)
        self.form2_layout.addRow(QtWidgets.QLabel('Responsable'), self.responsable_widget)

        self.form1_layout.addRow(self.from_form, self.to_form)

        self.equipo_widget.textChanged.connect(lambda: self.getChanges('Equipo'))
        self.nombre_widget.textChanged.connect(lambda: self.getChanges('Nombre'))
        self.institucion_widget.textChanged.connect(lambda: self.getChanges('Institución'))
        self.responsable_widget.textChanged.connect(lambda: self.getChanges('Responsable'))

        self.table = QtWidgets.QTableView()
        self.layout.addWidget(form)
        self.layout.addWidget(self.table)

        model = PandasModel(REGISTRO_DATAFRAME)
        self.table.setModel(model)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        font = QtGui.QFont("Courier New", 8)
        self.table.setFont(font)

        self.resize(800, 600)

    def getChanges(self, source):
        global REGISTRO_DATAFRAME

        bools = np.ones(REGISTRO_DATAFRAME.shape[0], dtype = bool)

        for i in range(len(self.WIDGETS)):
            source = self.FIELDS[i]
            widget = self.WIDGETS[i]
            value = eval("self.%s_widget"%widget).text()
            if value != "":
                pos = REGISTRO_DATAFRAME[source].str.contains(value, case = False, na = False)
                bools *= pos

        old = self.table.model()._data

        df = REGISTRO_DATAFRAME[bools]
        if not old.equals(df):
            self.table.setModel(PandasModel(df))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.setWindowTitle("Centro de Microscopía")

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)

        self.layout = QtWidgets.QHBoxLayout(wid)

        self.cotizacion_widget = QtWidgets.QPushButton("Generar/Modificar Cotización")
        self.descontar_widget = QtWidgets.QPushButton("Descontar")
        self.buscar_widget = QtWidgets.QPushButton("Buscar")

        self.layout.addWidget(self.cotizacion_widget)
        self.layout.addWidget(self.descontar_widget)
        self.layout.addWidget(self.buscar_widget)

        self.cotizacion_widget.clicked.connect(self.cotizacionHandler)
        self.descontar_widget.clicked.connect(self.descontarHandler)
        self.buscar_widget.clicked.connect(self.buscarHandler)

        self.cotizacion_window = CotizacionWindow()
        self.descontar_window = DescontarWindow()
        self.buscar_window = BuscarWindow()

        self.centerOnScreen()

        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.updateDataFrames)
        self.update_timer.start()

    def updateDataFrames(self):
        global CLIENTES_DATAFRAME, REGISTRO_DATAFRAME
        cli, reg = readDataFrames()
        if (not cli.equals(CLIENTES_DATAFRAME)) | (not reg.equals(REGISTRO_DATAFRAME)):
            CLIENTES_DATAFRAME = cli
            REGISTRO_DATAFRAME = reg
            self.cotizacion_window.updateCotizacionNumber()
            self.descontar_window.updateDataFrames()

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def cotizacionHandler(self):
        self.cotizacion_window.show()

    def descontarHandler(self):
        self.descontar_window.show()

    def buscarHandler(self):
        self.buscar_window.show()
