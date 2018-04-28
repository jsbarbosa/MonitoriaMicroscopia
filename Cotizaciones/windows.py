import sys
import config
from PyQt5 import QtCore, QtWidgets, QtGui

from objects import *

class Table(QtWidgets.QTableWidget):
    HEADER = ['Código', 'Descripción', 'Cantidad', 'Valor Unitario', 'Valor Total']
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

    def removeServicio(self):
        table_codigos = self.getCodigos()
        regis_codigos = self.parent.getCodigos()
        for (i, codigo) in enumerate(regis_codigos):
            if not codigo in table_codigos: self.parent.removeServicio(i)

    def handler(self, row, col):
        self.blockSignals(True)
        item = self.item(row, col)
        try:
            cod = self.item(row, 0).text()
            if col == 0:
                self.removeServicio()
                if cod == "":
                    self.item(row, 1).setText("")
                    self.item(row, 2).setText("")
                    self.item(row, 3).setText("")
                    self.item(row, 4).setText("")

                else:
                    equipo = self.parent.equipo_widget.currentText()
                    equipo_df = eval("constants.%s"%equipo)
                    interno = self.parent.interno_widget.checkState()
                    if interno: interno = "Interno"
                    else: interno = "Externo"

                    try: n = round(float(self.item(row, 2).text()), 1)
                    except: n = 1; self.item(row, 2).setText("1")

                    try:
                        servicio = Servicio(equipo = equipo, codigo = cod, interno = interno, cantidad = n)
                        self.parent.addServicio(servicio)
                    except:
                        self.item(row, 0).setText("")
                        self.item(row, 1).setText("")
                        self.item(row, 2).setText("")
                        self.item(row, 3).setText("")
                        self.item(row, 4).setText("")
                        raise(Exception("Código inválido."))

                    desc = servicio.getDescripcion()
                    valor = servicio.getValorUnitario()
                    total = servicio.getValorTotal()

                    self.item(row, 1).setText(desc)
                    self.item(row, 3).setText("{:,}".format(valor))
                    self.item(row, 4).setText("{:,}".format(total))

            if col == 2:
                try: n = round(float(self.item(row, 2).text()), 1)
                except: raise(Exception("Cantidad inválida.")); self.item(row, 2).setText("")

                self.item(row, 2).setText("%.1f"%n)


                if cod != "":
                    servicio = self.parent.getServicio(cod)
                    servicio.setCantidad(n)
                    total = servicio.getValorTotal()

                    self.item(row, 4).setText("{:,}".format(total))

            if col == 4:
                try: total = int(self.item(row, 4).text())
                except: raise(Exception("Valor total inválido.")); self.item(row, 4).setText("")

                self.item(row, 4).setText("{:,}".format(total))

                if cod != "":
                    servicio = self.parent.getServicio(cod)
                    n = total / servicio.getValorUnitario()

                    n = np.ceil(10 * n) / 10

                    servicio.setCantidad(n)
                    servicio.setValorTotal(total)

                    self.item(row, 2).setText("%.1f"%n)

            self.parent.setTotal()
        except Exception as e:
            self.parent.errorWindow(e)
        self.blockSignals(False)

    def setFromCotizacion(self):
        self.parent.getServicios()

    def getCodigos(self):
        return [self.item(i, 0).text() for i in range(self.n_rows)]

    def clean(self):
        self.blockSignals(True)
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                item = QtWidgets.QTableWidgetItem("")
                self.setItem(r, c, item)
        self.readOnly()
        self.blockSignals(False)

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

class CotizacionWindow(QtWidgets.QMainWindow):
    IGNORE = ["Proyecto", "Código"]
    FIELDS = ["Nombre", "Correo", "Teléfono", "Institución", "Documento", "Dirección", "Ciudad", "Interno", "Responsable", "Proyecto", "Código", "Muestra"]
    WIDGETS = ["nombre", "correo", "telefono", "institucion", "documento", "direccion", "ciudad", "interno", "responsable", "proyecto", "codigo", "muestra"]

    REGISTRO_FIELDS = ["Cotización", "Fecha", "Nombre", "Correo", "Teléfono", "Institución", "Interno", "Responsable", "Muestra", "Equipo", "Valor"]

    AUTOCOMPLETE_FIELDS = ["Nombre", "Correo", "Documento", "Teléfono"]
    AUTOCOMPLETE_WIDGETS = ["nombre", "correo", "documento", "telefono"]
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

        self.setAutoCompletar()

        self.interno_widget.stateChanged.connect(self.changeInterno)
        self.limpiar_button.clicked.connect(self.limpiar)
        self.guardar_button.clicked.connect(self.guardar)
        self.numero_cotizacion.clicked.connect(self.numeroCotizacion)

        self.interno_widget.setChecked(2)

        self.cotizacion = Cotizacion()

    def setAutoCompletar(self):
        for item in self.AUTOCOMPLETE_WIDGETS:
            exec("self.%s_widget.textChanged.connect(self.autoCompletar)"%item)

    def autoCompletar(self, text):
        global CLIENTES_DATAFRAME

        df = CLIENTES_DATAFRAME[self.AUTOCOMPLETE_FIELDS]
        booleans = df.isin([text]).values.sum(axis = 1)
        pos = np.where(booleans)[0]
        cliente = CLIENTES_DATAFRAME.iloc[pos]

        if len(pos):
            for (field, widgetT) in zip(self.FIELDS, self.WIDGETS):
                if field in CLIENTES_DATAFRAME.keys():
                    val = str(cliente[field].values[0])
                    if val == "nan": val = ""
                    widget = eval("self.%s_widget"%widgetT)

                    if field == "Interno":
                        if val == "Interno": widget.setCheckState(2)
                        else: widget.setCheckState(0)
                    else:
                        widget.blockSignals(True)
                        widget.setText(val)
                        widget.blockSignals(False)

    def changeInterno(self, state):
        state = bool(state)
        self.responsable_widget.setEnabled(state)
        self.proyecto_widget.setEnabled(state)
        self.codigo_widget.setEnabled(state)

    def limpiar(self):
        self.table.clean()
        for widget in self.WIDGETS:
            widget = eval("self.%s_widget"%widget)
            widget.setText("")
        self.interno_widget.setCheckState(2)

    def guardar(self):
        dic = {}
        for key in self.WIDGETS:
            if key == "interno":
                value = self.interno_widget.isChecked()
                if value: value = "Interno"
                else: value = "Externo"
            else: value = eval("self.%s_widget.text()"%key)
            dic[key] = value
        del dic["muestra"]

        usuario = Usuario(**dic)

        print(usuario)

    def numeroCotizacion(self):
        self.table.setFromCotizacion()

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def errorWindow(self, exception):
        error_text = str(exception)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(error_text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def addServicio(self, servicio):
        self.cotizacion.addServicio(servicio)

    def getCodigos(self):
        return self.cotizacion.getCodigos()

    def getServicio(self, cod):
        return self.cotizacion.getServicio(cod)

    def getServicios(self):
        return self.cotizacion.getServicios()

    def removeServicio(self, index):
        self.cotizacion.removeServicio(index)

    def setTotal(self, total = None):
        if total == None:
            total = self.cotizacion.getTotal()
        self.total_widget.setText("{:,}".format(total))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion')) # <- Choose the style

    app.processEvents()
    main = CotizacionWindow()
    main.show()
    app.exec_()
