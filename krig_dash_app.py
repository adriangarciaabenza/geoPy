import base64
import os
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from krigeado_precipitacion_app import *

UPLOAD_DIRECTORY = "./AppInput"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(server=server)

@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


app.layout = html.Div(
    [
        html.H1("File Browser"),
        html.H2("Upload"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag and drop or click to select a file to upload."]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.H2("File List"),
        html.Ul(id="file-list"),
        html.Button("Generate Report", id="btn-generate-report", n_clicks=0),
        html.Button("Delete Report", id="btn-delete-report", n_clicks=0),
        html.Button("Delete All Files", id="btn-delete-all-files", n_clicks=0),
        html.H2("Generated Report"),
        html.Div(id="output-container"),
    ],
    style={"max-width": "800px", "margin": "auto"},
)


def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    Output("file-list", "children", allow_duplicate=True),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
    prevent_initial_call='initial_duplicate',
    
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]

@app.callback(
    [Output("output-container", "children"),
    Output("file-list", "children", allow_duplicate=True)],
    [Input("btn-generate-report", "n_clicks"),
     Input("btn-delete-report", "n_clicks"),
     Input("btn-delete-all-files", "n_clicks")],
    prevent_initial_call=True,
)
def handle_buttons(n_clicks_generate, n_clicks_delete_report, n_clicks_delete_all_files):
    ctx = dash.callback_context
    if not ctx.triggered_id:
        raise dash.exceptions.PreventUpdate

    button_id = ctx.triggered_id.split(".")[0]

    if button_id == "btn-generate-report":
        files = uploaded_files()
        filename = [file for file in files if file.endswith(".csv")]
        df = kriging(filename=filename) 
        generate_table_and_animation()
        report_filepath = os.path.join(UPLOAD_DIRECTORY, 'report.html')
        df.to_html(report_filepath)
        files = uploaded_files()
        if len(files) == 0:
            return [html.Div([html.Iframe(srcDoc=open(report_filepath, 'r').read(), width='100%', height='600')]), html.Li("No files yet!")]
        else:
            return [html.Div([html.Iframe(srcDoc=open(report_filepath, 'r').read(), width='100%', height='600')]), [html.Li(file_download_link(filename)) for filename in files]]
    elif button_id == "btn-delete-report":
        delete_report()
        files = uploaded_files()
        if len(files) == 0:
            return [html.Div("Report deleted"), html.Li("No files yet!")]
        else:
            return [html.Div("Report deleted"), [html.Li(file_download_link(filename)) for filename in files]]
    elif button_id == "btn-delete-all-files":
        delete_all_files()
        files = uploaded_files()
        return [html.Div("All files deleted"), html.Li("No files yet!")]

def generate_table_and_animation():
    print("Generating table and animation...")

def delete_report():
    report_filepath = os.path.join(UPLOAD_DIRECTORY, 'report.html')
    if os.path.exists(report_filepath):
        os.remove(report_filepath)

def delete_all_files():
    for filename in os.listdir(UPLOAD_DIRECTORY):
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {filename}: {e}")



if __name__ == "__main__":
    app.run_server(debug=True)