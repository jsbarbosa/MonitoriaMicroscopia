import os
import config
import pandas as pd

OLD_DIR = "Old"
PDF_DIR = "PDF"
REGISTERS_DIR = "Registers"

CLIENTES_FILE = "Clientes.xlsx"
REGISTRO_FILE = "Registro.xlsx"

CLIENTES_FILE = os.path.join(REGISTERS_DIR, CLIENTES_FILE)
REGISTRO_FILE = os.path.join(REGISTERS_DIR, REGISTRO_FILE)

for item in config.EQUIPOS:
    name = '%s.xlsx'%item
    name = os.path.join(REGISTERS_DIR, name)
    data = pd.read_excel(name).astype(str)
    exec("%s = data"%item)
