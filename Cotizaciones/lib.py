import os
import numpy as np
from datetime import datetime, timedelta

from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import constants
from config import CODIGO_UNIANDES, CODIGO_GESTION, TERMINOS_Y_CONDICIONES, DEPENDENCIAS

class Cotizacion():
    WIDGETS = ["nombre", "correo", "telefono", "institucion", "documento", "direccion", "ciudad", "interno", "responsable", "proyecto", "codigo", "muestra"]
    def __init__(self, nombre, equipo = None, codigos = None, cantidades = None, usos = None, cambios = {}):
        if ".py" in nombre:
            file = os.path.basename(os.path.normpath(nombre))
            self.id = file.split(".")[0]
            self.readFromFile(nombre)
        else:
            for i in range(len(self.WIDGETS)):
                exec("self.%s = '%s'"%(self.WIDGETS[i], nombre[i]))
            self.id = nombre[-1]
            self.equipo = equipo
            self.codigos = codigos
            self.cantidades = cantidades
            self.registro_cambios = cambios
            if (self.codigos != None) and (usos == None):
                self.usos = [""]*10
            else: self.usos = usos

    def readFromFile(self, nombre):
        with open(nombre) as file:
            for line in file:
                exec("self.%s"%line)

    def descontarTable(self):
        equipo = eval("constants.%s"%self.equipo)
        table = []
        i = 0
        for (cod, n) in zip(self.codigos, self.cantidades):
            try:
                cod = int(cod)
                line = equipo[equipo["Código"] == cod]
                value = line[self.interno].values[0]
                desc = line["Descripción"].values[0]
                left = self.usos[i]
                try: left = int(left)
                except: left = 0

                try: n = int(n)
                except: n = 1

                line = [cod, desc, n, left]
                table.append(line)
            except ValueError as e:
                pass
            i += 1
        return np.array(table)

    def getItemTable(self):
        equipo = eval("constants.%s"%self.equipo)
        table = []
        total = 0
        for (cod, n) in zip(self.codigos, self.cantidades):
            try:
                cod = int(cod)
                line = equipo[equipo["Código"] == cod]
                value = line[self.interno].values[0]
                desc = line["Descripción"].values[0]
                try: n = int(n)
                except: n = 1
                total += value * n
                line = [cod, desc, n, "{:,}".format(value), "{:,}".format(value * n)]
                table.append(line)
            except ValueError:
                pass
        if total != 0:
            return table, "{:,}".format(total)
        else:
            raise(Exception("Ningún servicio ha sido cotizado."))

    def makeRegister(self, values):
        values = np.array(values)
        w = np.where(values > 0)[0]
        if len(w) > 0:
            date = datetime.strftime(datetime.now(), "%Y/%m/%d-%H:%M:%S")
            table = self.descontarTable().astype(object)
            cods = table[:, 0]
            sub = {}
            for i in w:
                sub[cods[i]] = values[i]
                j = self.codigos.index(cods[i])
                try: before = int(self.usos[j])
                except ValueError: before = 0
                self.usos[j] = before + values[i]
            self.registro_cambios[date] = sub
        self.save()

    def getReporteLine(self, cod):
        pass

    def getReporteTable(self):
        fechas = sorted(list(self.registro_cambios.keys()))
        equipo = eval("constants.%s"%self.equipo)
        table = []
        resumen = []
        current = [0] * len(self.cantidades)
        # if len(fechas) > 0:
        for fecha in fechas:
            made = self.registro_cambios[fecha]
            cods = sorted(list(made.keys()))
            for cod in cods:
                line = equipo[equipo["Código"] == int(cod)]
                desc = line["Descripción"].values[0]
                i = self.codigos.index(cod)
                cantidades = int(self.cantidades[i])
                usos = made[cod]
                current[i] += usos
                left = cantidades - current[i]
                temp = [fecha.split("-")[0], cod, desc, cantidades, usos, left]
                table.append(temp)
        # else:
        #     fecha = datetime.strftime(datetime.now(), "%Y/%m/%d")
        #     for cod in sorted(self.codigos):
        #         if cod != "":
        #             line = equipo[equipo["Código"] == int(cod)]
        #             desc = line["Descripción"].values[0]
        #             i = self.codigos.index(cod)
        #
        #             cantidades = int(self.cantidades[i])
        #             left = cantidades - current[i]
        #             temp = [fecha, cod, desc, cantidades, 0, left]
        #             table.append(temp)
        #             dones.append(cod)

        fecha = datetime.strftime(datetime.now(), "%Y/%m/%d")
        for cod in sorted(self.codigos):
            if cod != "":
                line = equipo[equipo["Código"] == int(cod)]
                desc = line["Descripción"].values[0]
                i = self.codigos.index(cod)
                cantidades = int(self.cantidades[i])
                left = cantidades - current[i]
                temp = [desc, cantidades, left]
                resumen.append(temp)
        return table, resumen

    def save(self):
        txt = []
        for i in range(len(self.WIDGETS)):
            val = eval("self.%s"%self.WIDGETS[i])
            txt.append("%s = '%s'"%(self.WIDGETS[i], val))
        txt.append("equipo = '%s'"%self.equipo)
        txt.append("codigos = %s"%self.codigos)
        txt.append("cantidades = %s"%self.cantidades)
        txt.append("usos = %s"%self.usos)
        txt.append("registro_cambios = %s"%self.registro_cambios)

        txt = "\n".join(txt)
        filename = os.path.join(constants.OLD_DIR, self.id + ".py")
        with open(filename, "w") as file:
            file.write(txt)

