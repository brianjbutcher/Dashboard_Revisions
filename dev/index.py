import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
#from flask import send_from_directory
import dash_table_experiments as dt
import flask

import logging
import time

_logger = logging.getLogger(__name__)

import query as mongo_query
import dash

app = dash.Dash(static_url_path='')
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally = True

from layouts import STATS, HISTO

app.layout = html.Div([
    html.Span(dt.DataTable(rows=[{}]), style={'display': 'none'}),
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='interval-component', interval = 2*60*1000, n_intervals = 0),
    html.Div(id='titlebar', className = 'row',
        children=[
            html.Div(html.H3('Western Digital', id = 'top-left-title'), className="three columns"),
            html.Div(html.H3('Real-Time Memory Test Monitor', id = 'top-right-title',), className="nine columns")
        ]
    ),
    html.Div([
        html.Div(html.Div(html.Div([
            html.Label('Product', className = 'theme-color-primary'),
            dcc.Dropdown(id='product-dropdown', placeholder="Choose BiCS3, BiCS4, etc."),
          ], className = 'container'), className = 'panel'), className='four columns'),

          html.Div(html.Div(html.Div([
            html.Label('Qualification', className = 'theme-color-primary'),
            dcc.Dropdown(id='qual-dropdown', placeholder="Choose Apple, iNAND, ESS, etc."),
          ], className = 'container'), className = 'panel'), className='four columns'),

        html.Div(html.Div(html.Div([
          html.Label('Test', className = 'theme-color-primary'),
          dcc.Dropdown(id='test-dropdown', placeholder="Choose certain test by Leg/Checkpoint/Step"),
        ], className = 'container'), className = 'panel'), className='four columns'),
    ], id='navbar', className='row bar'),

    html.Div([
      html.Div([

          html.Div(html.Div(html.Div([
              html.Div([
                  html.Label('Machine Readable Test Condition Label',
                             className='theme-color-quaternary', ),
              ], className='row'),
              html.Div(id='test-condition-label')
          ], className='panel theme-color-surface-variant'),
              className='four columns offset-by-four'), className='row container'),

          html.Div(html.Div(html.Div([html.Hr()], className='panel theme-color-surface-variant'),
              className='four columns offset-by-four'), className='row container'),


      html.Div(html.Div(html.Div([
          html.Div([
            html.Label('Data Query Time Stamp', className = 'theme-color-quaternary', ),
          ], className = 'row'),
          html.Div([
            html.B(id='last-query-time',  className = 'eight columns'),
            html.Button('Refresh', id='refresh-component',className = 'three columns offset-by-one')
          ],  className = 'row')
        ], className = 'panel theme-color-surface-variant'), className = 'four columns offset-by-four'), className = 'row container'),


      ], className = 'row', id='metabar'),

      html.Div(id = 'plot-area'),

      ], id='master', style= {'visibility':'hidden'}),
    #html.Div([
    #    html.Div([
    #        dcc.Textarea(id='text-input', placeholder='Start Typing Any Notes Here'),
    #    ], id = 'memo-body', className = '', style = {'display':'none','width': '100%', 'height': '100%'} ),
    #    html.Div([
    #        html.Button('Show Memo', id='toggle-memo'),
    #    ], className = '')
    #], className = 'container', id = 'memo-panel'),
    html.Button(id='toggle-layer', className ='theme-color-primary',style = {}),

    html.Div([
            html.Div([
                html.Div(
                    html.P('Western Digital Corporation or its affiliates. All rights reserved. Confidential.',
                        id = 'bottom-title',
                        ), className = 'four columns offset-by-four',
                        style = {'text-align':'center',
                             'color':'#ffffff',}),
                 #html.Img(src='data:image/png;base64,{}'.format(encoded_image_footer),
                 #         style={'width': '100%'}),
                    html.Div([
                        html.Span('Powered by dash'), html.Br(),
                        html.Span('core v{}'.format(dcc.__version__)), html.Br(),
                        html.Span('html v{}'.format(html.__version__)),html.Br(),
                        #html.Span('flask v{}'.format(flask.__version__))
                        ],style = {
                            'color':'#ffffff',
                            'text-align':'right',
                            'padding-right': '1%',
                            'font-size':'14px'
                        }, className = 'four columns'),

            ], className = 'row'), 
    ], id = 'footbar'),
], style = {
    'padding': '0',
    'margin': '0',
})

