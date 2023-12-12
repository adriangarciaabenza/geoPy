import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import io
import base64
import os
from app_auto_mapas_temperatura import calculate_grid_temperatures

# Directorio donde se guardarán los archivos subidos
UPLOAD_DIRECTORY = "./AppInput/"

# Verifica si el directorio de carga existe, y si no, créalo
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Inicializa la aplicación Dash
app = dash.Dash(__name__)

# Diseño de la aplicación
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Subir Archivo'),
        multiple=False
    ),
    html.Div(id='output-data'),
])

# Callback para procesar el archivo subido
@app.callback(
    Output('output-data', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)

        # Guarda el archivo en el directorio "input/"
        with open(file_path, 'wb') as f:
            f.write(decoded)
        
        try:
            # Lee el archivo en un DataFrame de Pandas
            df = calculate_grid_temperatures(file_path)
            
            # Aquí puedes ejecutar el código que tienes preparado con los datos del DataFrame 'df'
            # Por ejemplo, podrías realizar algún cálculo y guardar los resultados en una variable llamada 'resultados'
            # resultados = ...

            # Luego, muestra los resultados en una tabla
            table = html.Table([
                html.Tr([html.Th(col) for col in df.columns]),
                html.Tbody([
                    html.Tr([
                        html.Td(df.iloc[i][col]) for col in df.columns
                    ]) for i in range(len(df))
                ])
            ])
            return table
        except Exception as e:
            return html.Div('Hubo un error al procesar el archivo.')
    else:
        return ''

if __name__ == '__main__':
    app.run_server(host='172.24.37.8',port=8050,debug=True)