class PDFCotizacion():
    def __init__(self, cotizacion):
        name = cotizacion.id + ".pdf"
        name = os.path.join(constants.PDF_DIR, name)
        self.doc = SimpleDocTemplate(name, pagesize = letter,
                                rightMargin = cm, leftMargin = cm,
                                topMargin = cm, bottomMargin = cm)
        #Two Columns
        h = 4*cm
        frame1 = Frame(self.doc.leftMargin, self.doc.bottomMargin + self.doc.height - h, self.doc.width / 2 - 6, h, id='col1')
        frame2 = Frame(self.doc.leftMargin + self.doc.width / 2 + 2*cm, self.doc.bottomMargin + self.doc.height - h, self.doc.width / 2 - 6, h, id='col2')

        space = 0.5*cm
        info_h = 4*cm
        table_h = 7*cm
        observaciones_h = 3*cm
        terminos_h = 2.5*cm

        last_h = self.doc.bottomMargin + self.doc.height - h
        info_frame = Frame(self.doc.leftMargin, last_h - info_h - space, self.doc.width, info_h, showBoundary = 1)
        last_h += - info_h - space
        table_frame = Frame(self.doc.leftMargin, last_h - table_h - space, self.doc.width, table_h)
        last_h += - table_h - space
        observaciones_frame = Frame(self.doc.leftMargin, last_h - observaciones_h - space, self.doc.width, observaciones_h, showBoundary = 1)
        last_h += - observaciones_h - space
        terminos_frame = Frame(self.doc.leftMargin, last_h - terminos_h - space, self.doc.width, terminos_h, showBoundary = 1)
        last_h += - terminos_h - space
        end_frame = Frame(self.doc.leftMargin, last_h - 3*cm - space, self.doc.width, 3*cm)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name = 'Center', alignment = TA_CENTER))
        styles.add(ParagraphStyle(name = 'Justify', alignment = TA_JUSTIFY))

        Story = []

        height = 1.5

        logo = Image("logo.png", height*3.33*cm, height*cm, hAlign = "CENTER")

        Story.append(logo)
        Story.append(Spacer(0, 12))
        data = [["CÓDIGO UNIANDES", "CÓDIGO S.GESTIÓN"], [CODIGO_UNIANDES, CODIGO_GESTION]]
        t = Table(data, 90, 20)
        t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ('FONTSIZE', (0, 0), (1, 1), 8),
                               ]))

        Story.append(t)
        Story.append(FrameBreak())

        ptext = '<font size = 12><b>%s</b></font>' % "COTIZACIÓN DE SERVICIOS"
        Story.append(Paragraph(ptext, styles["Normal"]))

        numero = cotizacion.id
        today = datetime.now()
        fecha = datetime.strftime(today, "%d/%m/%Y")
        until = datetime.strftime(today + timedelta(days = 45), "%d/%m/%Y")

        data = [["COTIZACIÓN N°", "FECHA"], [numero, fecha], [numero, "VALIDA HASTA"], [numero, until]]

        t = Table(data, 80, 15, hAlign='LEFT')
        t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ('FONTSIZE', (0, 0), (-1, -1), 8),
                               ('FONTSIZE', (0, 1), (0, 1), 12),
                               ('ALIGN', (0, 1), (0, 1), "CENTER"),
                               ('VALIGN', (0, 1), (0, 1), "MIDDLE"),
                               ('SPAN',(0,1),(0,-1)),
                               ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                               ('BACKGROUND', (1, 2), (1, 2), colors.grey)
                                ]))

        Story.append(Spacer(1, 12))
        Story.append(t)

        """
        INFO
        """
        Story.append(FrameBreak())

        ptext = '<font size = 12><b>%s</b></font>' % "CENTRO DE MICROSCOPÍA - UNIVERSIDAD DE LOS ANDES"
        Story.append(Paragraph(ptext, styles["Center"]))

        Story.append(Spacer(1, 12))

        ptext = '<font size = 10>'
        ptext += "<b>%s</b>" % "Nombre:"
        ptext += "&nbsp %s" % cotizacion.nombre

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Institución:"
        ptext += "&nbsp %s" % cotizacion.institucion

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Documento (Nit/C.C.):"
        ptext += "&nbsp %s" % cotizacion.documento
        ptext += '</font>'

        Story.append(Paragraph(ptext, styles["Justify"]))
        Story.append(Spacer(1, 6))

        ptext = '<font size = 10>'
        ptext += "<b>%s</b>" % "Teléfono:"
        ptext += "&nbsp %s" % cotizacion.telefono

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Dirección:"
        ptext += "&nbsp %s" % cotizacion.direccion

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Ciudad:"
        ptext += "&nbsp %s" % cotizacion.ciudad
        ptext += '</font>'

        Story.append(Paragraph(ptext, styles["Justify"]))

        Story.append(Spacer(1, 6))

        ptext = '<font size = 10>'
        ptext += "<b>%s</b>" % "Correo:"
        ptext += "&nbsp %s" % cotizacion.correo

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Tipo de Muestra:"
        ptext += "&nbsp %s" % cotizacion.muestra
        ptext += '</font>'

        Story.append(Paragraph(ptext, styles["Justify"]))

        """
        TABLE
        """
        table, total = cotizacion.getItemTable()
        table.insert(0, ["COD", "SERVICIO", "CANTIDAD", "PRECIO UNIDAD", "PRECIO TOTAL"])
        table.append(["", "", "", "TOTAL", total])

        Story.append(FrameBreak())

        t = Table(table, [40, 260, 70, 90, 90], 15, hAlign='CENTER')

        t.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ('ALIGN', (0, 0), (-1, 0), "CENTER"),
                               ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('ALIGN', (-3, 0), (-1, -1), "RIGHT"),
                               ('SPAN',(0, -1),(-3, -1)),
                                ]))
        Story.append(t)

        """
        OBSERVACIONES
        """
        Story.append(FrameBreak())
        text = "OBSERVACIONES"
        ptext = '<font size = 10> <b> %s </b></font>'%text
        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(Spacer(1, 6))

        text = [("Responsable", cotizacion.responsable),
                ("Proyecto", cotizacion.proyecto),
                ("Código", cotizacion.codigo)]

        if cotizacion.interno == "Interno":
            for item in text:
                ptext = '<font size = 9> <b>%s:</b> <u>%s</u></font>'%item
                Story.append(Paragraph(ptext, styles["Normal"]))

        """
        TERMINOS Y CONDICIONES
        """
        Story.append(FrameBreak())

        text = "TÉRMINOS Y CONDICIONES"
        ptext = '<font size = 10> <b> %s </b></font>'%text
        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(Spacer(1, 6))

        for i in range(len(TERMINOS_Y_CONDICIONES)):
            text = TERMINOS_Y_CONDICIONES[i]
            ptext = '<font size = 8>%d. %s</font>'%(i + 1, text)
            Story.append(Paragraph(ptext, styles["Normal"]))

        """
        END
        """
        Story.append(FrameBreak())

        for i in range(len(DEPENDENCIAS)):
            text = DEPENDENCIAS[i]
            if i < 2:
                ptext = '<font size = 10> <b> %s </b></font>'%text
            else:
                ptext = '<font size = 10>%s</font>'%text
            Story.append(Paragraph(ptext, styles["Center"]))

        self.doc.addPageTemplates([PageTemplate(frames=[frame1, frame2, info_frame, table_frame, observaciones_frame, terminos_frame, end_frame], onPage = self.drawPage), ])
        self.doc.build(Story)

    def drawPage(self, canvas, doc):
        canvas.setTitle("Centro de Microscopía")
        canvas.setSubject("Cotización")
        canvas.setAuthor("Juan Barbosa")
        canvas.setCreator("MicroBill")
        styles = getSampleStyleSheet()

        P = Paragraph("<font size = 8>Creado usando MicroBill - Juan Barbosa (github.com/jsbarbosa)</font>",
                  styles["Normal"])
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)

