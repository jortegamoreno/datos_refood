import pandas as pd
import numpy as np

traducciones = {
    'tipos':
        {'alimentos frescos': ['Fruta y verdura', 'Aliementos frescos', 'Alimentos Frescos3',
                               'FRUTAS Y VERDURAS', 'Alimentos frescos ', 'Frescos', 'Fruta y verdura ',
                               'verdura y fruta', 'frutas y verduras', 'alimento fresco', 'ALINMENTOS FRESCOS '],
         'comida preparada': [
             'COMIDA PREPRADA', 'Comida Preparada ',
             'Plato preparado', 'Potaje', 'macarrones con tomate', 'Preparada',
             'Otros', 'Frutas y verduras', 'Patatas en salsa',
             'Macarrones con cohrizo', 'Garbanzos con carne', 'Pollo al horno',
             'Files de lomo', 'Macarrones con chorizo', 'Pollo con patatas',
             'Croissant', 'Filetes de lomo', 'Lentejas con chorizo',
             'Macarrones con atún', 'Filetes de Lomo', 'Pescado con verduras', 'COMIDA PREPARADA '],

         'bolleria': ['Bollería', 'Bollos']},

    'donantes': {
        'D001': ['VEDRUNA'],
        'D002': ['D2', 'D02', 'AQUINAS', 'EÑE'],
        'D003': ['D3', 'D03'],
        'D004': ['D04', 'D0004', 'LEVADURA MADRE'],
        'D005': ['B005'],
        'D006': ['D06', 'VALENCIA'],
        'D011': ['Q´PASTELITOS'],
        'D012': ['D12', 'LAS GEMELAS'],
        'D013': ['D0013'],
        'D014': ['DO14', 'D014 '],
        'D019': ['D19', 'DO19', 'D019 ', 'D029'],
        'D021': ['DO21', 'D21'],
        'D024': ['D24'],
        'D025': ['D25'],
        # Hay un error, y D005 y D018 representan a Bonjour. Convertimos D005 en D008
        'D018': ['D005'],
        'OTRO': ['-', 'D020']}
}
nombres_donantes = {
    'D001': 'Vedruna',
    'D002': 'Colegio Mayor Aquinas',
    'D003': 'Funway Academic Resort',
    'D004': 'Levaduramadre',
    'D006': 'Fruteria Valencia',
    'D008': 'Eñe + que una letra',
    'D009': 'LomiRock',
    'D011': 'Q Pastelitos',
    'D012': 'Frutería Las Gemelas',
    'D013': 'El Cebón',
    'D014': 'Fruteria El Moreno',
    'D015': 'CHIPA',
    'D016': 'Tercer Tiempo Bar',
    'D017': 'Fruterias Ignacio',
    'D018': 'Bonjour',
    'D019': 'CM Loyola',
    'D021': 'Zara frutas y verdura',
    'D022': 'Casa Ramona',
    'D023': 'Fruterias Andrés',
    'D024': 'Shurma Huerta',
    'D025': 'Hoy es Mañana',
    'D026': 'Pastelería Ludavi',
    'OTRO': 'Otros'
}

pesos = {
    'comida preparada': {'kg': 0.2, 'rac': 1},
    'alimentos frescos': {'kg': 1.5, 'rac': 3},
    'pan': {'kg': 0.2, 'rac': 0.5},
    'bolleria': {'kg': 0.2, 'rac': 0.1},
    'otros': {'kg': 0.2, 'rac': 0.1}
}


def leer_y_limpiar():
    df = pd.read_csv('salidas_trazabilidad_refood_def.csv', on_bad_lines='skip', sep=";")
    df = df.drop(labels=0, axis=0)

    df['Fecha Hora'] = pd.to_datetime(df['Fecha Hora'], dayfirst=True)
    # Donantes que no tenemos el nombre
    df.drop(df[df['ID Donantes'] == 'D007'].index, inplace=True)
    df.drop(df[df['ID Donantes'] == 'D010'].index, inplace=True)
    # Traducimos erratas
    df['ID Donantes'] = df['ID Donantes'].apply(lambda x: x.upper())
    
    df = traducir_erratas(df)
	 
    df = crear_columnas_kg_rac(df)
    
    df = anadir_columna_nombres(df)

    return df


def traducir_erratas(data):
    for traduccion in traducciones:
        for key in traducciones[traduccion]:
            trad = traducciones[traduccion]
            trad = trad[key]
            for i in trad:
                data = data.replace([i], key)

    return data

def crear_columnas_kg_rac(data):
	
    data = data[data['Cantidad (un. o kg)'].apply(lambda x: x.isdecimal())]
	
    data["Cantidad (un. o kg)"] = pd.to_numeric(data["Cantidad (un. o kg)"], downcast="float")

    data['Kilos rescatados'] = np.where(data['Tipo de comida'].str.lower() == 'comida preparada',
                                      data['Cantidad (un. o kg)'] * 0.2,
                                      np.where(data['Tipo de comida'].str.lower() == 'alimentos frescos',
                                               data['Cantidad (un. o kg)'] * 1.5,
                                               np.where(data['Tipo de comida'].str.lower() == 'pan',
                                                        data['Cantidad (un. o kg)'] * 0.2, 0.0)))

    data['Raciones rescatadas'] = np.where(data['Tipo de comida'].str.lower() == 'comida preparada',
                                         data['Cantidad (un. o kg)'] * 1,
                                         np.where(data['Tipo de comida'].str.lower() == 'alimentos frescos',
                                                  data['Cantidad (un. o kg)'] * 3,
                                                  np.where(data['Tipo de comida'].str.lower() == 'pan',
                                                           data['Cantidad (un. o kg)'] * 0.5, 0.0)))
    return data

def anadir_columna_nombres(data):
    donantes = data['ID Donantes'].unique()
    data['Nombres'] = data['ID Donantes']
    for donante in donantes:
        data['Nombres'] = data['Nombres'].replace([donante], nombres_donantes[donante])
    print("Fechas en el fichero por donantes:")
    print(data.groupby('Nombres')['Fecha Hora'].agg(['min', 'max']).rename(columns={'min': 'first', 'max': 'last'}))
    
    return data
