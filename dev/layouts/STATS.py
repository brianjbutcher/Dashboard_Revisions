from dash.dependencies import Input, Output, Event, State
import dash_core_components as dcc
import dash_html_components as html

import dash_table_experiments as dt
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

#init_notebook_mode(connected=True)

#import plotly.graph_objs as go
# from loremipsum import get_sentences
import plotly
import query as mongo_query

from layouts import utils
# from pprint import pprint
import os
from collections import defaultdict
import base64
import functools
import itertools
import random
import flask
import logging
import sys

_logger = logging.getLogger(__name__)

from index import app


__DUT_DB__ = 'DUT___{}___PerfStats'
__DIE_DB__ = 'DIE___{}___PerfStats'
__BLK_DB__ = 'BLK___{}___PerfStats'

__DUT_GBB_DB__ = 'DUT___{}___GBBHisto'
__DIE_GBB_DB__ = 'DIE___{}___GBBHisto'
__BLK_GBB_DB__ = 'BLK___{}___GBBHisto'

__STATS_COLUMN__ = ('max', 'avg', 'min',  )

__layout__ = '-'+__name__.split('.')[-1]

import operator
def accumulate(iterable, func=operator.add):
    'Return running totals'
    # accumulate([1,2,3,4,5]) --> 1 3 6 10 15
    # accumulate([1,2,3,4,5], operator.mul) --> 1 2 6 24 120
    it = iter(iterable)
    try:
        total = next(it)
    except StopIteration:
        return
    yield total
    for element in it:
        total = func(total, element)
        yield total

def printCSV(df, output_dir, filename):
    file = str(filename + '.csv')
    if os.path.isfile(os.path.join(output_dir, file)):
        print ("Appending..." + filename + '.csv')
        with open(os.path.join(output_dir, file), 'a') as f:
            df.to_csv(f, sep=",", index=False, header=False)
        print("\n\n")

    elif os.path.isfile(os.path.join(output_dir, file)) == False:
        print ("Creating..." + filename + '.csv')
        df.to_csv(os.path.join(output_dir, file), sep=",", index=False)
    return



#image_filename = os.path.join(os.getcwd(), 'assets','UpdatedWDCheader.PNG') # replace with your own image
#encoded_image_header = base64.b64encode(open(image_filename, 'rb').read())


#image_filename = os.path.join(os.getcwd(), 'assets','UpdatedWDCfooter.PNG') # replace with your own image
#encoded_image_footer = base64.b64encode(open(image_filename, 'rb').read())

style={
    'font-family' : '"avenir",arial',
    }

layout = [
  dcc.Input(id='toggle-normalization'+__layout__, style = {'display':'none'}, value={'dut':0, 'die':0, 'blk':0}),

  html.Div([
      html.Div([
          html.Div([
            html.Label('DUT Level Analysis', className= 'eight columns offset-by-one'),
            html.Button('Normalize plots', id='toggle-normalization-R1', className = 'two columns offset-by-one'),
          ], className = 'row panel-head theme-color-secondary'),
          html.Div(id='R1'+__layout__, className = 'row panel-body container-fluid'),
        ], className="panel row plotbar"),

      #html.Hr(),
      #html.Div(dcc.Textarea(id='texttop-input',className = 'row', style = {'width': '80%', 'margin-left': '10%'},
      #                      placeholder='Click and start typing any notes, which will be saved when you export page'), className = 'container'),
      #html.Hr(),
      html.Div([
          html.Div([
            html.Label('Die Level Analysis', className= 'two columns offset-by-one'),

              html.Div(dcc.Dropdown(id='dut-dropdown' + __layout__,
                                    placeholder="Select a DUT for Die Level Analysis"),
                       className='four columns offset-by-one'),
              html.Button('Normalize Plots', id='toggle-normalization-R2',
                          className='two columns offset-by-two'),
          ], className='row panel-head theme-color-secondary'),
        html.Div(id='R2'+__layout__, className = "row panel-body container-fluid"),

        ], className="row plotbar panel"),

      #html.Hr(),
      #html.Div(dcc.Textarea(id='texttop-input',className = 'row', style = {'width': '80%', 'margin-left': '10%'},
      #                      placeholder='Click and start typing any notes, which will be saved when you export page'), className = 'container'),
      #html.Hr(),
      html.Div([
          html.Div([
            html.Label('Block Level Analysis', className= 'two columns offset-by-one'),
            html.Div(dcc.Dropdown(id='die-dropdown'+__layout__,
                                  placeholder="Select a DIE for Block Level Analysis"),className= 'four columns offset-by-one'),
            html.Button('Normalize Plots', id='toggle-normalization-R3', className = 'two columns offset-by-two'),
        ], className = 'row panel-head theme-color-secondary'),

      html.Div(id='R3'+__layout__, className="row panel-body container-fluid"),
      ], className="panel row plotbar"),
      html.Div(id='R4'+__layout__, className="panel row plotbar"),


      html.Hr(style = {'visibility':'hidden'}),
  ], className = 'bar')

]