class PDFReporte():
    def __init__(self, cotizacion):
        name = cotizacion.id + "_Reporte.pdf"
        name = os.path.join(constants.PDF_DIR, name)
        self.doc = SimpleDocTemplate(name, pagesize = letter,
                                rightMargin = cm, leftMargin = cm,
                                topMargin = cm, bottomMargin = cm)

        table, resumen = cotizacion.getReporteTable()
        resumen.insert(0, ["DESCRIPCIÓN", "COTIZADOS", "RESTANTES"])
        table.insert(0, ["FECHA", "COD", "DESCRIPCIÓN", "COTIZADOS", "USADOS", "RESTANTES"])

        #Two Columns
        h = 3*cm
        frame1 = Frame(self.doc.leftMargin, self.doc.bottomMargin + self.doc.height - h, self.doc.width / 2 - 6, h, id='col1')
        frame2 = Frame(self.doc.leftMargin + self.doc.width / 2 + 2*cm, self.doc.bottomMargin + self.doc.height - h, self.doc.width / 2 - 6, h, id='col2')

        space = 0.5*cm
        info_h = 4*cm
        table_h = (len(table) + 1)*15
        observaciones_h = (len(resumen) + 2)*15
        terminos_h = 2.5*cm

        last_h = self.doc.bottomMargin + self.doc.height - h
        info_frame = Frame(self.doc.leftMargin, last_h - info_h - space, self.doc.width, info_h, showBoundary = 1)
        last_h += -info_h - space

        table_frame = Frame(self.doc.leftMargin, self.doc.bottomMargin, self.doc.width, last_h - cm)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name = 'Center', alignment = TA_CENTER))
        styles.add(ParagraphStyle(name = 'Justify', alignment = TA_JUSTIFY))

        Story = []

        height = 1.5
        logo = Image("logo.png", height*3.33*cm, height*cm, hAlign = "CENTER")

        Story.append(logo)
        Story.append(FrameBreak())

        ptext = '<font size = 12><b>%s</b></font>' % "REPORTE DE SERVICIOS"
        Story.append(Paragraph(ptext, styles["Normal"]))

        numero = cotizacion.id
        today = datetime.now()
        fecha = datetime.strftime(today, "%d/%m/%Y")

        data = [["COTIZACIÓN N°", "FECHA"], [numero, fecha]]

        t = Table(data, 80, 20, hAlign='LEFT')
        t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ('FONTSIZE', (0, 0), (-1, -1), 10),
                               ('FONTSIZE', (0, 1), (0, 1), 12),
                               ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                               ('VALIGN', (0, 0), (-1, -1), "MIDDLE"),
                               ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                               ('BACKGROUND', (1, 2), (1, 2), colors.grey)
                                ]))

        Story.append(Spacer(1, 12))
        Story.append(t)

        """
        INFO
        """
        Story.append(FrameBreak())

        ptext = '<font size = 12><b>%s</b></font>' % "CENTRO DE MICROSCOPÍA - UNIVERSIDAD DE LOS ANDES"
        Story.append(Paragraph(ptext, styles["Center"]))

        Story.append(Spacer(1, 12))

        ptext = '<font size = 10>'
        ptext += "<b>%s</b>" % "Nombre:"
        ptext += "&nbsp %s" % cotizacion.nombre

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Institución:"
        ptext += "&nbsp %s" % cotizacion.institucion

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Documento (Nit/C.C.):"
        ptext += "&nbsp %s" % cotizacion.documento
        ptext += '</font>'

        Story.append(Paragraph(ptext, styles["Justify"]))
        Story.append(Spacer(1, 6))

        ptext = '<font size = 10>'
        ptext += "<b>%s</b>" % "Teléfono:"
        ptext += "&nbsp %s" % cotizacion.telefono

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Dirección:"
        ptext += "&nbsp %s" % cotizacion.direccion

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Ciudad:"
        ptext += "&nbsp %s" % cotizacion.ciudad
        ptext += '</font>'

        Story.append(Paragraph(ptext, styles["Justify"]))

        Story.append(Spacer(1, 6))

        ptext = '<font size = 10>'
        ptext += "<b>%s</b>" % "Correo:"
        ptext += "&nbsp %s" % cotizacion.correo

        ptext += "&nbsp &nbsp &nbsp &nbsp <b>%s</b>" % "Tipo de Muestra:"
        ptext += "&nbsp %s" % cotizacion.muestra
        ptext += '</font>'

        Story.append(Paragraph(ptext, styles["Justify"]))

        """
        TABLE
        """
        Story.append(FrameBreak())
        t = Table(table, [70, 40, 200, 80, 80, 80], 15, hAlign='CENTER')

        t.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ('ALIGN', (0, 0), (-1, 0), "CENTER"),
                               ('ALIGN', (3, 0), (-1, -1), "CENTER"),
                               ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('ALIGN', (-3, 1), (-1, -1), "RIGHT"),
                                ]))
        Story.append(t)
        Story.append(Spacer(0, cm))

        """
        RESUMEN
        """
        # Story.append(FrameBreak())
        text = "RESUMEN"
        ptext = '<font size = 10> <b> %s </b></font>'%text
        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(Spacer(1, 6))


        t = Table(resumen, [200, 80, 80], 15, hAlign='CENTER')

        t.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ('ALIGN', (0, 0), (-1, 0), "CENTER"),
                               ('ALIGN', (0, 1), (0, -1), "LEFT"),
                               ('ALIGN', (-2, 1), (-1, -1), "RIGHT"),
                               ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ]))

        Story.append(t)
        Story.append(Spacer(0, cm))

        """
        END
        """
        for i in range(len(DEPENDENCIAS)):
            text = DEPENDENCIAS[i]
            if i < 2:
                ptext = '<font size = 10> <b> %s </b></font>'%text
            else:
                ptext = '<font size = 10>%s</font>'%text
            Story.append(Paragraph(ptext, styles["Center"]))

        self.doc.addPageTemplates([PageTemplate(frames = [frame1, frame2, info_frame, table_frame], onPage = self.drawPage), ])

        self.doc.build(Story)

    def drawPage(self, canvas, doc):
        canvas.setTitle("Centro de Microscopía")
        canvas.setSubject("Reporte")
        canvas.setAuthor("Juan Barbosa")
        canvas.setCreator("MicroBill")
        styles = getSampleStyleSheet()

        P = Paragraph("<font size = 8>Creado usando MicroBill - Juan Barbosa (github.com/jsbarbosa)</font>",
                  styles["Normal"])
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