routes = {
    '/apps/stats': STATS,
    '/apps/stats_slc':STATS,
    '/apps/histo': HISTO,
    '/apps/histo_slc': HISTO,
}
stores = {
    '/apps/stats': 'DUT___{}___PerfStats',
    '/apps/stats_slc':'DUT___{}___PerfStats',
    '/apps/histo': 'DUT___{}___FBCHisto',
    '/apps/histo_slc': 'DUT___{}___FBCHisto',
}


@app.callback(Output('toggle-layer', 'value'),
              [Input('toggle-layer', 'n_clicks'), Input('toggle-layer', 'n_clicks_timestamp')],
              [])
def flip_layer(click, timestamp):
    return (['LP','MP','UP'],['SLC'])[int(click)%2 if click else 0]


@app.callback(Output('toggle-layer', 'children'),
              [Input('toggle-layer', 'n_clicks'), Input('toggle-layer', 'n_clicks_timestamp')],)
def toggle_layer(click, timestamp):
    return ('TLC Mode','SLC Mode')[int(click)%2 if click else 0]
'''
@app.callback(Output('memo-body', 'style'),
              [Input('toggle-memo', 'n_clicks'), Input('toggle-memo', 'n_clicks_timestamp')],
              [State('memo-body', 'style')])
def show_memo(click, timestamp, style):
    #old_visibility = old_style['visibility'] if 'visibility' in old_style else None
    #print(click, timestamp)
    style.update({'display': 'initial' if click and int(click)%2 else 'none'})
    return style


@app.callback(Output('toggle-memo', 'children'),
              [Input('toggle-memo', 'n_clicks'),],)
def toggle_memo(click):
    return 'Hide Memo' if click and int(click)%2 else 'Show Memo'

'''
import re
@app.callback(Output('toggle-layer', 'style'),
              [Input('url', 'pathname')],
              [State('toggle-layer', 'style')])
def flip_layer(pathname, style):
    if not pathname: return style
    if re.search('stat', str(pathname)):
        style['display'] = 'none'
    else: 
        style['display'] = 'initial'
    return style

@app.callback(Output('plot-area', 'children'),
              [Input('url', 'pathname')])
def display_layout(pathname):

    if not pathname: return "please provide specific app url!"
    try:
        return routes[pathname.lower()].layout
    except KeyError:
        return "requested app not found!"
#    try:
#        import importlib
#        mod = importlib.import_module('layouts.{}'.format(routes[pathname]))
#        return mod.layout
#    except KeyError:
#        return "dummy - check URL for type-o's"


@app.callback(Output('last-query-time', 'children'),
              [
               Input('refresh-component', 'n_clicks'),
               Input('interval-component', 'n_intervals')])
def update_timestamp( manual_refresh, interval_refresh):
    #print(manual_refresh)
    return time.strftime("%I:%M:%S %d/%m/%Y")


@app.callback(Output('test-condition-label', 'children'),[
              Input( 'product-dropdown', 'value'),
              Input( 'qual-dropdown'   , 'value'),
              Input( 'test-dropdown', 'value'),
              Input( 'interval-component', 'n_intervals'),
              Input('url', 'pathname')])
def update_condition_label(product_choice, qual_choice, test_choice, interval_refresh, pathname):

    if not pathname: return []
    if not qual_choice: return []
    try:
        dbvalue = stores[pathname.lower()].format(product_choice)
        testtype = str(".*," + test_choice + ".*")
        query = {"_id": {"$regex": testtype}}
        #uid = mongo_query.run_query_unique(dbvalue, qual_choice, query, '_id')
        #query_result = tuple(mongo_query.run_query(dbvalue, qual_choice, {"_id": each},limit = 1)[0] for each in uid)
        
        query_result = mongo_query.get_databases(db = dbvalue)[qual_choice].aggregate([{'$match':query},{'$group':{'_id': '$_id', '_id_name':{'$first':'$_id_name'}}}])
        output = set(dict(zip(each['_id_name'].split(','), each['_id'].split(','))).get('testname','EMPTY_CHECK_SOURCE') for each in query_result)

        return [html.Div(html.B('{}'.format(i)),className='row') for i in output]
    except Exception as e:
        return html.B('No valid ID label found')

