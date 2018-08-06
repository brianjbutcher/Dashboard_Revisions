from dash.dependencies import Input, Output, Event, State
import dash_core_components as dcc
import dash_html_components as html

from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

#init_notebook_mode(connected=True)

#import plotly.graph_objs as go
# from loremipsum import get_sentences
import dash_table_experiments as dt
import plotly
import query as mongo_query
# from pprint import pprint
import os
from collections import defaultdict
import base64
import time
import functools
import itertools
import random
import flask
import logging

from layouts import utils
_logger = logging.getLogger(__name__)

from index import app


__DUT_DB__ = 'DUT___{}___FBCHisto'
__DIE_DB__ = 'DIE___{}___FBCHisto'
__BLK_DB__ = 'BLK___{}___FBCStats'

__STATS_COLUMN__ = ('max', 'min', 'avg' )
#import pdb; pdb.set_trace()

__DEFAULT_UPPER_LIMIT__ = {'LP':150, 'MP':150, 'UP':150, 'SLC':20}


__layout__ = '-'+__name__.split('.')[-1]

__SAMPLE_STEP__ = 5
import operator
def reverse_accumulate(iterable, func=operator.add):
    'Return running totals'
    # accumulate([1,2,3,4,5]) --> 1 3 6 10 15
    # accumulate([1,2,3,4,5], operator.mul) --> 1 2 6 24 120
    #sum = reduce(func, reversed(iterable))
    it = iter(reversed(iterable))
    #it = iter(iterable)
    try:
        total = next(it)
    except StopIteration:
        return
    yield total
    for element in it:
        total = func(total, element)
        yield total




#image_filename = os.path.join(os.getcwd(), 'assets','UpdatedWDCheader.PNG') # replace with your own image
#encoded_image_header = base64.b64encode(open(image_filename, 'rb').read())


#image_filename = os.path.join(os.getcwd(), 'assets','UpdatedWDCfooter.PNG') # replace with your own image
#encoded_image_footer = base64.b64encode(open(image_filename, 'rb').read())


style={
    'font-family' : '"avenir",arial',
    #'fontFamily': 'Sans-Serif',
    #'fontsize' : '22',
    }

layout = [   
  dcc.Input(id='toggle-normalization'+__layout__, style = {'display':'none'}, value={'dut':0, 'die':0, 'blk':0}),

  html.Div([
      html.Div([
          html.Div([
            html.Label('DUT Level Analysis', className= 'eight columns offset-by-one'),
            html.Button('Normalize plots', id='toggle-normalization-R1', className = 'two columns offset-by-one'),
          ], className = 'row panel-head theme-color-secondary'),
          html.Div(id = 'R1'+__layout__, className = 'row panel-body container-fluid'),
        ], className="panel row plotbar"),

      #html.Hr(),
      #html.Div(dcc.Textarea(className = 'row', style = {'width': '80%', 'margin-left': '10%'},
      #                      placeholder='Click and start typing any notes, which will be saved when you export page'), className = 'container'),
      #html.Hr(),
      html.Div([
          html.Div([
            html.Label('Die Level Analysis', className= 'two columns offset-by-one'),

            html.Div(dcc.Dropdown(id='dut-dropdown'+__layout__,
                        placeholder="Select a DUT for Die Level Analysis"),
                        className= 'four columns offset-by-one'),
            html.Button('Normalize Plots', id='toggle-normalization-R2', className = 'two columns offset-by-two'),
          ], className = 'row panel-head theme-color-secondary'),
          html.Div(id = 'R2'+__layout__, className = "row panel-body container-fluid"),
        ], className="row plotbar panel"),


      #html.Hr(),
      #html.Div(dcc.Textarea(className = 'row', style = {'width': '80%', 'margin-left': '10%'},
      #                      placeholder='Click and start typing any notes, which will be saved when you export page'), className = 'container'),
      #html.Hr(),
      html.Div([
          html.Div([
            html.Label('Block Level Analysis', className= 'two columns offset-by-one'),
            html.Div(dcc.Dropdown(id='die-dropdown'+__layout__,
                            placeholder="Select a DIE for Block Level Analysis"),className= 'four columns offset-by-one'),
            html.Button('Normalize Plots', id='toggle-normalization-R3', className = 'two columns offset-by-two'),
        ], className = 'row panel-head theme-color-secondary'),
        html.Div(id = 'R3'+__layout__ , className="row panel-body container-fluid"),
      ], className="panel row plotbar"),
      

      html.Hr(style = {'visibility':'hidden'}),
  ], className = 'bar')

]