@app.callback(Output('dut-dropdown'+__layout__, 'options'),[
              Input('product-dropdown', 'value'),
              Input('qual-dropdown', 'value'),
              Input('test-dropdown', 'value'),
              Input('refresh-component', 'n_clicks'),
              Input('interval-component', 'n_intervals')])
def update_dropdown(product_choice, qual_choice, test_choice, manual_refresh, interval_refresh):

    try:
        # client = MongoClient(host='10.196.155.85', port=27017)
        query = {"_id": {"$regex": test_choice}}
        dbvalue = __DUT_DB__.format(product_choice)
        query_result = mongo_query.run_query(dbvalue, qual_choice, query)
        for each in query_result:
            each['_id_pair'] = dict(zip(each['_id_name'].split(','), each['_id'].split(',')))
        output = set(x['_id_pair']['dut']
                       #+ str('-')
                       #+ x.split(',')[5]
                       + str(',')
                       + x['_id_pair']['pcname']
                     for x in query_result)
        return [{'label': i, 'value': i} for i in output]
    except:
        return []


@app.callback(Output('die-dropdown'+__layout__, 'options'),[
              Input('product-dropdown', 'value'),
              Input('qual-dropdown', 'value'),
              Input('test-dropdown', 'value'),
              Input('dut-dropdown'+__layout__, 'value'),
              Input('refresh-component', 'n_clicks'),
              Input('interval-component', 'n_intervals')],)
def update_dropdown(product_choice, qual_choice, test_choice, dut_choice, manual_refresh, interval_refresh):

    try:
        query = {"$and": [ {"_id": {"$regex": test_choice}},
                           {"_id": {"$regex": dut_choice }}
                          ]
                 }
        dbvalue = __DIE_DB__.format(product_choice)
        query_result = mongo_query.run_query(dbvalue, qual_choice, query)
        for each in query_result:
            each['_id_pair'] = dict(zip(each['_id_name'].split(','), each['_id'].split(',')))

        output = set(str('X')
                        +(x['_id_pair']['x'])
                        +str(',Y')
                        +(x['_id_pair']['y'])
                    for x in query_result)


        return [{'label': i, 'value': i} for i in output]
    except Exception as e:
        return []


@app.callback(Output('toggle-normalization'+__layout__, 'value'),[
              Input('toggle-normalization-R1', 'n_clicks'),
              Input('toggle-normalization-R2', 'n_clicks'),
              Input('toggle-normalization-R3', 'n_clicks')],
              [State('toggle-normalization'+__layout__, 'value')])
def normalization(dut, die, blk, old_flag):
    flag = {}
    if dut is not None: flag['dut']=dut%2
    else: flag['dut'] = old_flag['dut']
    if die is not None: flag['die']=die%2
    else: flag['die'] = old_flag['die']
    if blk is not None: flag['blk']=blk%2
    else: flag['blk'] = old_flag['blk']
    #import pdb;pdb.set_trace()
    return flag