@app.callback(Output('product-dropdown', 'options'),[Input('interval-component', 'n_intervals')])
def update_dropdown(interval_refresh):
    try:
      names = mongo_query.get_collection_map()
      return [{'label': y, 'value': y}  for y in set(x.split('___')[1] for x in sorted(names.keys(), key = lambda each: each.lower()) if x not in ('admin', 'config', 'local'))]
    except Exception as err:
      #return [{'label': i,'value': i} for i in [str(err)]]
      return []


@app.callback(Output( 'qual-dropdown', 'options'),
  [Input('product-dropdown', 'value'),Input('interval-component', 'n_intervals'),Input('url', 'pathname')])
def update_dropdown(product_choice, interval_refresh, pathname):
    if not pathname: return []
    try:
        names = mongo_query.get_collection_map()
        dbvalue = stores[pathname.lower()].format(product_choice)
        return [{'label' : x, 'value': x} for x in sorted(names[dbvalue], key = lambda each: each.lower())]
    except Exception as err:
      #return [{'label': i,'value': i} for i in [str(err)]]
      return []


@app.callback(Output( 'test-dropdown', 'options'),
            [Input('product-dropdown', 'value'),
            Input( 'qual-dropdown', 'value'),
            Input( 'interval-component', 'n_intervals'), Input('url', 'pathname')])
def update_dropdown(product_choice, qual_choice, interval_refresh, pathname):
    if not pathname: return []
    if not qual_choice: return []
    try:
        # client = MongoClient(host='10.196.155.85', port=27017)
        #print(product_choice, qual_choice)

        dbvalue = stores[pathname.lower()].format(product_choice)

        #import pdb; pdb.set_trace()
        #query_result = mongo_query.run_query_unique(dbvalue, qual_choice, {}, "_id")
        query_result = mongo_query.get_databases(db = dbvalue)[qual_choice].aggregate([{'$group':{'_id': '$_id', '_id_name':{'$first':'$_id_name'}}}])

        #_logger.info(type(uid))
        #query_result = tuple(mongo_query.run_query(dbvalue, qual_choice, {"_id": each}, limit= 1)[0] for each in uid)
        #output = set(x.split(',')[2] for x in query_result)
        output = set(dict(zip(each['_id_name'].split(','), each['_id'].split(','))).get('testdatatype','EMPTY_CHECK_SOURCE') for each in query_result)

        return [{'label': i, 'value': i} for i in sorted(output, key = lambda each: each.lower())]
    except Exception as err:
      _logger.error(uid)
      _logger.error(err)
      #return [{'label': i,'value': i} for i in [str(err)]]
      return []


@app.callback(Output('master', 'style'),[
            #Input('product-dropdown', 'value'),
            #Input('qual-dropdown', 'value'),
            #Input('test-dropdown', 'value'),
            Input('test-dropdown', 'value'),
            Input('url', 'pathname')],
            [State('master', 'style')])
def display_style(test_choice, pathname, style):
    
    if not pathname: return style
    try:
        style.update(routes[pathname.lower()].style)
    except:
        pass
    if test_choice is not None:
        style.update({'visibility':'visible'})
    else:
        style.update({'visibility':'hidden'})
    return style


@app.server.route('/assets/<path>')
def send_assets(path):
    import os
    return flask.send_from_directory(os.path.join(os.getcwd(), 'assets'), path)

@app.server.after_request
def add_header(response):
    # response.cache_control.no_store = True
    #if 'Cache-Control' not in response.headers:
    response.headers['Cache-Control'] = 'no-store'
    return response

external_css = ["/assets/reset.css", "/assets/extra.css"] #"https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/css/bootstrap.min.css",
external_js = ['https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/js/bootstrap.min.js', 'https://code.jquery.com/jquery-3.3.1.slim.min.js', 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js']
#external_css = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css""https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css", "https://codepen.io/chriddyp/pen/brPBPO.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='[%(asctime)-15s %(name)s %(levelname)s] %(message)s')
    
    #for js in external_js:
    #    app.scripts.append_script({"external_url": js})
    app.run_server(host='0.0.0.0', debug=True)
