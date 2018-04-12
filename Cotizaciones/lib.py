import os
from datetime import datetime

from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import constants
from config import CODIGO_UNIANDES, CODIGO_GESTION, VALIDO_HASTA, TERMINOS_Y_CONDICIONES, DEPENDENCIAS

class Cotizacion():
    def __init__(self, nombre, correo = None, telefono = None, institucion = None,
            documento = None, direccion = None, ciudad = None, interno = False,
            responsable = None, proyecto = None, codigo = None, muestra = None,
            codigos = None, cantidades = None):

        if ".py" in nombre:
            file = os.path.basename(os.path.normpath(nombre))
            self.id = file.split(".")[0]
            self.readFromFile(nombre)

        else:
            self.nombre = nombre
            self.correo = correo
            self.telefono = telefono
            self.institucion = institucion
            self.documento = documento
            self.direccion = direccion
            self.ciudad = ciudad
            self.interno = interno
            self.responsable = responsable
            self.proyecto = proyecto
            self.codigo = codigo
            self.muestra = muestra
            self.codigos = codigos
            self.cantidades = cantidades

    def readFromFile(self, nombre):
        with open(nombre) as file:
            for line in file:
                exec("self.%s"%line)

    def getItemTable(self):
        try:
            self.codigos
        except:
            return None

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

class PDFFile():
    def __init__(self, cotizacion):

        name = cotizacion.id + ".pdf"
        name = os.path.join(constants.PDF_DIR, name)
        doc = SimpleDocTemplate(name, pagesize = letter,
                                rightMargin = cm, leftMargin = cm,
                                topMargin = cm, bottomMargin = cm)
        #Two Columns
        h = 4*cm
        frame1 = Frame(doc.leftMargin, doc.bottomMargin + doc.height - h, doc.width / 2 - 6, h, id='col1')
        frame2 = Frame(doc.leftMargin + doc.width / 2 + 2*cm, doc.bottomMargin + doc.height - h, doc.width / 2 - 6, h, id='col2')

        space = 0.5*cm
        info_h = 4*cm
        table_h = 7*cm
        observaciones_h = 3*cm
        terminos_h = 2.5*cm

        last_h = doc.bottomMargin + doc.height - h
        info_frame = Frame(doc.leftMargin, last_h - info_h - space, doc.width, info_h, showBoundary = 1)
        last_h += - info_h - space
        table_frame = Frame(doc.leftMargin, last_h - table_h - space, doc.width, table_h)
        last_h += - table_h - space
        observaciones_frame = Frame(doc.leftMargin, last_h - observaciones_h - space, doc.width, observaciones_h, showBoundary = 1)
        last_h += - observaciones_h - space
        terminos_frame = Frame(doc.leftMargin, last_h - terminos_h - space, doc.width, terminos_h, showBoundary = 1)
        last_h += - terminos_h - space
        end_frame = Frame(doc.leftMargin, last_h - 3*cm - space, doc.width, 3*cm)

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
        fecha = datetime.strftime(datetime.now(), "%d/%m/%Y")

        data = [["COTIZACIÓN N°", "FECHA"], [numero, fecha], [numero, "VALIDA HASTA"], [numero, VALIDO_HASTA]]

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


        doc.addPageTemplates([PageTemplate(id='TwoCol',frames=[frame1, frame2, info_frame, table_frame, observaciones_frame, terminos_frame, end_frame]), ])

        doc.build(Story)