@app.callback(Output('R3'+__layout__, 'children'),[
              Input('product-dropdown', 'value'),
              Input('qual-dropdown', 'value'),
              Input('test-dropdown', 'value'),
              Input('dut-dropdown'+__layout__, 'value'),
              Input('die-dropdown'+__layout__, 'value'),
              Input('toggle-normalization'+__layout__, 'value'),
              Input('refresh-component', 'n_clicks'),
              Input('interval-component', 'n_intervals')])
def update_figure(product_choice, qual_choice, test_choice, dut_choice, die_choice, normalize_choice, manual_refresh, interval_refresh):
  def generate_statistic(datatype):
    dbvalue = __BLK_DB__.format(product_choice)
    if not dut_choice:
        return {'data': []}
    if not die_choice :
        return {'data': []}
    testtype = str(".*," + test_choice + ".*")
    duttype = str(".*," + dut_choice + ".*")
    dietype = str(".*," + die_choice.split(',')[0].split('X')[1]
                  +"," +  die_choice.split(',')[1].split('Y')[1] + ".*")


    query = {"$and": [ {"_id": {"$regex": testtype}},
                      {"_id": {"$regex": duttype}},
                      {"_id": {"$regex": dietype}},
                       {"_id": {"$regex": datatype}}
                      ]
             }

    query_result  = utils.query_statistic(query, dbvalue, qual_choice)
    #upper_limit = utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, normalize_choice, test_choice, dut_choice, die_choice) 
    xaxisUser = {'title': 'Block', 'type': 'category', 'tickangle': 45}
    yaxisUser = {'type': 'linear', 'title': datatype}
    if normalize_choice['blk']: #else __DEFAULT_UPPER_LIMIT__[layer]
      yaxisUser['range'] =  [0, utils.statistic_upper_limit(dbvalue, qual_choice, test_choice, dut_choice, die_choice)]


    return {'data': [
        go.Scattergl(

            x=[row['_id_pair']['blk_dec'] for row in query_result],
            y=[row[series] for row in query_result],
            text=[
                dut_choice
                 + "<br>"
                 + die_choice
                 + "<br>"
                 + str(row['_id_pair']['blk_dec']) for row in query_result
            ],
            opacity=0.85,
            legendgroup = series,
            name=series,
        ) for series in __STATS_COLUMN__
    ],'layout': go.Layout(
        xaxis=xaxisUser,
        yaxis=yaxisUser,
        margin={'b': 40, 't': 25, 'r': 5},
        showlegend=True,
        #legend={'x': 1, 'y': 1},
        #legend=dict(orientation="h"),
        #legend={'orientation': 'h',
        #        'xanchor': 'center',
        #        'y': 1.2,
        #        'x': 0.5
        #        },
        hovermode='closest',
        barmode='overlay'

        )
    }
  return [
    html.Div([
      html.Div(html.B(name), className='row container theme-color-tertiary',),
      html.Div(dcc.Graph(id='R3'+each, figure = generate_statistic(each)) ,className = 'row'),
    ], className="six columns") for name, each in [('tErase Statistics', 'ERASE_TIME'), ('tProgram Statistics', 'PGM_TIME')]
  ]

@app.callback(Output('R4'+__layout__, 'children'),[
              Input('product-dropdown', 'value'),
              Input('qual-dropdown', 'value'),
              Input('test-dropdown', 'value'),
              Input('dut-dropdown'+__layout__, 'value'),
              Input('die-dropdown'+__layout__, 'value'),
              Input('refresh-component', 'n_clicks'),
              Input('interval-component', 'n_intervals')])
