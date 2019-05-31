import base64
import datetime
import io

from geocode import geocode
from spatial_options import spatial_options

import json
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import redis
import uuid
from flask import Flask, request, Response
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.supress_callback_exceptions = True
r = redis.StrictRedis(host='localhost', port=6379, db=0)

app.layout = html.Div([

    html.H1('Baiyue\'s fun geocoder! yay!!!'),
    html.Hr(),
    html.H2('select your features here:'),

    dcc.Dropdown(
        id='select',
        options=spatial_options,
        multi=True,
        value=['First Borough Name', 'First Street Name Normalized', 'House Number - Display Format']),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderStyle': 'dashed',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '10px',
            'padding': '10px 20px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])

def parse_contents(contents, opt, filename, date):
    r.flushdb()
    session_id = str(uuid.uuid4())

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df_sample = df[0:5]
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        return html.Div([
            'There was an error processing this file.'
        ])

    DATA = []
    for i in df.to_dict('records'):
        results = geocode(i['house_number'],i['street_name'],
                        i['borough_code'], mode='api', columns=opt)
        DATA.append(results)
    r.set(session_id, json.dumps(DATA))

    return html.Div([
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        html.H5(f'File name: {filename}'),
        html.H6(f'Last edit: {datetime.datetime.fromtimestamp(date)}'),

        dash_table.DataTable(
            data=DATA[0:5],
            columns=[{'name': i, 'id': i} for i in opt],
            style_table={'overflowX': 'scroll',
                         'maxHeight': '300px',
                         'overflowY': 'scroll',
                         'border': 'thin lightgrey solid'},
            editable=True,
            n_fixed_rows=1,
        ),

        html.Hr(),  # horizontal line

        html.Div(children=[
                html.A(id = 'download-link', children=[
                        html.Button('Download',
                            id='submit',
                            type='submit',
                            className='button-primary')
                        ])
                ], style={'padding': '20px 20px 20px 20px'}),

        html.Hr(),
        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('select', 'value'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified')])
def update_output(list_of_contents, opt, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, opt, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(
    Output('download-link', 'href'),
    [Input('session-id', 'children')])
def get_data(session_id):
    return f'/download.csv?session_id={session_id}'

@server.route('/download.csv')
def download_csv():
    session_id = request.args.get('session_id')
    def generate():
        i = 0
        for row in json.loads(r.get(session_id)):
            print(row)
            if i == 0:
                yield ','.join(str(i) for i in row.keys()) + '\n'
                i += 1
            yield ','.join(str(x) for x in row.values()) + '\n'
    return Response(generate(), mimetype = 'text/csv')

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True, port=8050)
