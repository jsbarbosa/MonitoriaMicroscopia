import os
import codecs
import datetime
import numpy as np
import pandas as pd
from unidecode import unidecode
from PyQt5 import QtCore, QtGui, QtWidgets

import lib
import config
import constants

CLIENTES_DATAFRAME = pd.read_excel(constants.CLIENTES_FILE)
REGISTRO_DATAFRAME = pd.read_excel(constants.REGISTRO_FILE)


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

        self.readOnly()

        self.cellChanged.connect(self.handler)

    def handler(self, row, col):
        item = self.item(row, col)
        if col == 0:
            equipo = eval("constants.%s"%self.parent.equipo_widget.currentText())
            interno = self.parent.interno_widget.checkState()

            val = "Externo"
            if interno: val = "Interno"

            try:
                cod = int(str(int(item.text()))[-1])
            except:
                cod = -1

            line = equipo[equipo["Código"] == cod]
            if line.shape[0] == 1:
                d = line["Descripción"].values[0]
                val = line[val].values[0]

                self.item(row, 1).setText(d)
                self.item(row, 3).setText("{:,}".format(val))

                try:
                    n = int(self.item(row, 2).text().replace(",", ""))
                except:
                    n = 1

                self.item(row, 4).setText("{:,}".format(val * n))

        if col == 2:
            try:
                val = int(self.item(row, 3).text().replace(",", ""))
                n = int(self.item(row, 2).text().replace(",", ""))
            except:
                val = 0
                n = 1

            self.item(row, 4).setText("{:,}".format(val * n))

        total = self.getTotal()
        self.parent.total_widget.setText(total)

    def getTotal(self):
        total = 0
        for i in range(self.n_rows):
            text = self.item(i, 4).text().replace(",", "")
            try:
                val = int(text)
            except:
                val = 0
            total += val
        return "{:,}".format(total)

    def setCodigos(self, codigos):
        for i in range(len(codigos)):
            self.item(i, 0).setText(codigos[i])

    def setCantidades(self, cantidades):
        for i in range(len(cantidades)):
            self.item(i, 2).setText(cantidades[i])

    def getCodigos(self):
        return [self.item(i, 0).text() for i in range(self.n_rows)]

    def getCantidades(self):
        return [self.item(i, 2).text() for i in range(self.n_rows)]

    def updateInterno(self):
        for i in range(self.n_rows):
            self.handler(i, 0)

    def clean(self):
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                item = QtWidgets.QTableWidgetItem("")
                self.setItem(r, c, item)
        self.readOnly()

    def readOnly(self):
        flags = QtCore.Qt.ItemIsEditable
        for r in range(self.n_rows):
            for c in [1, 3, 4]:
                item = QtWidgets.QTableWidgetItem("")
                item.setFlags(flags)
                self.setItem(r, c, item)

class AutoLineEdit(QtWidgets.QLineEdit):
    AUTOCOMPLETE = ["Nombre", "Correo", "Documento", "Teléfono", "Cotización"]
    def __init__(self, target, parent):
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

        self.textChanged.connect(self.change)

    def change(self, value):
        if type(self.parent) is MainWindow:
            dataframe = CLIENTES_DATAFRAME
            range_ = len(self.parent.FIELDS) -3
        elif type(self.parent) is ChangeCotizacion:
            dataframe = REGISTRO_DATAFRAME
            range_ = len(self.parent.FIELDS)

        try:
            df = dataframe.loc[dataframe[self.target] == value]
            rows = df.shape[0]
        except TypeError as e:
            rows = 0
            print(e)

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
        if type(self.parent) is MainWindow:
            dataframe = CLIENTES_DATAFRAME
            order = 1
        elif type(self.parent) is ChangeCotizacion:
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


class MainWindow(QtWidgets.QMainWindow):
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
        self.guardar_button = QtWidgets.QPushButton("Guardar")
        self.limpiar_button = QtWidgets.QPushButton("Limpiar")
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

        self.numero_cotizacion.clicked.connect(self.changeCotizacion)
        self.equipo_widget.currentIndexChanged.connect(self.changeEquipo)

        self.changeEquipo(0)

        self.centerOnScreen()

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
        except FileNotFoundError as e:
            self.errorWindow(e)

    def changeEquipo(self, index):
        year = str(datetime.datetime.now().year)[-2:]
        last = self.getLastCotizacion()
        equipo = self.equipo_widget.currentText()[0]
        self.numero_cotizacion.setText("%s%s-%04d"%(equipo, year, last + 1))
        self.table.clean()

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
        cotizacion = lib.Cotizacion(cotizacion)
        lib.PDFFile(cotizacion)

    def guardar(self):
        global CLIENTES_DATAFRAME, REGISTRO_DATAFRAME
        try:
            fields = self.getFields()
            last = CLIENTES_DATAFRAME.shape[0]

            fields2 = fields[:4] + fields[7:]


            fecha = datetime.datetime.now()
            equipo = self.equipo_widget.currentText()
            valor = int(self.total_widget.text().replace(",", ""))

            codigos = self.table.getCodigos()

            if all(item == "" for item in codigos):
                raise(Exception("Ningún servicio ha sido cotizado."))

            codigos = str(codigos)
            cantidades = str(self.table.getCantidades())

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
                        datetime_format= "dd/mm/yy hh:mm:ss")

            REGISTRO_DATAFRAME.to_excel(writer, index = False)

            txt = []
            for i in range(len(fields)):
                txt.append("%s = '%s'"%(self.WIDGETS[i], fields[i]))
            txt.append("equipo = '%s'"%self.equipo_widget.currentText())
            txt.append("codigos = %s"%codigos)
            txt.append("cantidades = %s"%cantidades)

            txt = "\n".join(txt)

            filename = os.path.join(constants.OLD_DIR, last + ".py")
            with open(filename, "w") as file:
                file.write(txt)

            self.generatePDF(filename)

            self.nombre_widget.update()
            self.limpiar()

        except Exception as e:
            self.errorWindow(e)

        self.changeEquipo(0)

    def limpiar(self):
        for item in self.WIDGETS:
            if item != "interno":
                eval('self.%s_widget.setText("")'%item)
            else:
                self.interno_widget.setChecked(2)
        self.table.clean()

    def errorWindow(self, exception):
        error_text = str(exception)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(error_text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.exec_()

    def internoHandler(self, state):
        if state == 2:
            self.responsable_widget.setEnabled(True)
        else:
            self.responsable_widget.setEnabled(False)
            self.responsable_widget.setText("")

        self.table.updateInterno()