def update_figure(product_choice, qual_choice, test_choice, dut_choice, die_choice, manual_refresh, interval_refresh):
  def generate_table():
    dbvalue = __BLK_GBB_DB__.format(product_choice)
    if not dut_choice:
        return [{}]
    if not die_choice :
        return [{}]
    testtype = str(".*," + test_choice + ",.*")
    duttype = str(".*," + dut_choice + ",.*")

    dietype = str(".*," + die_choice.split(',')[0].split('X')[1]
                  + "," + die_choice.split(',')[1].split('Y')[1] + ",.*")

    query = {"$and": [{"_id": {"$regex": testtype}},
                      {"_id": {"$regex": duttype}},
                      {"_id": {"$regex": dietype}},
                      ]
             }
    query_result = mongo_query.run_query(dbvalue, qual_choice, query)
    return tuple(dict(zip(row['_id_name'].split(','), row['_id'].split(','))) for row in query_result)
  return [
          html.Div(html.B('Bad Block Table'), className = 'row panel-head theme-color-secondary', ),
          html.Div(dt.DataTable(id='R4GBB',
                                rows=generate_table(),
                                editable=False,
                                row_selectable=True,
                                filterable=True,
                                sortable=True,
                                selected_row_indices=[]), className="row panel-body"),
      ]


@app.callback(Output('R2'+__layout__, 'children'),[
              Input('product-dropdown', 'value'),
              Input('qual-dropdown', 'value'),
              Input('test-dropdown', 'value'),
              Input('dut-dropdown'+__layout__, 'value'),
              Input('toggle-normalization'+__layout__, 'value'),
              Input('refresh-component', 'n_clicks'),
              Input('interval-component', 'n_intervals')])
