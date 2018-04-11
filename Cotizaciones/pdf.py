import time

from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

file_name = "Test.pdf"

doc = SimpleDocTemplate(file_name, pagesize = letter,
                        rightMargin = cm, leftMargin = cm,
                        topMargin = 72, bottomMargin = 18)
#Two Columns
h = 4*cm
frame1 = Frame(doc.leftMargin, doc.bottomMargin + doc.height - h, doc.width / 2 - 6, h, id='col1')
frame2 = Frame(doc.leftMargin + doc.width / 2 + 2*cm, doc.bottomMargin + doc.height - h, doc.width / 2 - 6, h, id='col2')

h2 = 5*cm
frame3 = Frame(doc.leftMargin, doc.bottomMargin + doc.height - h - h2, doc.width, h2, id='frame3', showBoundary = 1)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name = 'Center', alignment = TA_CENTER))
styles.add(ParagraphStyle(name = 'Justify', alignment = TA_JUSTIFY))

Story = []

height = 1.5

logo = Image("logo.png", height*3*cm, height*cm, hAlign = "CENTER")

Story.append(logo)
Story.append(Spacer(0, 12))
data = [["CÓDIGO UNIANDES", "CÓDIGO S.GESTIÓN"], ["", "UA-FM-CM-001"]]
t = Table(data, 90, 20)
t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ('FONTSIZE', (0, 0), (1, 1), 8),
                       ]))

Story.append(t)
Story.append(FrameBreak())

ptext = '<font size = 12><b>%s</b></font>' % "COTIZACIÓN DE SERVICIOS"
Story.append(Paragraph(ptext, styles["Normal"]))

numero = "B18-85"
fecha = "06/04/2018"
valid = "21/05/2018"

data = [["COTIZACIÓN N", "FECHA"], [numero, fecha], [numero, "VALIDA HASTA"], [numero, valid]]

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

Story.append(FrameBreak())

ptext = '<font size = 12><b>%s</b></font>' % "CENTRO DE MICROSCOPÍA - UNIVERSIDAD DE LOS ANDES"
Story.append(Paragraph(ptext, styles["Center"]))

Story.append(Spacer(1, 12))

user_name = "Juan Barbosa"

ptext = '<font size = 10>'
ptext += "<b>%s</b>" % "Nombre:"
ptext += "&nbsp <u>%s</u>" % user_name
ptext += "&nbsp &nbsp <b>%s</b>" % "Institución:"
ptext += "&nbsp <u>%s</u>" % "POASQE"
ptext += '</font>'

Story.append(Paragraph(ptext, styles["Justify"]))








doc.addPageTemplates([PageTemplate(id='TwoCol',frames=[frame1, frame2, frame3]), ])

doc.build(Story)