@app.callback(Output('dut-dropdown'+__layout__, 'options'),[
              Input( 'product-dropdown', 'value'),
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
              Input( 'product-dropdown', 'value'),
              Input('qual-dropdown', 'value'),
              Input('test-dropdown', 'value'),
              Input('dut-dropdown'+__layout__, 'value'),
              Input('refresh-component', 'n_clicks'),
              Input('interval-component', 'n_intervals')],)
def update_dropdown(product_choice, qual_choice, test_choice, dut_choice, manual_refresh, interval_refresh):

    try:
        # print('dut_choice',dut_choice)
        # client = MongoClient(host='10.196.155.85', port=27017)
        query = {"$and": [ {"_id": {"$regex": test_choice}},
                           {"_id": {"$regex": dut_choice }}
                          ]
                 }
        dbvalue = __DIE_DB__.format(product_choice)
        query_result = mongo_query.run_query(dbvalue, qual_choice, query)
        for each in query_result:
            each['_id_pair'] = dict(zip(each['_id_name'].split(','), each['_id'].split(',')))
        # print(BLKList.head())
        #import pdb; pdb.set_trace()
        # print(lstDD)
        output = set(str('X')
                        +(x['_id_pair']['x'])
                        +str(',Y')
                        +(x['_id_pair']['y'])
                    for x in query_result)


        # print('OUTPUT',output)
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
              Input('toggle-layer', 'value'),
              Input('refresh-component', 'n_clicks'),
              #Input('interval-component', 'n_intervals'),
              ])