def update_figure(product_choice, qual_choice, test_choice, dut_choice, normalize_choice, manual_refresh, interval_refresh):
  def generate_histogram(datatype):
    dbvalue = __DIE_GBB_DB__.format(product_choice)
    if not dut_choice:
        return {'data': []}
    testtype = str(".*," + test_choice + ".*")
    duttype = str(".*," + dut_choice + ".*")

    query = {"$and": [{"_id": {"$regex": testtype}},
                      {"_id": {"$regex": duttype}},
                      ]
             }

    
    query_result  = utils.query_histogram(query, dbvalue, qual_choice)
    xaxisUser = {'title': 'Cycle', 'type': 'linear', 'tickangle':45}
    yaxisUser = {'type': 'linear', 'title': datatype}
    #query_result = sorted(query_result, key =
    #functools.cmp_to_key(lambda a, b: cmp(int(a['_id_pair'].get('cyclecount', 1)),int(b['_id_pair'].get('cyclecount', 1)))))
    graph = {'data':[
            go.Scattergl(
            x= row['value'][0],
            y= tuple(accumulate(row['value'][1])),
            text=
                dut_choice
                + "<br>"
                + 'X{}, Y{}'.format(row['_id_pair']['x'],
                                    row['_id_pair']['y']),
            opacity=0.85,
            mode='lines+markers',
            marker={
                'size': 10,
                'line': {'width': 0.5, 'color': 'white'}
            },

            name=
                dut_choice
                + "<br>"
                + 'X{}, Y{}'.format(row['_id_pair']['x'],
                                    row['_id_pair']['y']),
        ) for row in query_result
    ],'layout': go.Layout(
        xaxis=xaxisUser,
        yaxis=yaxisUser,
        margin={'b': 40, 't': 25, 'r': 5},
        showlegend=False,
        # legend={'x': 1, 'y': 1},
        # legend=dict(orientation="h"),
        #legend={'orientation': 'h',
        #        'xanchor': 'center',
        #        'y': 1.2,
        #        'x': 0.5
        #        },
        hovermode='closest'

        )
    }
    return {'data':[
            go.Scattergl(
            x= row['value'][0],
            y= tuple(accumulate(row['value'][1])),
            text=
                dut_choice
                + "<br>"
                + 'X{}, Y{}'.format(row['_id_pair']['x'],
                                    row['_id_pair']['y']),
            opacity=0.85,
            mode='lines+markers',
            marker={
                'size': 10,
                'line': {'width': 0.5, 'color': 'white'}
            },

            name=
                dut_choice
                + "<br>"
                + 'X{}, Y{}'.format(row['_id_pair']['x'],
                                    row['_id_pair']['y']),
        ) for row in query_result
    ],'layout': go.Layout(
        xaxis=xaxisUser,
        yaxis=yaxisUser,
        margin={'b': 40, 't': 25, 'r': 5},
        showlegend=False,
        # legend={'x': 1, 'y': 1},
        # legend=dict(orientation="h"),
        #legend={'orientation': 'h',
        #        'xanchor': 'center',
        #        'y': 1.2,
        #        'x': 0.5
        #        },
        hovermode='closest'

        )
    }

  def generate_statistic(datatype):
    dbvalue = __DIE_DB__.format(product_choice)
    if not dut_choice:
        return {'data': []}
    testtype = str(".*," + test_choice + ",.*")
    duttype = str(".*," + dut_choice + ",.*")

    query = {"$and": [ {"_id": {"$regex": testtype}},
                       {"_id": {"$regex": duttype}},
                       {"_id": {"$regex": datatype}}
                      ]
             }


    query_result  = utils.query_statistic(query, dbvalue, qual_choice)
    #upper_limit = utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, normalize_choice, test_choice, dut_choice, die_choice) 

    xaxisUser = {'title': 'Die', 'type': 'category', 'tickangle':45}
    yaxisUser = {'type': 'linear', 'title': datatype}
    if normalize_choice['die']: #else __DEFAULT_UPPER_LIMIT__[layer]
      yaxisUser['range'] =  [0, utils.statistic_upper_limit(dbvalue, qual_choice, test_choice, dut_choice)]
    return {'data': [
        go.Scattergl(

            x=['{}:{}'.format(row['_id_pair']['x'],
                                    row['_id_pair']['y']) for row in query_result],
            y=[row[series] for row in query_result],
            text=[
                dut_choice
                + "<br>"
                + 'X{}, Y{}'.format(row['_id_pair']['x'],
                                    row['_id_pair']['y']) for row in query_result
            ],
            opacity=0.85,
            legendgroup=series,
            name=series,
        ) for series in __STATS_COLUMN__
    ],'layout': go.Layout(
        xaxis=xaxisUser,
        yaxis=yaxisUser,
        margin={'b': 40, 't': 25, 'r': 5},
        showlegend=True,
        # legend={'x': 1, 'y': 1},
        # legend=dict(orientation="h"),
        #legend={'orientation': 'h',
        #        'xanchor': 'center',
        #        'y': 1.2,
        #        'x': 0.5
        #        },
        hovermode='closest',

        )
    }
  return [
  html.Div([
      html.Div(html.B(name), className='row container theme-color-tertiary',),
      html.Div(dcc.Graph(id='R2'+each, figure = generate_histogram(each)), className = 'row'),
    ], className="four columns") for name, each in [('Bad Block Growth', 'GBB')]
  ]+[
    html.Div([
      html.Div(html.B(name), className='row container theme-color-tertiary',),
      html.Div(dcc.Graph(id='R2'+each, figure = generate_statistic(each)), className = 'row'),
    ], className="four columns") for name, each in [('tErase Statistics', 'ERASE_TIME'), ('tProgram Statistics', 'PGM_TIME')]
  ]




@app.callback(Output('R1'+__layout__, 'children'),[
              Input('product-dropdown', 'value'),
              Input('qual-dropdown', 'value'),
              Input('test-dropdown', 'value'),
              Input('toggle-normalization'+__layout__, 'value'),
              Input('refresh-component', 'n_clicks'),
              Input('interval-component', 'n_intervals')])
