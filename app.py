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
            'width': '95%',
            'height': '60px',
            'lineHeight': '60px',
            'borderStyle': 'dashed',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '10px',
            'padding': '20px 20px'
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
    r.set(session_id, decoded)

    try:
        if 'csv' in filename:
            file = io.StringIO(decoded.decode('utf-8-sig'))
            column_names = file.readline().strip().split(',')
            column_options = [{'label': i, 'value': i} for i in column_names]
    except Exception as e:
        return html.Div([
            'file not supported'
        ])
    
    return html.Div([
        html.H4('identify location indicators:'), 
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        dcc.Dropdown(
            id='hnum',
            options=column_options,
            multi=False,
            placeholder="Select house number"), 

        dcc.Dropdown(
            id='sname',
            options=column_options,
            multi=False,
            placeholder="Select street name"), 

        dcc.Dropdown(
            id='boro',
            options=column_options,
            multi=False,
            placeholder="Select borough"),
        
        html.Button('Generate Preview', id='preview'),
        html.Div(id='output-preview'),

    ])


    # DATA = []
    # for i in df.to_dict('records'):
    #     results = geocode(i['house_number'],i['street_name'],
    #                     i['borough_code'], mode='api', columns=opt)
    #     DATA.append(results)
    # r.set(session_id, json.dumps(DATA))

    # return html.Div([
    #     html.Div(session_id, id='session-id', style={'display': 'none'}),
    #     html.H5(f'File name: {filename}'),
    #     html.H6(f'Last edit: {datetime.datetime.fromtimestamp(date)}'),

    #     dash_table.DataTable(
    #         data=df.to_dict('record'),
    #         columns=[{'name': i, 'id': i} for i in opt],
    #         style_table={'overflowX': 'scroll',
    #                      'maxHeight': '300px',
    #                      'overflowY': 'scroll',
    #                      'border': 'thin lightgrey solid'},
    #         editable=True,
    #         n_fixed_rows=1,
    #     ),

    #     html.Hr(),  # horizontal line

    #     html.Div(children=[
    #             html.A(id = 'download-link', children=[
    #                     html.Button('Download',
    #                         id='submit',
    #                         type='submit',
    #                         className='button-primary')
    #                     ])
    #             ], style={'padding': '20px 20px 20px 20px'}),

    #     html.Hr(),
    #     # For debugging, display the raw contents provided by the web browser
    #     html.Div('Raw Content'),
    #     html.Pre(contents[0:200] + '...', style={
    #         'whiteSpace': 'pre-wrap',
    #         'wordBreak': 'break-all'
    #     })
    # ])
@app.callback(Output('output-preview', 'children'),
              [Input('preview', 'n_clicks')],
              [State('select', 'value'),
              State('hnum', 'value'),
              State('sname', 'value'),
              State('boro', 'value'),
              State('session-id', 'children')])
def generate_preview(nclicks, opt, hnum, sname, boro, session_id):
    decoded = r.get(session_id)
    file = io.StringIO(decoded.decode('utf-8-sig'))
    df = pd.read_csv(file, nrows=5)
    if nclicks:
        DATA = []
        for i in df.to_dict('records'):
            results = geocode(i[hnum],i[sname],
                            i[boro], mode='api', columns=opt)
            DATA.append(results)
        return html.Div([
            dash_table.DataTable(
                data=DATA,
                columns=[{'name': i, 'id': i} for i in opt],
                style_table={'overflowX': 'scroll',
                            'maxHeight': '300px',
                            'overflowY': 'scroll',
                            'border': 'thin lightgrey solid'},
                editable=True,
                n_fixed_rows=1,
            ), 
            html.A(
                id = 'download-link', children = [ 
                html.Button(
                    'Geocode All and Download',
                    id='submit',
                    type='submit',
                    className='button-primary')
                ])
        ])
    else: pass

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
    [Input('submit', 'n_clicks')], 
    [State('select', 'value'),
    State('hnum', 'value'),
    State('sname', 'value'),
    State('boro', 'value'),
    State('session-id', 'children')])
def generate_download_link(nclicks, opt, hnum, sname, boro, session_id):
    if nclicks:
        return f'/download.csv?opt={opt}&hnum={hnum}&sname={sname}&boro={boro}&session_id={session_id}'

@server.route('/download.csv')
def download_csv():
    opt = request.args.getlist('opt')
    if type(opt) == list:
        print('yes')
    else: print('no')
    hnum = request.args.get('hnum')
    sname = request.args.get('sname')
    boro = request.args.get('boro')
    session_id = request.args.get('session_id')
    decoded = r.get(session_id)
    file = io.StringIO(decoded.decode('utf-8-sig'))
    df = pd.read_csv(file)
    DATA = []
    # for i in df.to_dict('records'):
    #     results = geocode(i[hnum],i[sname],
    #                     i[boro], mode='api', columns=opt)
    #     DATA.append(results)
    # def generate():
    #     i = 0
    #     for row in DATA:
    #         if i == 0:
    #             yield ','.join(str(i) for i in row.keys()) + '\n'
    #             i += 1
    #         yield ','.join(str(x) for x in row.values()) + '\n'
    # return Response(generate(), mimetype = 'text/csv')

if __name__ == '__main__':
    app.run_server(debug=True)
