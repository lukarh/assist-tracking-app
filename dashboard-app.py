# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_daq as daq
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash import callback_context, dash_table, html, dcc

import plotly.express as px
import plotly.graph_objects as go

import math
import numpy as np
import pandas as pd

from datetime import date, datetime

##############################################################################
###################### Create Processed Data Template ########################
##############################################################################

from itertools import product

distances = ['0-10 ft.','10-20 ft.','20-30 ft.','30-40 ft.',      
             '40-50 ft.','50-60 ft.','60-70 ft.','70-80 ft.','80-90 ft.']       
shottypes = ['AtRim','ShortMidRange','LongMidRange',          
             'Arc3','Corner3']  
directions = ['N','NEN','NE','ENE','E','ESE','SE','SES',
              'S','SWS','SW','WSW','W','WNW','NW','NWN']

main_df = pd.read_csv('data/main_data.csv')
tracked_df = pd.read_csv('data/tracked_data.csv')

##############################################################################
##############################################################################
##############################################################################

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

server = Flask(__name__)

app = dash.Dash(__name__, server=server,
                external_stylesheets=[dbc.themes.FLATLY],
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
        )
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app.server)
con = db.engine.connect()

##############################################################################
################################ Draw Court ##################################
##############################################################################


def draw_plotly_court(fig, fig_width=500, fig_height=870, margins=10, lwidth=3,
                      show_title=True, labelticks=True, show_axis=True,
                      glayer='below', bg_color='white'):

    # From: https://community.plot.ly/t/arc-shape-with-path/7205/5
    def ellipse_arc(x_center=0.0, y_center=0.0, a=10.5, b=10.5,
                    start_angle=0.0, end_angle=2 * np.pi, N=200,
                    closed=False, opposite=False):
        t = np.linspace(start_angle, end_angle, N)
        x = x_center + a * np.cos(t)
        if opposite:
            y = y_center + b * np.sin(-t)
        else:
            y = y_center + b * np.sin(t)
        path = f'M {x[0]}, {y[0]}'
        for k in range(1, len(t)):
            path += f'L{x[k]}, {y[k]}'
        if closed:
            path += ' Z'
        return path

    ####################################################################
    ############################ dimensions ############################
    #  half-court -52.5 <= y <= 417.5, full-court -52.5 <= y <= 887.5  #
    ####################################################################
    fig.update_layout(height=870,
                      template='plotly_dark')

    # Set axes ranges
    fig.update_xaxes(range=[-250 - margins, 250 + margins],
                     visible=show_title)
    fig.update_yaxes(range=[-52.5 - margins, 887.5 + margins],
                     visible=show_title)

    threept_break_y = 89.47765084
    three_line_col = "#777777"
    main_line_col = "#777777"
    fig.update_layout(
        # Line Horizontal
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            fixedrange=True,
            visible=show_axis,
            showticklabels=labelticks,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            fixedrange=True,
            visible=show_axis,
            showticklabels=labelticks,
        ),
        yaxis2=dict(
            scaleanchor="x2",
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            fixedrange=True,
            visible=show_axis,
            showticklabels=labelticks,
            range=[-52.5 - margins, 887.5 + margins]
        ),
        xaxis2=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            fixedrange=True,
            visible=show_axis,
            showticklabels=labelticks,
            range=[-250 - margins, 250 + margins]
        ),
        showlegend=False,
        shapes=[
            # court border
            dict(
                type="rect", x0=-250, y0=-52.5, x1=250, y1=887.5,
                line=dict(color=main_line_col, width=lwidth),
                # fillcolor='#333333',
                layer=glayer
            ),
            # half-court line
            dict(
                type="line", x0=-250, y0=417.5, x1=250, y1=417.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            # back-court outer ft-lines
            dict(
                type="line", x0=-80, y0=697.5, x1=-80, y1=887.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            dict(
                type="line", x0=80, y0=697.5, x1=80, y1=887.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            # back-court inner ft-lines
            dict(
                type="line", x0=-60, y0=697.5, x1=-60, y1=887.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            dict(
                type="line", x0=60, y0=697.5, x1=60, y1=887.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            # front-court outer ft-lines
            dict(
                type="line", x0=-80, y0=-52.5, x1=-80, y1=137.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            dict(
                type="line", x0=80, y0=-52.5, x1=80, y1=137.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            # front-court inner ft-lines
            dict(
                type="line", x0=-60, y0=-52.5, x1=-60, y1=137.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            dict(
                type="line", x0=60, y0=-52.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            # back-court ft-circle
            dict(
                type="circle", x0=-60, y0=637.5, x1=60, y1=757.5, xref="x", yref="y",
                line=dict(color=main_line_col, width=lwidth),
                # fillcolor='#dddddd',
                layer=glayer
            ),
            # front-court ft-circle
            dict(
                type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y",
                line=dict(color=main_line_col, width=lwidth),
                # fillcolor='#dddddd',
                layer=glayer
            ),
            # back-court ft-line
            dict(
                type="line", x0=-80, y0=697.5, x1=80, y1=697.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            # front-court ft-line
            dict(
                type="line", x0=-80, y0=137.5, x1=80, y1=137.5,
                line=dict(color=main_line_col, width=lwidth),
                layer=glayer
            ),
            # back-court basket
            dict(
                type="circle", x0=-7.5, y0=827.5, x1=7.5, y1=842.5, xref="x", yref="y",
                line=dict(color="#ec7607", width=lwidth),
            ),
            dict(
                type="rect", x0=-2, y0=842.25, x1=2, y1=847.25,
                line=dict(color="#ec7607", width=lwidth),
                fillcolor='#ec7607',
            ),
            dict(
                type="line", x0=-30, y0=847.5, x1=30, y1=847.5,
                line=dict(color="#ec7607", width=lwidth),
            ),
            # front-court basket
            dict(
                type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
                line=dict(color="#ec7607", width=lwidth),
            ),
            dict(
                type="rect", x0=-2, y0=-7.25, x1=2, y1=-12.5,
                line=dict(color="#ec7607", width=lwidth),
                fillcolor='#ec7607',
            ),
            dict(
                type="line", x0=-30, y0=-12.5, x1=30, y1=-12.5,
                line=dict(color="#ec7607", width=lwidth),
            ),
            # back-court charge circle
            dict(type="path",
                 path=ellipse_arc(y_center=835, a=40, b=40,
                                  start_angle=0, end_angle=np.pi, opposite=True),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
            # front-court charge circle
            dict(type="path",
                 path=ellipse_arc(a=40, b=40, start_angle=0, end_angle=np.pi),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
            # back-court 3pt line
            dict(type="path",
                 path=ellipse_arc(y_center=835, a=237.5, b=237.5, start_angle=np.pi - \
                                                                              0.386283101, end_angle=0.386283101, opposite=True),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
            # front-court 3pt line
            dict(type="path",
                 path=ellipse_arc(
                     a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
            # back-court corner three lines
            dict(
                type="line", x0=-220, y0=835-threept_break_y, x1=-220, y1=887.5,
                line=dict(color=three_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=220, y0=835-threept_break_y, x1=220, y1=887.5,
                line=dict(color=three_line_col, width=lwidth), layer=glayer
            ),
            # front-court corner three lines
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=220, y0=-52.5, x1=220, y1=threept_break_y,
                line=dict(color=three_line_col, width=lwidth), layer=glayer
            ),
            # back-court tick marks
            dict(
                type="line", x0=-250, y0=607.5, x1=-220, y1=607.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=250, y0=607.5, x1=220, y1=607.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            # front-court tick marks
            dict(
                type="line", x0=-250, y0=227.5, x1=-220, y1=227.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=250, y0=227.5, x1=220, y1=227.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            # front-court free-throw tick marks
            dict(
                type="line", x0=-90, y0=17.5, x1=-80, y1=17.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=-90, y0=27.5, x1=-80, y1=27.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=-90, y0=57.5, x1=-80, y1=57.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=-90, y0=87.5, x1=-80, y1=87.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=90, y0=17.5, x1=80, y1=17.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=90, y0=27.5, x1=80, y1=27.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=90, y0=57.5, x1=80, y1=57.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=90, y0=87.5, x1=80, y1=87.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            # back-court free-throw tick marks
            dict(
                type="line", x0=-90, y0=817.5, x1=-80, y1=817.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=-90, y0=807.5, x1=-80, y1=807.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=-90, y0=777.5, x1=-80, y1=777.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=-90, y0=747.5, x1=-80, y1=747.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=90, y0=817.5, x1=80, y1=817.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=90, y0=807.5, x1=80, y1=807.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=90, y0=777.5, x1=80, y1=777.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=90, y0=747.5, x1=80, y1=747.5,
                line=dict(color=main_line_col, width=lwidth), layer=glayer
            ),
            # half-court outer circle
            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=60, b=60,
                                  start_angle=0, end_angle=2*np.pi),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
            # half-court inner circle
            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=25, b=25,
                                  start_angle=0, end_angle=2*np.pi),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
        ]
    )
    return True

##############################################################################
############################### Tracking Tab #################################
##############################################################################

GS = 100
fig = px.scatter(
    x=np.repeat(np.linspace(-300, 300, GS), GS),
    y=np.tile(np.linspace(-75, 900, GS), GS),
    opacity=0
)
draw_plotly_court(fig, margins=0)

##############################
display_fig = go.Figure()
draw_plotly_court(display_fig, show_title=False, labelticks=False, show_axis=False,
                  glayer='above', bg_color='black', margins=0)

##############################
hover_fig = px.scatter(
    x=np.repeat(np.linspace(-300, 300, GS), GS),
    y=np.tile(np.linspace(-75, 900, GS), GS),
    opacity=0
)
draw_plotly_court(hover_fig, show_title=False, labelticks=False, show_axis=False,
                  glayer='above', bg_color='black', margins=0)


##############################
hist_fig = px.histogram(nbins=24,
                        template="plotly_dark"
                        )

dist_fig = px.bar_polar(template="plotly_dark",
                        color_discrete_sequence=['#67001f','#bb2a34','#e58368','#fbceb6','#f7f7f7',
                                                 '#c1ddec','#6bacd1','#2a71b2','#053061'],
                        )

shottype_fig = px.bar_polar(template="plotly_dark",
                            color_discrete_sequence=['#67001f','#bb2a34','#e58368','#fbceb6','#f7f7f7',
                                                     '#c1ddec','#6bacd1','#2a71b2','#053061'],
                            )

sunburst_fig = px.sunburst(template='plotly_dark')

kde_fig = px.scatter_polar(template="plotly_dark")

court_graph = dcc.Graph(
    id='court-graph',
    figure=fig,
    config={'staticPlot': False,
            'scrollZoom': False,
            },
    style={"display": "inline-block",
           "float": "left",
           "height": "100%",
           "width": "100%",
           },
)

display_graph = dcc.Graph(
    id='display-graph',
    figure=display_fig,
    config={'staticPlot': False,
            'scrollZoom': False,
            },
)

rose_plot = dcc.Graph(
    id='rose-plot',
    figure=dist_fig,
    config={'staticPlot': False,
            'scrollZoom': False},
)

hist_plot = dcc.Graph(
    id='hist-plot',
    figure=hist_fig,
    config={'staticPlot': False,
            'scrollZoom': False}
)

sunburst_plot = dcc.Graph(
    id='sunburst-plot',
    figure=sunburst_fig,
    config={'staticPlot': False,
            'scrollZoom': False}
)

kde_plot = dcc.Graph(
    id='kde-plot',
    figure=kde_fig,
    config={'staticPlot': False,
            'scrollZoom': False}
)

rose_graph_tab = html.Div([
    rose_plot,
    hist_plot
])

other_tab = html.Div([
    dash_table.DataTable(
        id='info-table',
        # virtualization=True,
        fixed_rows={'headers': False},
        style_table={'overflowX': 'auto',
                     'overflowY': 'auto'},
        style_cell={'textAlign': 'left'},

        page_size=23,

        #sort_action='custom',
        #sort_mode='multi',
        #sort_by=[]
        #columns=[{"name": i, "id": i} for i in trackingdata_df.columns],
    ),
])

graph_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(rose_graph_tab, label="Rose Plots", tab_id="rose-graph-tab"),
                dbc.Tab(other_tab, label="More Information", tab_id="other-graph-tab"),
            ],
            id="graph-tabs",
            active_tab="rose-graph-tab",
        ),
        html.Div(id="content"),
    ]
)

about_offcanvas = dbc.Offcanvas([
    html.H5('Motivation'),
    html.P("Currently, publicly available spatial data is limited to shot coordinate data. "
           "As a result, this application was built in order to analyze hand-tracked pass "
           "coordinate data during assist plays."),
    html.H5('About The Data Source'),
    html.P(["Thanks to Darryl Blackport, the currently available shot tracking data has been made "
            "accessible on his site at ",
            html.A("tracking.pbpstats.com", href="tracking.pbpstats.com"),
            ". This dataset was filtered for all shots that were assisted. "
            "An application was then built to manually track the pass origin "
            "and endpoint by watching film from the Video URL that the dataset pairs each shot with. Please "
            "feel free to read more about the tracking application here, however it is not publicly available. "
            "The manual hand-tracking process was done for 8 players during the 2020-21 season "
            "(Julius Randle, Bam Adebayo, Nikola Jokic, Draymond Green, "
            "LeBron James, LaMelo Ball, Chris Paul, and James Harden), totaling to 2292 manually "
            "tracked data points. "]),
    html.H5('Developed By:'),
    html.P("Lukar Huang (lwhuang@andrew.cmu.edu)"),
],
    id="about-offcanvas",
    title="About this Application",
    className='font-weight-bolder',
    is_open=False,
),

##############################################################################
######################### Interactive Dashboard Page #########################
##############################################################################

dashboard_page = dbc.Container([
    dcc.Store(id='stored-player-data-2', storage_type='session', data=''),
    dcc.Store(id='filtered-player-data-2', storage_type='session', data=''),
    dcc.Store(id='placeholder', storage_type='session', data=''),
    dbc.Offcanvas([
        html.H5('Motivation'),
        html.P("Currently, publicly available spatial data is limited to shot coordinate data. "
               "As a result, this application was built in order to analyze hand-tracked pass "
               "coordinate data during assist plays."),
        html.H5('About The Data Source'),
        html.P(["Thanks to Darryl Blackport, the currently available shot tracking data has been made "
                "accessible on his site at ",
                html.A("tracking.pbpstats.com", href="tracking.pbpstats.com"),
                ". This dataset was filtered for all shots that were assisted. "
                "An application was then built to manually track the pass origin "
                "and endpoint by watching film from the Video URL that the dataset pairs each shot with. Please "
                "feel free to read more about the tracking application here, however it is not publicly available. "
                "The manual hand-tracking process was done for 8 players "
                "(Julius Randle, Bam Adebayo, Nikola Jokic, Draymond Green, "
                "LeBron James, LaMelo Ball, Chris Paul, and James Harden), totaling to 2292 manually "
                "tracked data points. "]),
        html.H5('Developed By:'),
        html.P("Lukar Huang (lwhuang@andrew.cmu.edu)"),
    ],
        id="about-offcanvas",
        title="About this Application",
        className='font-weight-bolder',
        is_open=False,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Video Playback of Chosen Assist",
                                           id='modal-title'
                                           )
                            ),
            html.Center([
                html.Video(
                    id='video-playback-modal',
                    controls=True,
                    src='',
                    loop='loop',
                    autoPlay=False,
                    width='100%',
                    height='100%'
                ),
            ]),
        ],
        id="video-modal",
        size="xl",
        is_open=False,
    ),
    dbc.Row([
        dbc.Col([
            html.H4("Pick A Passer",
                    className='mt-2 text-center',
                    style={'font=size': '14px'}),
            html.Hr(className="my-2"),
            html.Center(
                html.Img(
                    id='player-image',
                    width='60%'),
            ),
            dcc.Dropdown(
                id='tracked-player-select', multi=False, placeholder='Select Player...',
                options=[],
                #options=player_options,
                searchable=True,
                clearable=False,
                value=101108,
                persistence=True,
                className='mb-3'
            ),
            html.H5("Pass Details", className='mt-2 text-center'),
            html.Hr(className="my-2"),
            dcc.RadioItems(
                id='graph-filter',
                options=[
                    {'label': "Pass Origin", 'value': 'pass_'},
                    {'label': "Pass Target", 'value': ''}
                ],
                value='pass_',
                labelStyle={"margin-right": "5px"},
                inputStyle={"margin-right": "5px"},
            ),
            html.P("Date Filter:", className='mt-2 mb-1 text-left font-weight-bolder'),
            dcc.DatePickerRange(
                id='date-filter',
                display_format='MMM Do, Y',
                min_date_allowed=date(2020, 12, 1),
                max_date_allowed=date(2021, 7, 1),
                initial_visible_month=date(2020, 12, 1),
                start_date=date(2020, 12, 1),
                end_date=date(2021, 7, 1),
            ),
            html.P("Shotclock Filter:", className='mt-2 mb-2 text-left font-weight-bolder'),
            dcc.RangeSlider(
                id='shotclock-filter',
                min=0,
                max=24,
                step=1,
                value=[0,24],
                allowCross=False,
                marks={
                    0: '0s',
                    6: '6s',
                    12: '12s',
                    18: '18s',
                    24: '24s',
                },
                #tooltip={'placement': 'top',
                #         'always_visible': True},
                updatemode='drag'
            ),
            html.P("Minute Filter:", className='mt-2 mb-2 text-left font-weight-bolder'),
            dcc.RangeSlider(
                id='time-filter',
                min=0,
                max=720,
                step=1,
                value=[0,720],
                allowCross=False,
                marks={
                    0: '0:00',
                    180: '3:00',
                    360: '6:00',
                    540: '9:00',
                    720: '12:00',
                },
                #tooltip={'placement': 'top',
                #         'always_visible': True},
                updatemode='drag'
            ),
            html.P("Game Detail Filters:", className='mt-2 mb-1 text-left font-weight-bolder'),
            html.Div([
                dbc.DropdownMenu([
                    dcc.Checklist(
                        id='opp-team-filter',
                        value=[],
                        persistence=True,
                        labelStyle={'display': 'block', },
                        inputStyle={"margin-right": "5px", },
                        style={ "overflow-y": "scroll", "height": "200px",
                                "width": "100%"},
                        className='ml-1',
                    ),
                ],
                    id='opp-team-dropdown',
                    direction="up",
                    label="30 of 30 Teams Selected",
                    color="info",
                    className='mb-1',
                    toggle_style={'width': '100%'},
                    style={'width': '100%'}
                )],
                style={'width': '100%'}
            ),
            html.Div([
                dbc.DropdownMenu([
                    dcc.Checklist(
                        id='shottype-filter',
                        options=[
                            {'label': 'Arc 3', 'value': 'Arc3'},
                            {'label': 'Corner 3', 'value': 'Corner3'},
                            {'label': 'Short Midrange', 'value': 'ShortMidRange'},
                            {'label': 'Long Midrange', 'value': 'LongMidRange'},
                            {'label': 'Rim', 'value': 'AtRim'}
                        ],
                        value=['Arc3', 'Corner3', 'ShortMidRange',
                               'LongMidRange','AtRim'],
                        labelStyle={'display': 'block'},
                        inputStyle={"margin-right": "5px"},
                        className='ml-1'
                    ),
                ],
                    id='shottype-dropdown',
                    direction="up",
                    label="All Shot Types Selected",
                    color="info",
                    className='mb-1 mb-1 mw-100',
                    style={'width': '100%'},
                    toggle_style={'width': '100%'}
                )],
            ),
            html.Div([
                dbc.DropdownMenu([
                    dcc.Checklist(
                        id='cs-filter',
                        options=[
                            #{'label': 'Pick and Roll', 'value': 'PR'},
                            #{'label': 'Non-Pick and Roll', 'value': 'NoPR'},
                            {'label': 'Catch and Shoot', 'value': 'CS'},
                            {'label': 'Non-Catch and Shoot', 'value': 'NoCS'},
                            #{'label': 'Wide Open', 'value': 'Wide Open'},
                            #{'label': 'Contested', 'value': 'Contested'},
                        ],
                        value=['CS', 'NoCS',
                               #'Wide Open','Contested'
                               ],
                        labelStyle={'display': 'block'},
                        inputStyle={"margin-right": "5px"},
                        className='ml-1'
                    ),
                ],
                    id='cs-dropdown',
                    direction="up",
                    label='C&S and Non-C&S Shots Selected',
                    color="info",
                    className='mb-1',
                    style={'width': '100%'},
                    toggle_style={'width': '100%'}
                )],
            ),
            html.Div([
                dbc.DropdownMenu([
                    dcc.Checklist(
                        id='hand-filter',
                        options=[
                            {'label': 'Left', 'value': 'Left'},
                            {'label': 'Right', 'value': 'Right'},
                            {'label': 'Two-Handed', 'value': 'Both'},
                        ],
                        value=['Left', 'Right', 'Both'],
                        labelStyle={'display': 'block'},
                        inputStyle={"margin-right": "5px"},
                        className='ml-1',
                    ),
                ],
                    id='hand-dropdown',
                    direction="up",
                    label="All Handed-Passes Selected",
                    color="info",
                    className='mb-1 mw-100',
                    toggle_style={'width': '100%'}
                ),
            ],),
            html.Div([
                dbc.DropdownMenu([
                    dcc.Checklist(
                        id='quarter-filter',
                        options=[
                            {'label': '1st Quarter', 'value': 1},
                            {'label': '2nd Quarter', 'value': 2},
                            {'label': '3rd Quarter', 'value': 3},
                            {'label': '4th Quarter', 'value': 4},
                        ],
                        value=[1,2,3,4],
                        labelStyle={'display': 'block'},
                        inputStyle={"margin-right": "5px"},
                        className='ml-1'
                    ),
                ],
                    id='quarter-dropdown',
                    direction="up",
                    label="All Period Filters Selected",
                    color="info",
                    className='mb-1 d-block',
                    toggle_style={'width': '100%'}
                )],
            ),
            html.Div([
                dbc.DropdownMenu([
                    dcc.Checklist(
                        id='pass-target-filter',
                        options=[],
                        value=[],
                        labelStyle={'display': 'block'},
                        inputStyle={"margin-right": "5px"},
                        style={ "overflow-y": "scroll", "height": "200px"},
                        className='ml-1'
                    ),
                ],
                    id='pass-target-dropdown',
                    direction="up",
                    label="All Pass Targets Selected",
                    color="info",
                    className='mb-1',
                    toggle_style={'width': '100%'},
                )],
            ),
            html.Div([
                dbc.DropdownMenu([
                    dcc.Checklist(
                        id='possession-filter',
                        options=[
                            {'label': 'Off FT Miss', 'value': 'OffFTMiss'},
                            {'label': 'Off FT Make', 'value': 'OffFTMake'},
                            {'label': 'Off Arc3 Miss', 'value': 'OffArc3Miss'},
                            {'label': 'Off Arc3 Make', 'value': 'OffArc3Make'},
                            {'label': 'Off Arc3 Block', 'value': 'OffArc3Block'},
                            {'label': 'Off Corner3 Miss', 'value': 'OffCorner3Miss'},
                            {'label': 'Off Corner3 Make', 'value': 'OffCorner3Make'},
                            {'label': 'Off Corner3 Block', 'value': 'OffCorner3Block'},
                            {'label': 'Off At Rim Miss', 'value': 'OffAtRimMiss'},
                            {'label': 'Off At Rim Make', 'value': 'OffAtRimMake'},
                            {'label': 'Off At Rim Block', 'value': 'OffAtRimBlock'},
                            {'label': 'Off Short Midrange Miss', 'value': 'OffShortMidRangeMiss'},
                            {'label': 'Off Short Midrange Make', 'value': 'OffShortMidRangeMake'},
                            {'label': 'Off Short Midrange Block', 'value': 'OffShortMidRangeBlock'},
                            {'label': 'Off Long Midrange Miss', 'value': 'OffLongMidRangeMiss'},
                            {'label': 'Off Long Midrange Make', 'value': 'OffLongMidRangeMake'},
                            {'label': 'Off Long Midrange Block', 'value': 'OffLongMidRangeBlock'},
                            {'label': 'Off Timeout', 'value': "OffTimeout"},
                            {'label': 'Off Live Ball Turnover', 'value': 'OffLiveBallTurnover'},
                            {'label': 'Off Deadball', 'value': 'OffDeadball'}
                        ],
                        value=['OffFTMiss','OffFTMake','OffArc3Miss','OffArc3Make','OffArc3Block',
                               'OffCorner3Miss','OffCorner3Make','OffCorner3Block',
                               'OffAtRimMiss','OffAtRimMake','OffAtRimBlock',
                               'OffShortMidRangeMiss','OffShortMidRangeMake','OffShortMidRangeBlock',
                               'OffLongMidRangeMiss','OffLongMidRangeMake','OffLongMidRangeBlock',
                               'OffTimeout','OffLiveBallTurnover','OffDeadball'],
                        labelStyle={'display': 'block'},
                        inputStyle={"margin-right": "5px"},
                        style={ "overflow-y": "scroll", "height": "200px"},
                        className='ml-1'
                    ),
                ],
                    id='possession-dropdown',
                    direction="up",
                    label="All Possession-Types Selected",
                    color="info",
                    className='mb-1',
                    toggle_style={'width': '100%'}
                )],
            ),
        ],
            width=2,
            className='ml-0 mr-0',
        ),

        dbc.Col([
            html.Div([
                display_graph,
            ])
        ],
            width=3,
            style={'margin-right': '0px',
                   'margin-left': '0px',
                   'backgroundColor': 'black'},
        ),

        dbc.Col([
            rose_plot,
            hist_plot
        ],
            width=5,
            style={'margin-right': '0px',
                   'margin-left': '0px',
                   'backgroundColor': 'black'},
        ),

        dbc.Col([
            html.H5("How do I interpret these visuals?",
                    className='mt-2 text-center text-white'),
            html.Hr(className="my-2",
                    style={'color': 'white'}),
            html.P(
                "The Assist Rose Plots express directional passing tendencies "
                "on assist plays with the frame of reference being the hoop due South. "
                "Every assist is associated with a vector that indicates where "
                "the pass was thrown initially and caught. All the vectors are then "
                "centered at an origin and a rose plot is then generated.",
                className='text-white'
            ),
            html.P(
                "This unfortunately leaves out a ton of other information such as "
                "court location of the pass, while also excluding passes that "
                "do not directly result in assists. It also assumes the player "
                "is facing the basket at all times which is not particularly always true. However, this "
                "paints a good general representation of a player's passing habits "
                "and court vision with the very little data I was able to manually track. "
                "Furthermore, please feel free to click on any point on the graph "
                "for a Circular KDE of passing tendencies at that particular spot on the floor.",
                className='text-white'
            ),
            html.Hr(className="my-2",
                    style={'color': 'white'}),
            html.P(
                "Graph Options",
                className='text-center text-white'
            ),
            daq.ToggleSwitch(id='graph-toggle',
                             label='Rose Plot by Pass Distance',
                             labelPosition='top',
                             className='text-white mb-2',
                             ),
            daq.BooleanSwitch(id='tooltips-toggle', on=True,
                              label='Tooltips are On',
                              labelPosition='top',
                              className='mb-2 text-white',
                              color='green',
                              ),
            html.Hr(className="my-2",
                    style={'color': 'white'}),
            dbc.Button("Show Video of Play",
                       id='open-modal-btn',
                       style={'width': '100%'},
                       ),
            dbc.Tooltip(
                "Click on a Scatter Point on the Court to view video of the play. ",
                target="open-modal-btn",
                placement="top"
            ),
            html.Hr(className="my-2",
                    style={'color': 'white'}),
        ],
            width=2,
            style={'margin-right': '0px',
                   'margin-left': '0px',
                   'backgroundColor': 'black'},
        ),
    ]),
], fluid=True)

##############################################################################
################################# App Layout #################################
##############################################################################

navigation_bar = html.Div(
    dbc.NavbarSimple([
        dbc.Button("About This App", id="open-offcanvas", n_clicks=0),
        dbc.NavLink("Interactive Dashboard", href="/home", active='exact',
                    ),
    ],
        dark=True,
        color='primary',
        brand='Tracking Plays App',
        brand_href='#',
        className='py-lg-0',
    )
)

content = html.Div(id='page-content', children=[dashboard_page])

tracking_columns = ['pass_x', 'pass_y', 'pass_rec_x', 'pass_rec_y',
                    'pass_shotclock', 'catch_and_shoot', 'pick_and_roll',
                    'handedness', 'courtside', 'pass_distance',
                    'pass_angle','pass_shot_distance','direction',
                    'pass_dist_range', 'num_dribbles', 'row_id']

app.layout = html.Div([
    dcc.Store(id='processed-distance-data', storage_type='session', data=''),
    dcc.Store(id='processed-shottype-data', storage_type='session', data=''),
    dcc.Store(id='stored-player-data', storage_type='session', data=''),
    dcc.Store(id='distances_df_template', storage_type='session',
              data=pd.DataFrame(product(directions, distances, [0]),
                                columns=['Direction','Pass Distance','Frequency']).to_dict('records')),
    dcc.Store(id='shottypes_df_template', storage_type='session',
              data=pd.DataFrame(product(directions, shottypes, [0]),
                                columns=['Direction','Shot Type','Frequency']).to_dict('records')),
    dcc.Store(id='row-id', storage_type='session', data=0),
    dcc.Store(id='tracked-cols', storage_type='session', data=['pass_x', 'pass_y', 'pass_rec_x', 'pass_rec_y',
                                                               'pass_shotclock', 'catch_and_shoot', 'pick_and_roll',
                                                               'handedness', 'pass_distance',
                                                               'pass_angle','pass_shot_distance','direction',
                                                               'pass_dist_range', 'num_dribbles', 'row_id']),

    dcc.Store(id='player-options', storage_type='session', data=[]),
    dcc.Store(id='team-options', storage_type='session', data=[]),
    dcc.Store(id='tracked-player-options', storage_type='session', data=[]),
    dcc.Location(id='url', pathname='/home'),
    navigation_bar,
    content])

##############################################################################
############################### App Callbacks ################################
##############################################################################

@app.callback(
    Output(component_id="about-offcanvas", component_property="is_open"),
    Input(component_id="open-offcanvas", component_property="n_clicks"),
    State(component_id="about-offcanvas", component_property="is_open"),
)
def toggle_offcanvas(n1, is_open):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'open-offcanvas' in changed_id:
        return not is_open
    return is_open

@app.callback(
    Output(component_id="page-content", component_property="children"),
    Input(component_id="url", component_property="pathname"),
)
def render_page_content(pathname, ):
    print('-----------------')
    print('rendering page...')
    if pathname == '/home':
        return dashboard_page
    else:
        return html.Div(
            dbc.Container(
                [
                    html.H1("404: Not found", className="text-danger"),
                    html.Hr(),
                    html.P(f"The pathname {pathname} was not recognised..."),
                ],
                fluid=True,
                className="py-3",
            ),
            className="p-3 bg-light rounded-3",
        )
    return dash.no_update

@app.callback(
    Output(component_id='video-modal', component_property='is_open'),
    Input(component_id='open-modal-btn', component_property='n_clicks'),
    State(component_id='video-modal', component_property='is_open'),
    State(component_id='video-playback-modal', component_property='src')
)
def open_video_modal(btn, is_open, link):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'open-modal-btn' in changed_id and link != '':
        return not is_open
    return is_open

@app.callback(
    Output(component_id='tooltips-toggle', component_property='label'),
    Input(component_id='tooltips-toggle', component_property='on')
)
def update_track_toggle_info(tooltips_toggle):
    print('toolstips toggle detected...')
    return 'Tooltips are On' if tooltips_toggle else 'Tooltips are Off'

@app.callback(
    Output(component_id='graph-toggle', component_property='label'),
    Input(component_id='graph-toggle', component_property='value'),
)
def update_input_toggle_info(graph_toggle):
    print('graph toggle detected...')
    return 'Rose Plot by Pass Distance' if not graph_toggle else 'Rose Plot by Shot Type Created'

@app.callback(
    Output(component_id='stored-player-data-2', component_property='data'),
    Input(component_id='tracked-player-select', component_property='value')
)
def update_player_data2(pid):
    print('-------------------------------------')
    print('updating stored-player-data-2', pid)
    player_df = tracked_df[tracked_df['assistplayerid'] == pid]
    print('finished updating stored-player-data-2')
    return player_df.to_dict('records')

@app.callback(
    Output(component_id='processed-distance-data', component_property='data'),
    Output(component_id='processed-shottype-data', component_property='data'),
    Input(component_id='filtered-player-data-2', component_property='data'),
    State(component_id='distances_df_template', component_property='data'),
    State(component_id='shottypes_df_template', component_property='data'),
)
def process_tracking_data(data, dist_template, shot_template):
    distances_df, shottypes_df = pd.DataFrame(dist_template), pd.DataFrame(shot_template)
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if changed_id.split('.')[0] in ['filtered-player-data-2'] and data != []:
        player_df = pd.DataFrame(data)
        print('2. start processing', changed_id)
        distcounts_df = player_df.groupby(['direction', 'pass_dist_range']).size().reset_index()
        distcounts_df = distcounts_df.rename({
            'direction': 'Direction', 'pass_dist_range': 'Pass Distance', 0: 'Frequency 2'
        }, axis=1)
        shotcounts_df = player_df.groupby(['direction', 'shottype']).size().reset_index()
        shotcounts_df = shotcounts_df.rename({
            'direction': 'Direction', 'shottype': 'Shot Type', 0: 'Frequency 2'
        }, axis=1)
        distances_df = distances_df.merge(distcounts_df, on=['Direction', 'Pass Distance',], how='left')
        distances_df['Frequency'] = np.max(distances_df[['Frequency', 'Frequency 2']], axis=1)
        distances_df = distances_df.drop(columns=['Frequency 2'])
        shottypes_df = shottypes_df.merge(shotcounts_df, on=['Direction', 'Shot Type'], how='left')
        shottypes_df['Frequency'] = np.max(shottypes_df[['Frequency', 'Frequency 2']], axis=1)
        shottypes_df = shottypes_df.drop(columns=['Frequency 2'])
        print('2.  finished processing')
        return distances_df.to_dict('records'), shottypes_df.to_dict('records')
    return distances_df.to_dict('records'), shottypes_df.to_dict('records')

@app.callback(
    Output(component_id='rose-plot', component_property='figure'),
    Input(component_id='processed-distance-data', component_property='data'),
    Input(component_id='processed-shottype-data', component_property='data'),
    Input(component_id='graph-toggle', component_property='value'),
    State(component_id='filtered-player-data-2', component_property='data')
)
def update_rose_plot(distance_data, shottype_data, graph_toggle, f_data):
    print('starting to update dist plot', [p['prop_id'] for p in callback_context.triggered][0])
    data = distance_data if not graph_toggle else shottype_data
    if f_data != []:
        distances_colors = ['#67001f','#bb2a34','#e58368','#fbceb6','#f7f7f7',
                            '#c1ddec','#6bacd1','#2a71b2','#053061']
        shottype_colors = ['#b7e2ab','#6fc9a3','#46879c','#3e5590','#2c2037']
        new_fig = px.bar_polar(pd.DataFrame(data), r="Frequency", theta="Direction",
                               color='Pass Distance' if not graph_toggle else 'Shot Type',
                               template="plotly_dark",
                               color_discrete_sequence=distances_colors if not graph_toggle else shottype_colors,
                               title="Passing Tendencies on Assists by %s" % ('Pass Distance' if not graph_toggle else 'Shot Type'),
                               )
        new_fig.update_layout(legend_title_text='Pass Distance Range' if not graph_toggle else 'Shot Type Created',
                              )
        print('finished updating dist plot')
        return new_fig
    return px.bar_polar(template="plotly_dark",
                        title='No Data To Display! Please double check your filters again!')

@app.callback(
    Output(component_id='hist-plot', component_property='figure'),
    Input(component_id='graph-toggle', component_property='value'),
    Input(component_id='filtered-player-data-2', component_property='data'),
)
def update_histogram(graph_toggle, data):
    print('starting to update hist plot')
    if data != []:
        df = pd.DataFrame(data)
        new_fig = px.histogram(df, x='pass_shotclock',
                               color='pass_dist_range' if not graph_toggle else 'shottype',
                               template="plotly_dark",
                               range_x=[df['pass_shotclock'].min(), df['pass_shotclock'].max()],
                               color_discrete_map={'AtRim': '#b7e2ab',
                                                   'ShortMidRange': '#6fc9a3',
                                                   'LongMidRange': '#46879c',
                                                   'Arc3': '#3e5590',
                                                   'Corner3': '#2c2037',
                                                   '0-10 ft.': '#67001f',
                                                   '10-20 ft.': '#bb2a34',
                                                   '20-30 ft.': '#e58368',
                                                   '30-40 ft.': '#fbceb6',
                                                   '40-50 ft.': '#f7f7f7',
                                                   '50-60 ft.': '#c1ddec',
                                                   '60-70 ft.': '#6bacd1',
                                                   '70-80 ft.': '#2a71b2',
                                                   '80-90 ft.': '#053061',
                                                   },
                               category_orders={'shottype': [
                                   'AtRim',
                                   'ShortMidRange',
                                   'LongMidRange',
                                   'Arc3',
                                   'Corner3'],
                                   'pass_dist_range': [
                                       '0-10 ft.',
                                       '10-20 ft.',
                                       '20-30 ft.',
                                       '30-40 ft.',
                                       '40-50 ft.',
                                       '50-60 ft.',
                                       '60-70 ft.',
                                       '70-80 ft.',
                                       '80-90 ft.',
                                   ]
                               },
                               labels={'pass_shotclock': 'Time Left On Shotclock when Pass is Thrown',
                                       'shottype': 'Shot Type Created',
                                       },
                               title="Assist Distribution by Time Left on Shotclock when Pass is Thrown",
                               nbins=len([x for x in range(df['pass_shotclock'].min(), df['pass_shotclock'].max()+1)])
                               )
        new_fig.update_layout(yaxis_title='Frequency',
                              legend_title_text='Pass Distance Range' if not graph_toggle else 'Shot Type Created',
                              )
        print('finished updating hist plot')
        return new_fig
    return px.histogram(template="plotly_dark",
                        title='No Data To Display! Please double check your filters again!')

@app.callback(
    Output(component_id='player-image', component_property='src'),
    Input(component_id='tracked-player-select', component_property='value')
)
def update_image(pid):
    return 'https://cdn.nba.com/headshots/nba/latest/1040x760/%d.png' % pid

@app.callback(
    Output(component_id='player-options', component_property='data'),
    Output(component_id='team-options', component_property='data'),
    Output(component_id='tracked-player-options', component_property='data'),
    Input(component_id='player-options', component_property='data'),
)
def get_player_and_team_options(data):
    print('updating team and player options...')
    allids_df = main_df[['assistplayerid', 'assist_player', 'offense_team_id',
                                              'team', 'pass_x']]
    pids_df = pd.DataFrame(allids_df.groupby(['assistplayerid', 'assist_player']).size(
    ).reset_index().rename(columns={0: 'count',
                                    'assist_player': 'label',
                                    'assistplayerid': 'value'}))

    pids_df = pids_df[['label', 'value']].sort_values('label').reset_index(drop=True)
    player_options = pids_df.to_dict('records')

    teamids_df = pd.DataFrame(allids_df.groupby(['offense_team_id', 'team']).size(
    ).reset_index().rename(columns={0: 'count',
                                    'team': 'label',
                                    'offense_team_id': 'value'}))

    teamids_df = teamids_df[['label', 'value']].sort_values('label').reset_index(drop=True)
    team_options = teamids_df.to_dict('records')

    tracked_pids_df = pd.DataFrame(allids_df[~allids_df['pass_x'].isnull()].groupby(['assistplayerid', 'assist_player']).size(
    ).reset_index().rename(columns={0: 'count',
                                    'assist_player': 'label',
                                    'assistplayerid': 'value'}))
    tracked_pids_df = tracked_pids_df[['label', 'value']].sort_values('label').reset_index(drop=True)
    tracked_player_options = tracked_pids_df.to_dict('records')

    return player_options, team_options, tracked_player_options

@app.callback(
    Output(component_id='opp-team-filter', component_property='options'),
    Output(component_id='opp-team-filter', component_property='value'),
    Input(component_id='team-options', component_property='data'),
)
def update_teamselect_options(team_options, ):
    print('triggered team-select',[p['prop_id'] for p in callback_context.triggered], len(team_options))
    return team_options, [team['value'] for team in team_options]

@app.callback(
    Output(component_id='tracked-player-select', component_property='options'),
    Input(component_id='tracked-player-options', component_property='data'),
)
def update_pselect2_options(tracked_player_options, ):
    print('trigger pselect2',[p['prop_id'] for p in callback_context.triggered][0], )
    return tracked_player_options

@app.callback(
    Output(component_id='pass-target-filter', component_property='options'),
    Output(component_id='pass-target-filter', component_property='value'),
    Input(component_id='stored-player-data-2', component_property='data'),
)
def update_target_filter(data, ):
    print('updating targets...', [p['prop_id'] for p in callback_context.triggered][0])
    targets_df = pd.DataFrame(pd.DataFrame(data).groupby(['playerid', 'player']).size(
    ).reset_index().rename(columns={0: 'count',
                                    'player': 'label',
                                    'playerid': 'value'}))
    targets_df = targets_df[['label', 'value']].sort_values('label').reset_index(drop=True)
    target_options = targets_df.to_dict('records')
    print('finished updating target options',)
    return target_options, [player['value'] for player in target_options]


@app.callback(
    Output(component_id='display-graph', component_property='figure'),
    Input(component_id='filtered-player-data-2', component_property='data'),
    Input(component_id='graph-filter', component_property='value'),
    Input(component_id='display-graph', component_property='clickData'),
    Input(component_id='tooltips-toggle', component_property='on')
)
def update_display_graph(data, graph_type, clickData, tooltips_ison):
    def calc_vector_pts(x1, x2, y1, y2):
        m = (y2 - y1) / (x2 - x1)
        b = y1 - (m*x1)
        x = np.linspace(x1, x2, 250)
        y = m*x + b
        return x, y
    def vonmises_kde(data, kappa, n_bins=100):
        print('starting')
        from scipy.special import i0
        bins = np.linspace(-np.pi, np.pi, n_bins)
        x = np.linspace(-np.pi, np.pi, n_bins)
        # integrate vonmises kernels
        kde = np.exp(kappa*np.cos(x[:, None]-data[None, :])).sum(1)/(2*np.pi*i0(kappa))
        kde /= np.trapz(kde, x=bins)
        print('returned')
        return bins, kde
    def circle(r0, theta0, rho, degrees = True):
        ##https://community.plotly.com/t/shapes-on-a-polar-plot-is-it-posible/29155/2
        from numpy import pi, sin, cos, sqrt, arctan2
        # compute the polar coordinates for 100 points on a circle of center (r0, theta0) and radius rho
        if degrees:
            theta0 = theta0 * pi / 180
        phi = np.linspace(0, 2*pi, 100)
        x = rho * cos(phi) + r0 * cos(theta0)
        y = rho * sin(phi) + r0 * sin(theta0)
        r = sqrt(x**2 + y**2)

        J = np.where(y<0)
        theta = arctan2(y, x)
        theta[J] = theta[J] + 2*pi
        return (r, theta * 180 / pi) if degrees else (r, theta)
    if data != []:
        df = pd.DataFrame(data)
        display_fig.data = [] ##display_fig
        #fig['data'] = [] ##display_fig
        display_fig.add_trace(go.Histogram2dContour( ##
            x=df['%sx' % graph_type].to_list(),
            y=df['%sy' % graph_type].to_list(),
            colorscale='Inferno',
            xaxis='x2',
            yaxis='y2',
            showscale=False,
            line=dict(width=0),
            hoverinfo='none'
        ))
        display_fig.add_trace(go.Scatter( ##
            x=df['%sx' % graph_type].to_list(),
            y=df['%sy' % graph_type].to_list(),
            xaxis='x2',
            yaxis='y2',
            mode='markers',
            marker=dict(
                color='white',
                size=2
            ),
            name='Pass Origin' if graph_type == 'pass_' else 'Pass Target',
            hoverinfo='none',
        ))
        new_customdatadf = np.stack((df['shottype'], df['player'],
                                     df['period'], df['time'], df['date'],
                                     df['possession_start_type'], df['pass_distance'],
                                     df['pass_x'], df['pass_y'],
                                     df['pass_rec_x'], df['pass_rec_y'],
                                     df['assist_player'], df['team'],
                                     df['opponent'], df['video_url'],
                                     ), axis=-1)
        #https://chart-studio.plotly.com/~empet/15366/customdata-for-a-few-plotly-chart-types/#/#
        display_fig.update_traces(customdata=new_customdatadf, ##
                                  selector=dict(type='scatter'),
                                  hovertemplate="<b>Date:</b> %{customdata[4]}<br>" +
                                                "<b>Time:</b> Q%{customdata[2]} | %{customdata[3]} left in the Quarter<br>"+
                                                "<b>Player Assisted:</b> %{customdata[1]}<br>" +
                                                "<b>Shot Type Created:</b> %{customdata[0]}<br>" +
                                                "<b>Pass Distance:</b> %{customdata[6]} ft.<br>" +
                                                "<b>Possession Start Type:</b> %{customdata[5]}<br>" if tooltips_ison else None
                                      )
        try:
            print('testing for kde')
            if 'pointNumber' in clickData['points'][0].keys():
                print('attempting kde...')
                df = pd.DataFrame(data)
                r, ref_x, ref_y = 35, clickData['points'][0]['customdata'][-5], clickData['points'][0]['customdata'][-4]
                df['within_dist'] = df.apply(lambda x: True if (np.sqrt((ref_x - x['pass_x'])**2 + (ref_y - x['pass_y'])**2) <= r) else False, axis=1)
                df['pass_angle'] = df['pass_angle'] * (math.pi/180)
                filtered_df = df[df['within_dist'] == True]
                bins, kde = vonmises_kde(np.array(filtered_df['pass_angle'].to_list()), kappa=10, n_bins=1000)
                x = [ref_x + (r*100)*math.cos(theta) for r, theta in zip(kde, bins)]
                y = [ref_y + (r*100)*math.sin(theta) for r, theta in zip(kde, bins)]
                r, theta = circle(0, 0, .1)
                print('adding kde')
                display_fig.add_trace(go.Scatter( ##
                    x=x,
                    y=y,
                    xaxis='x2',
                    yaxis='y2',
                    mode='markers',
                    marker=dict(
                        color='white',
                        size=2
                    ),
                    name='kde'
                ))
                print('finished creating it')
            return display_fig ##
        except:
            return display_fig ##
    court_fig = go.Figure()
    draw_plotly_court(court_fig, show_title=False, labelticks=False, show_axis=False,
                      glayer='above', bg_color='black', margins=0)
    print('retrurned court_fig')
    return court_fig

@app.callback(
    Output(component_id='video-playback-modal', component_property='src'),
    Output(component_id='modal-title', component_property='children'),
    Input(component_id='display-graph', component_property='clickData')
)
def update_video_modal(clickData):
    print('update modal')
    if clickData:
        try:
            print('getting link')
            link = clickData['points'][0]['customdata'][-1]
            player = clickData['points'][0]['customdata'][1]
            assist_player = clickData['points'][0]['customdata'][-4]
            date = clickData['points'][0]['customdata'][4]
            print('got date', date)
            date = datetime.fromisoformat(date).strftime('%b %d, %Y')
            print('reformatted date!')
            opp = clickData['points'][0]['customdata'][-2]
            team = clickData['points'][0]['customdata'][-3]
            title = "%s's assist to %s (%s vs. %s on %s)" % (assist_player, player, team, opp, date)#[:10])
            print('got data')
            return link, title
        except:
            return dash.no_update, dash.no_update
    return dash.no_update, dash.no_update

@app.callback(
    Output(component_id='filtered-player-data-2', component_property='data'),
    Input(component_id='shotclock-filter', component_property='value'),
    Input(component_id='time-filter', component_property='value'),
    Input(component_id='hand-filter', component_property='value'),
    Input(component_id='pass-target-filter', component_property='value'),
    Input(component_id='shottype-filter', component_property='value'),
    Input(component_id='opp-team-filter', component_property='value'),
    Input(component_id='cs-filter', component_property='value'),
    Input(component_id='quarter-filter', component_property='value'),
    Input(component_id='possession-filter', component_property='value'),
    Input(component_id='date-filter', component_property='start_date'),
    Input(component_id='date-filter', component_property='end_date'),
    State(component_id='stored-player-data-2', component_property='data'),
    prevent_initial_callback=True
)
def filter_player_data(shotclock_filter, minute_filter, hand_filter, target_filter,
                       shottype_filter, opp_team_filter, extra_filter, period_filter,
                       possession_filter, start_date, end_date, data):
    print('1. starting to filter', start_date, end_date, type(start_date), type(end_date))
    player_df = pd.DataFrame(data)
    player_df['date'] = pd.to_datetime(player_df['date'])
    player_df = player_df[(player_df['date'] > start_date) & (player_df['date'] <= end_date)]
    player_df['time'] = player_df['time'].str.split(':').apply(lambda x: int(x[0]) * 60 + int(x[1]))
    filtered_df = player_df[player_df['pass_shotclock'].between(shotclock_filter[0], shotclock_filter[1], inclusive='both')]
    filtered_df = filtered_df[filtered_df['time'].between(minute_filter[0], minute_filter[1], inclusive='both')]
    filtered_df['time'] = pd.to_datetime(filtered_df["time"], unit='s').dt.strftime("%M:%S")
    filtered_df = filtered_df[filtered_df['playerid'].isin(target_filter)]
    filtered_df = filtered_df[filtered_df['shottype'].isin(shottype_filter)]
    filtered_df = filtered_df[filtered_df['defense_team_id'].isin(opp_team_filter)]
    filtered_df = filtered_df[filtered_df['period'].isin(period_filter)]
    filtered_df = filtered_df[filtered_df['possession_start_type'].isin(possession_filter)]
    cs_filter = [x for x in extra_filter if 'CS' in x]
    cs_filter = list(map(lambda x: 'False' if 'No' in x else 'True', cs_filter))
    filtered_df['catch_and_shoot'] = filtered_df['catch_and_shoot'].astype('str')
    filtered_df = filtered_df[filtered_df['catch_and_shoot'].isin(cs_filter)]
    print('1. finishing filtering', filtered_df.shape)
    return filtered_df.reset_index(drop=True).to_dict('records')

@app.callback(
    Output(component_id='opp-team-dropdown', component_property='label'),
    Input(component_id='opp-team-filter', component_property='value'),
)
def update_team_dropdown_label(opp_team_filter):
    return '%d of 30 Teams Selected' % len(opp_team_filter)

@app.callback(
    Output(component_id='hand-dropdown', component_property='label'),
    Input(component_id='hand-filter', component_property='value')
)
def update_hand_dropdown_label(hand_filter):
    if len(hand_filter) == 3:
        return 'All Handed-Passes Selected'
    elif len(hand_filter) == 2:
        return '%s and %s Handed-Passes Selected' % (hand_filter[0], hand_filter[1])
    else:
        return '%s Handed-Passes Selected' % hand_filter[0]

@app.callback(
    Output(component_id='shottype-dropdown', component_property='label'),
    Input(component_id='shottype-filter', component_property='value')
)
def update_shottype_dropdown(shottype_filter):
    if len(shottype_filter) == 5:
        return 'All Shot Types Selected'
    else:
        return '%d of 5 Shot Types Selected' % len(shottype_filter)

@app.callback(
    Output(component_id='pass-target-dropdown', component_property='label'),
    Input(component_id='pass-target-filter', component_property='value'),
    Input(component_id='pass-target-filter', component_property='options')
)
def update_pass_target_dropdown_label(pass_target_filter, target_options):
    return '%d of %d Pass Targets Selected' % (len(pass_target_filter), len(target_options))

@app.callback(
    Output(component_id='quarter-dropdown', component_property='label'),
    Input(component_id='quarter-filter', component_property='value'),
)
def update_period_dropdown_label(period_filter):
    period_filter.sort()
    if len(period_filter) == 4:
        return 'All Quarters Filters Selected'
    elif len(period_filter) == 3:
        return 'Quarter %d, %d, and %d Selected' % (period_filter[0], period_filter[1], period_filter[2])
    elif len(period_filter) == 2:
        return 'Quarter %d and %d Selected' % (period_filter[0], period_filter[1])
    elif len(period_filter) == 1:
        return 'Quarter %d Selected' % period_filter[0]
    else:
        return "No Quarters Selected"

@app.callback(
    Output(component_id='possession-dropdown', component_property='label'),
    Input(component_id='possession-filter', component_property='value'),
)
def update_possession_dropdown_label(possession_filter):
    return "%d of 20 Possession Types Selected" % len(possession_filter)

@app.callback(
    Output(component_id='cs-dropdown', component_property='label'),
    Input(component_id='cs-filter', component_property='value')
)
def update_cs_dropdown_label(cs_filter):
    if len(cs_filter) == 2:
        return 'C&S and Non-C&S Shots Selected'
    elif cs_filter[0] == 'CS':
        return 'Catch-and-Shoot Shots Selected'
    else:
        return 'Non-Catch-and-Shoot Shots Selected'

if __name__ == '__main__':
    app.run_server(debug=True)