def update_figure(product_choice, qual_choice, test_choice, normalize_choice, manual_refresh, interval_refresh):
  def generate_histogram(datatype):
    dbvalue = __DUT_GBB_DB__.format(product_choice)
    if not test_choice:
        return {'data': []}
    testtype = str(".*," + test_choice + ",.*")

    query = {"$and": [ {"_id": {"$regex": testtype}},
                ]
             }

    xaxisUser = {'title': 'Cycle', 'type': 'linear', 'tickangle':45}
    yaxisUser = {'type': 'linear', 'title': datatype}

    query_result  = utils.query_histogram(query, dbvalue, qual_choice)
    return {'data':[
            go.Scattergl(
            x= row['value'][0],
            y= tuple(accumulate(row['value'][1])),
            text=
                row['_id_pair']['dut']
                + '<br>'
                + row['_id_pair']['pcname'],
            opacity=0.85,
            mode='lines+markers',
            marker={
                'size': 10,
                'line': {'width': 0.5, 'color': 'white'}
            },

            name=
                row['_id_pair']['dut']
                + '<br>'
                + row['_id_pair']['pcname'],
        ) for row in query_result
    ],'layout': go.Layout(
        xaxis=xaxisUser,
        yaxis=yaxisUser,
        margin={'b': 40, 't': 25, 'r': 5},
        showlegend=False,
        #legend={'x': 1, 'y': 1},
        # legend=dict(orientation="h"),
        #legend={'orientation': 'h',
        #        'xanchor': 'center',
        #        'y': 1.2,
        #        'x': 0.5
        #        },
        hovermode='closest'
        )
    }

  def generate_statistic(datatype):
    dbvalue = __DUT_DB__.format(product_choice)
    if not test_choice:
        return {'data': []}
    testtype = str(".*," + test_choice + ",.*")

    query = {"$and": [ {"_id": {"$regex": testtype}},
                       {"_id": {"$regex": datatype}}
                      ]
             }
    query_result = utils.query_statistic(query, dbvalue, qual_choice)
    xaxisUser = {'type': 'category', 'tickangle':45}
    yaxisUser = {'type': 'linear', 'title': datatype}
    if normalize_choice['dut']:
      yaxisUser['range'] =  [0, utils.statistic_upper_limit(dbvalue, qual_choice, test_choice)]

    return {'data': [
        go.Scattergl(
            x=[row['_id_pair']['dut'] for row in query_result],
            y=[row[series] for row in query_result],
            text=[
                row['_id_pair']['dut']
                + '<br>'
                + row['_id_pair']['pcname'] for row in query_result
            ],
            opacity=0.85,
            legendgroup = series,
            name=series,
        ) for series in __STATS_COLUMN__
    ],'layout': go.Layout(
        xaxis=xaxisUser,
        yaxis=yaxisUser,
        margin={'b': 40, 't': 25, 'r': 5},
        showlegend=True,
        # legend={'x': 1, 'y': 1},
        # legend=dict(orientation="h"),
        #legend={'orientation': 'h',
        #        'xanchor': 'center',
        #        'y': 1.2,
        #        'x': 0.5
        #        },
        hovermode='closest',

        )
    }
  return [
  html.Div([
      html.Div(html.B(name), className='row container theme-color-tertiary',),
      html.Div(dcc.Graph(id='R1'+each, figure = generate_histogram(each)), className = 'row'),
    ], className="four columns") for name, each in [('Bad Block Growth', 'GBB')]
  ]+[
    html.Div([
      html.Div(html.B(name), className='row container theme-color-tertiary',),
      html.Div(dcc.Graph(id='R1'+each, figure = generate_statistic(each)), className = 'row'),
    ], className="four columns") for name, each in [('tErase Statistics', 'ERASE_TIME'), ('tProgram Statistics', 'PGM_TIME')]
  ]





if __layout__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        port = 8055
    else:
        port = sys.argv[1]
    app.run_server(host='0.0.0.0', port = int(port), debug = True)