def update_figure(product_choice, qual_choice, test_choice, dut_choice, die_choice, normalize_choice, layer_choice, manual_refresh):
    if not die_choice :
      return []

    testtype = str(".*," + test_choice + ".*")
    duttype  = str(".*," + dut_choice + ".*")
    dietype  = str(".*," + die_choice.split(',')[0].split('X')[1]+ "," + die_choice.split(',')[1].split('Y')[1] + ".*")
    xaxisUser = {'title': 'BlockNo', 'type': 'category', 'tickangle': 45}
    yaxisUser = {'type': 'linear', 'title': 'Stats'}
    if normalize_choice['blk']: #else __DEFAULT_UPPER_LIMIT__[layer]
      yaxisUser['range'] =  [0, utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, testtype, duttype, dietype)]
    def generate_figure(layer):
      dbvalue = __BLK_DB__.format(product_choice)

      query = {"$and": [{"_id": {"$regex": testtype}}
                       ,{"_id": {"$regex": duttype}}
                       ,{"_id": {"$regex": dietype}}
                       ,{"_id": {"$regex": ".*,{}.*".format(layer)}}
                       ]
               }


      query_result  = utils.query_statistic(query, dbvalue, qual_choice)
      #upper_limit = utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, normalize_choice, test_choice, dut_choice, die_choice) 


      return {'data': [
          go.Scatter(

              x=[row['_id_pair']['blk_dec'] for row in query_result],
              y=[row[series] for row in query_result],
              text=[
              str(row['_id_pair']['blk_dec'])+ '<br>'
                  + 'S{}, G{}'.format(row['_id_pair'].get('setno', 0),row['_id_pair'].get('groupno', 0)) for row in query_result
              ],
              opacity=0.7,
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
    chart_title = {
    'LP':'Lower Page Statistics', 
    'MP':'Middle Page Statistics',
    'UP':'Upper Page Statistics',
    'SLC':'Single Page Statistics'
    }
    return [
            html.Div([
                html.Div(html.B(chart_title[layer]),
                         className='row container theme-color-tertiary',
                         ),
                html.Div(dcc.Graph(
                  id = 'R3'+layer,
                  figure = generate_figure(layer), 
                  className = 'row')
                )], className="{} columns".format(utils.number_to_word(int(12/len(layer_choice)))))
            for layer in layer_choice ]

@app.callback(Output('R2'+__layout__, 'children'),[
              Input('product-dropdown', 'value'),
              Input('qual-dropdown'   , 'value'),
              Input('test-dropdown'   , 'value'),
              Input('dut-dropdown'+__layout__, 'value'),
              Input('toggle-normalization'+__layout__      , 'value'),
              Input('toggle-layer', 'value'),
              Input('refresh-component', 'n_clicks'),
              #Input('interval-component', 'n_intervals')]
              ])
def update_figure(product_choice, qual_choice, test_choice, dut_choice, normalize_choice, layer_choice, manual_refresh):
    if not dut_choice:
      return []
    testtype = str(".*," + test_choice + ".*")
    duttype = str(".*," + dut_choice + ".*")
    xaxisUser = {'title': 'FBC', }
    yaxisUser = {'type': 'log', 'title': 'Sector Count'}
    if normalize_choice['die']: #else __DEFAULT_UPPER_LIMIT__[layer]
      xaxisUser['range'] =  [0, utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, testtype, duttype)]
      #raise Exception(utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, test_choice, dut_choice))
    def generate_figure(layer):
      dbvalue = __DIE_DB__.format(product_choice)
      #if not dut_choice:
      #  return {'data': []}
      query = {"$and": [ {"_id": {"$regex": testtype}}
              , {"_id": {"$regex": duttype}}
              , {"_id": {"$regex": ".*,{}.*".format(layer)}}
              ]}
      query_result  = utils.query_histogram(query, dbvalue, qual_choice)
      #upper_limit = utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, normalize_choice, test_choice, dut_choice) if normalize_choice['die'] else __DEFAULT_UPPER_LIMIT__[layer]

      return {'data': [
          go.Scattergl(
              #x=tuple(reversed(row['value'][0])),
              #y=tuple(accumulate(row['value'][1])),
              x=tuple(y for x,y in enumerate(reversed(row['value'][0])) if x==0 or x in range(len(row['value'][0])-1, 0, -__SAMPLE_STEP__)),
              y=tuple(y for x,y in enumerate(reverse_accumulate(row['value'][1])) if x==0 or x in range(len(row['value'][1])-1, 0, -__SAMPLE_STEP__)),
              text='X{}, Y{}'.format(row['_id_pair']['x'],row['_id_pair']['y']) + '<br>'
                  + 'S{}, G{}'.format(row['_id_pair'].get('setno', 0),row['_id_pair'].get('groupno', 0)),

              mode='lines+markers',
              opacity=0.7,
              marker={
                  'size': 5,
                  'line': {'width': 0.5, 'color': 'white'}
              },
              name='X{}, Y{}'.format(row['_id_pair']['x'],row['_id_pair']['y']) + '<br>'
                  + 'S{}, G{}'.format(row['_id_pair'].get('setno', 0),row['_id_pair'].get('groupno', 0)),

          ) for row in query_result
      ],
          'layout': go.Layout(

              xaxis=xaxisUser,
              yaxis=yaxisUser,
              margin={'b': 40, 't': 25, 'r': 15},
              showlegend=True,
              legend={'x': 1, 'y': 1},

              hovermode='closest'
          )
      }

    chart_title = {
    'LP':'Lower Page Histogram', 
    'MP':'Middle Page Histogram',
    'UP':'Upper Page Histogram',
    'SLC':'Single Page Histogram'
    }
    return [
            html.Div([
                html.Div(html.B(chart_title[layer]),
                         className='row container theme-color-tertiary',
                         ),
                html.Div(dcc.Graph(
                  id = 'R2'+layer,
                  figure = generate_figure(layer), 
                  className = 'row')
                )], className="{} columns".format(utils.number_to_word(int(12/len(layer_choice)))))
            for layer in layer_choice ]

@app.callback(Output('R1'+__layout__, 'children'),[
              Input('product-dropdown', 'value'),
              Input('qual-dropdown'   , 'value'),
              Input('test-dropdown'   , 'value'),
              Input('toggle-normalization'+__layout__, 'value'),
              Input('toggle-layer', 'value'),
              Input('refresh-component', 'n_clicks'),
              #Input('interval-component', 'n_intervals')]
              ])
def update_figure(product_choice, qual_choice, test_choice, normalize_choice, layer_choice, manual_refresh):
    if not test_choice:
      return []
    xaxisUser = {'title': 'FBC'}
    yaxisUser = {'type': 'log', 'title': 'Sector Count'}

    testtype = str(".*," + test_choice + ".*")
    if normalize_choice['dut']: #else __DEFAULT_UPPER_LIMIT__[layer]
      xaxisUser['range'] =  [0, utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, testtype)]
    def generate_figure(layer):
        
      dbvalue = __DUT_DB__.format(product_choice)

      query = {"$and": [
                {"_id": {"$regex": testtype}},
                {"_id": {"$regex": ".*,{}.*".format(layer)}}
              ]}

      query_result  = utils.query_histogram(query, dbvalue, qual_choice)
      #upper_limit = utils.statistic_upper_limit(__BLK_DB__.format(product_choice), qual_choice, normalize_choice, testtype) if normalize_choice['dut'] else __DEFAULT_UPPER_LIMIT__[layer]

      return {'data': [
          go.Scattergl(
              #x=tuple(reversed(row['value'][0])),
              #y=tuple(accumulate(row['value'][1])),
              x=tuple(y for x,y in enumerate(reversed(row['value'][0])) if x==0 or x in range(len(row['value'][0])-1, 0, -__SAMPLE_STEP__)),
              y=tuple(y for x,y in enumerate(reverse_accumulate(row['value'][1])) if x==0 or x in range(len(row['value'][1])-1, 0, -__SAMPLE_STEP__)),
              text=row['_id_pair']['dut']+ '<br>'
              + row['_id_pair']['pcname']+ '<br>'
              + 'S{}, G{}'.format(row['_id_pair'].get('setno', 0),row['_id_pair'].get('groupno', 0)),
              mode='lines+markers',
              opacity=0.7,
              marker={
                  'size': 5,
                  'line': {'width': 0.5, 'color': 'white'}
              },
              name=row['_id_pair']['dut']+ '<br>'
              + row['_id_pair']['pcname']+ '<br>'
              + 'S{}, G{}'.format(row['_id_pair'].get('setno', 0),row['_id_pair'].get('groupno', 0)),

          ) for row in query_result
      ],
          'layout': go.Layout(

              xaxis=xaxisUser,
              yaxis=yaxisUser,
              margin={'b': 40, 't': 25, 'r': 15},
              showlegend=False,
              legend={'x': 1, 'y': 1},

              hovermode='closest'
          )
      }

    chart_title = {
    'LP':'Lower Page Histogram', 
    'MP':'Middle Page Histogram',
    'UP':'Upper Page Histogram',
    'SLC':'Single Page Histogram'
    }
    return [
            html.Div([
                html.Div(html.B(chart_title[layer]),
                         className='row container theme-color-tertiary',
                         ),
                html.Div(dcc.Graph(
                  id ='R1'+layer,
                  figure = generate_figure(layer), 
                  className = 'row')
                )], className="{} columns".format(utils.number_to_word(int(12/len(layer_choice)))))
            for layer in layer_choice ]


server = app.server  # grapping server directly gunicorn

if __layout__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        port = 8050
    else:
        port = sys.argv[1]
    app.run_server(host='0.0.0.0', port = int(port))
