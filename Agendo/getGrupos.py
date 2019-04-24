import pandas as pd

df = pd.read_excel("Registro.xlsx").fillna("").astype(str)

responsables = df[['Responsable']]
responsables = responsables.drop_duplicates('Responsable', 'first')

data = responsables['Responsable'].str.lstrip(' ').str.rstrip(' ')

responsables['Responsable'] = data

responsables = responsables.sort_values("Responsable")

responsables.reset_index(inplace = True, drop = True)

responsables.to_excel("Responsables.xlsx", index = False)
