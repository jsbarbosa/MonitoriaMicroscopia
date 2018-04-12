import config
import pandas as pd

OLD_DIR = "Old"
PDF_DIR = "PDF"

CLIENTES_FILE = "Clientes.xlsx"
REGISTRO_FILE = "Registro.xlsx"

for item in config.EQUIPOS:
    data = pd.read_excel('%s.xlsx'%item)
    exec("%s = data"%item)
