import os
from io import BytesIO
import base64
import dash
from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Configuración de la carga de archivos con Dash-Uploader
UPLOAD_DIRECTORY = "./uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

app.layout = html.Div([
    html.H1("Subir y Guardar Archivo"),
    
    # Cargar archivos
    dcc.Upload(
        id='upload-data',
        children=html.Button('Cargar Archivo'),
        multiple=False
    ),

    html.Br(),

    # Botón para guardar el archivo
    html.Button('Guardar Archivo', id='btn-guardar-archivo', n_clicks=0),

    # Mensaje de confirmación
    html.Div(id='mensaje-confirmacion')
])

# Callback para cargar y mostrar el contenido del archivo
@app.callback(
    Output('mensaje-confirmacion', 'children'),
    [Input('btn-guardar-archivo', 'n_clicks')],
    [State('upload-data', 'contents'),
     State('upload-data', 'filename')]
)
def guardar_archivo(n_clicks, contents, filename):
    if n_clicks == 0:
        raise PreventUpdate

    # Guardar el archivo en la carpeta local
    filepath = os.path.join(UPLOAD_DIRECTORY, filename)
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    with open(filepath, 'wb') as f:
        f.write(decoded)

    return f"Archivo guardado correctamente en: {filepath}"

# Ejecutar la aplicación Dash
if __name__ == '__main__':
    app.run_server(debug=True)