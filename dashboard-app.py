# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_auth

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
from itertools import product

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# import dependencies
# manage database and users
import sqlite3
from sqlalchemy import Table, create_engine
from sqlalchemy.sql import select
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin
# manage password hashing
from werkzeug.security import generate_password_hash, check_password_hash
# use to config server
import warnings
import configparser
import os

import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

##############################################################################
###################### Create Processed Data Template ########################
##############################################################################

distances = ['0-10 ft.', '10-20 ft.', '20-30 ft.', '30-40 ft.',
             '40-50 ft.', '50-60 ft.', '60-70 ft.', '70-80 ft.', '80-90 ft.']
shottypes = ['AtRim', 'ShortMidRange', 'LongMidRange',
             'Arc3', 'Corner3']
directions = ['N', 'NEN', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SES',
              'S', 'SWS', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NWN']

##############################################################################
##############################################################################
##############################################################################

# instantiate dash app
# server = Flask(__name__)
app = dash.Dash(__name__,  # server=server,
                external_stylesheets=[dbc.themes.FLATLY],
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                )

server = app.server
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app.server)
con = db.engine.connect()

warnings.filterwarnings("ignore")
conn = sqlite3.connect('data.sqlite')
engine = create_engine('sqlite:///data.sqlite')
config = configparser.ConfigParser()

engine_two = create_engine(
    'postgresql://gndqnrtidbgilj:67b080bd60767b2ed2ed78d0a9b6d8fc10200abb2bc5a43678e35b9544a68b8b@ec2-52-86-177-34.compute-1.amazonaws.com:5432/d8g5e9bldijo6')


# create users class for interacting with users table
class Users(db.Model):
    # __tablename__ = 'users',
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean, nullable=False)
Users_tbl = Table('users', Users.metadata)

class TrackingData(db.Model):
    __tablename__ = 'nbatrackingdata',
    __bind_key__ = 'nbatrackingdb',
    game_id = db.Column(db.Integer)
    period = db.Column(db.Integer)
    possessionnumber = db.Column(db.Integer)
    eventnum = db.Column(db.Integer)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    value = db.Column(db.Integer)
    playerid = db.Column(db.Integer)
    made = db.Column(db.Integer)
    time = db.Column(db.String(5))
    margin = db.Column(db.Integer)
    blocked = db.Column(db.Integer)
    blockplayerid = db.Column(db.Integer)
    assisted = db.Column(db.Integer)
    assistplayerid = db.Column(db.Integer)
    putback = db.Column(db.Integer)
    shottype = db.Column(db.String(13))
    oreboundedshoteventnum = db.Column(db.Integer)
    oreboundedrebeventnum = db.Column(db.Integer)
    lineupid = db.Column(db.Integer)
    opplineupid = db.Column(db.Integer)
    and1 = db.Column(db.Integer)
    offense_team_id = db.Column(db.Integer)
    defense_team_id = db.Column(db.Integer)
    possession_start_type = db.Column(db.String(20))
    possession_start_time = db.Column(db.Integer)
    closest_def_dist = db.Column(db.String(25))
    shot_clock = db.Column(db.String(25))
    touch_time = db.Column(db.String(25))
    dribble_range = db.Column(db.String(25))
    video_url = db.Column(db.String(1000))
    player = db.Column(db.String(100))
    date = db.Column(db.String(10))
    team = db.Column(db.String(3))
    opponent = db.Column(db.String(3))
    assist_player = db.Column(db.String(100))
    block_player = db.Column(db.String(100))
    pass_x = db.Column(db.Integer)
    pass_y = db.Column(db.Integer)
    pass_rec_x = db.Column(db.Integer)
    pass_rec_y = db.Column(db.Integer)
    pass_shotclock = db.Column(db.Integer)
    catch_and_shoot = db.Column(db.Boolean)
    pick_and_roll = db.Column(db.Boolean)
    handedness = db.Column(db.Integer)
    courtside = db.Column(db.Integer)
    pass_distance = db.Column(db.Float)
    pass_angle = db.Column(db.Float)
    pass_shot_distance = db.Column(db.Float)
    direction = db.Column(db.String(4))
    pass_dist_range = db.Column(db.String(12))
    num_dribbles = db.Column(db.Integer)
    row_id = db.Column(db.Integer, primary_key=True)
Tracking_tbl = Table('nbatrackingdata', TrackingData.metadata)

server.config.update(
    SECRET_KEY=os.environ['SECRET_KEY'],
    #SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI='sqlite:///data.sqlite',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_BINDS={
        'nbatrackingdb': 'postgresql://gndqnrtidbgilj:67b080bd60767b2ed2ed78d0a9b6d8fc10200abb2bc5a43678e35b9544a68b8b@ec2-52-86-177-34.compute-1.amazonaws.com:5432/d8g5e9bldijo6',
    }
)

db.init_app(server)

# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


# User as base

# Create User class with UserMixin
class Users(UserMixin, Users):
    pass

home = dbc.Container([
    html.H1('About this App', className='mt-3'),
    html.Hr(className="my-2"),
    html.H5('Motivation'),
    html.P("Currently, publicly available spatial data is limited to shot coordinate data. "
           "As a result, this application was built in order to analyze hand-tracked pass "
           "coordinate data during assist plays and grant the general public with "
           "insights they may have never seen before. A prior version of this application "
           "was also presented to former Milwaukee Bucks Analytics Manager Ashley Brio and "
           "it received positive feedback."),
    html.H5('About The Data Source'),
    html.P(["Thanks to Darryl Blackport, the currently available shot tracking data has been made "
            "accessible on his site at ",
            html.A("tracking.pbpstats.com", href="tracking.pbpstats.com"),
            ". That dataset was then filtered for all assisted shots. "
            "I then built this application to manually track the pass origin "
            "and endpoint by watching film from the Video URL that the dataset pairs each shot with. Please "
            "feel free to read more about the tracking application and process by clicking here "
            "since that feature is not publicly available. "
            "The manual hand-tracking process was done for 8 players during the 2020-21 season "
            "(Julius Randle, Bam Adebayo, Nikola Jokic, Draymond Green, "
            "LeBron James, LaMelo Ball, Chris Paul, and James Harden), totaling to 2292 manually "
            "tracked data points. "]),
    html.H5('Will more shots be manually tracked?'),
    html.P("More assisted shots will be manually hand-tracked for the 2021-22 season and possibly previous "
           "seasons as well. "
           ),
    html.H5('Implications'),
    html.P("This tracking application, which is not available to the public, can be custom-built "
           "for other features to be hand-tracked as well that may not be recorded via Second Spectrum. "
           "If you have any ideas or suggestions, please feel free to reach out to me via email."
           ),
    html.H5('Future Additions'),
    html.P("Please be on the lookout for updates to this app for more fun data!"
           ),
    html.H5('Developed By:'),
    html.P("Lukar Huang (lwhuang@andrew.cmu.edu)"),
])

login = dbc.Container(
    dbc.Row([
        dbc.Col([
            html.Div()
        ],
            width={'size': 4},
            className='ml-0 mr-0',
        ),
        dbc.Col([
            html.Center([
                html.H3('Please log in to continue', id='h1', className='text-center'),
                html.Hr(className="my-2"),
                html.Div(
                    [
                        dbc.Label("Username", html_for="username"),
                        dbc.Input(type="text", id="uname-box",
                                  placeholder="Enter username", value='GuestUser'),
                        dbc.FormText(
                            "Please enter the username you were provided with to login.",
                            color="secondary",
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Label("Password", html_for="password"),
                        dbc.Input(type="password", id="pwd-box",
                                  placeholder="Enter password", value='freeaccess'),
                        dbc.FormText(
                            "Please enter the password associated with your account.", color="secondary"
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.Button('Login',
                           type='submit',
                           id='login-btn',
                           ),
                html.Div(children='', id='output-state'),
                dbc.Alert(
                    "Incorrect Username or Password! Please try again!",
                    id='login-alert',
                    color="danger",
                    duration=2500,
                    is_open=False,
                    dismissable=True,
                    className='mt-3'
                )
            ]),
        ],
            width={'size': 4},
            align='center',
            className='ml-0 mr-0 py-5 d-inline-block',
        ),
        dbc.Col([
            html.Div()
        ],
            width={'size': 4},
            className='ml-0 mr-0',
        ),
    ],
        align='center',
    ),
    className='pad-row'
)

create = dbc.Container(
    dbc.Row([
        dbc.Col([
            html.Div()
        ],
            width={'size': 4},
            className='ml-0 mr-0',
        ),
        dbc.Col([
            html.Center([
                html.H2('Create User Account', id='h2', className='text-center'),
                html.Div(
                    [
                        dbc.Label("Username", html_for="username"),
                        dbc.Input(type="text", id="username", placeholder="Enter username"),
                        dbc.FormText(
                            "Give me a username bruh",
                            color="secondary",
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Label("Password", html_for="password"),
                        dbc.Input(type="password", id="password", placeholder="Enter password",
                                  ),
                        dbc.FormText(
                            "A password stops mean people taking your stuff", color="secondary"
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Label("Re-enter Password", html_for="password"),
                        dbc.Input(type="password", id="password-confirm", placeholder="Re-enter password",
                                  ),
                        dbc.FormText(
                            "Just double checking you know your password", color="secondary"
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Label("Email", html_for="email"),
                        dbc.Input(type="email", id="email", placeholder="Enter email",
                                  ),
                        dbc.FormText(
                            "Just casually taking your email too", color="secondary"
                        ),
                    ],
                    className="mb-3",
                ),
                daq.BooleanSwitch(
                    id='admin-access',
                    on=False,
                    label="Admin Access?",
                    labelPosition="top",
                    className='mb-2'
                ),
                dbc.Button('Create User',
                           n_clicks=0,
                           type='submit',
                           id='create-user-btn'),
                dbc.Alert(
                    'Successfully Created a New User Account!',
                    id='create-alert',
                    duration=2500,
                    dismissable=False,
                    is_open=False,
                    color='success',
                    className='mt-3'
                ),
                dbc.Alert(
                    'Unable to Create a New Account with those Credentials! '
                    'Please double check to make sure your account details are all valid.',
                    id='no-create-alert',
                    duration=2500,
                    dismissable=False,
                    is_open=False,
                    color='danger',
                    className='mt-3'
                ),
            ],
                className='mt-5',
            )
        ],
            width={'size': 4},
            align='center',
            className='ml-0 mr-0 py-5 d-inline-block',
        ),
        dbc.Col([
            html.Div()
        ],
            width={'size': 4},
            className='ml-0 mr-0',
        ),
    ],
        align='center',
    ),
)


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
                                                                              0.386283101, end_angle=0.386283101,
                                  opposite=True),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
            # front-court 3pt line
            dict(type="path",
                 path=ellipse_arc(
                     a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
            # back-court corner three lines
            dict(
                type="line", x0=-220, y0=835 - threept_break_y, x1=-220, y1=887.5,
                line=dict(color=three_line_col, width=lwidth), layer=glayer
            ),
            dict(
                type="line", x0=220, y0=835 - threept_break_y, x1=220, y1=887.5,
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
                                  start_angle=0, end_angle=2 * np.pi),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
            # half-court inner circle
            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=25, b=25,
                                  start_angle=0, end_angle=2 * np.pi),
                 line=dict(color=main_line_col, width=lwidth), layer=glayer),
        ]
    )
    return True


##############################################################################
############################# Initialize Graphs ##############################
##############################################################################

GS = 100
fig = px.scatter(
    x=np.repeat(np.linspace(-300, 300, GS), GS),
    y=np.tile(np.linspace(-75, 900, GS), GS),
    opacity=0
)
draw_plotly_court(fig, margins=0)

display_fig = go.Figure()
draw_plotly_court(display_fig, show_title=False, labelticks=False, show_axis=False,
                  glayer='above', bg_color='black', margins=0)

##############################
hist_fig = px.histogram(nbins=24,
                        template="plotly_dark"
                        )

dist_fig = px.bar_polar(template="plotly_dark",
                        color_discrete_sequence=['#67001f', '#bb2a34', '#e58368', '#fbceb6', '#f7f7f7',
                                                 '#c1ddec', '#6bacd1', '#2a71b2', '#053061'],
                        )

shottype_fig = px.bar_polar(template="plotly_dark",
                            color_discrete_sequence=['#67001f', '#bb2a34', '#e58368', '#fbceb6', '#f7f7f7',
                                                     '#c1ddec', '#6bacd1', '#2a71b2', '#053061'],
                            )

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

about_offcanvas = dbc.Offcanvas([
    html.H5('Motivation'),
    html.P("Currently, publicly available spatial data is limited to shot coordinate data. "
           "As a result, this application was built in order to analyze hand-tracked pass "
           "coordinate data during assist plays."),
    html.H5('About The Data Source'),
    html.P(["Thanks to Darryl Blackport, the currently available shot tracking data has been made "
            "accessible on his site at ",
            html.A("tracking.pbpstats.com", href="tracking.pbpstats.com"),
            ". That dataset was then filtered for all assisted shots. "
            "I then built an application to manually track the pass origin "
            "and endpoint by watching film from the Video URL that the dataset pairs each shot with. Please "
            "feel free to read more about the tracking application here as this app is not publicly available. "
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
############################### Tracking Tab #################################
##############################################################################

tracking_tab = dbc.Container([
    dbc.Row([
        dbc.Col([
            court_graph
        ],
            width={'size': 3},
            className='ml-0 mr-3',
        ),
        dbc.Col([
            html.H3("Tracking Panel", className='mt-2 text-center'),
            html.Hr(className="my-2"),
            html.P(
                "Use the selection panel below to manually "
                "track plays and add new data tags. Select "
                "corresponding identifiers for each play viewed "
                "and then click Update."

            ),
            daq.BooleanSwitch(id='track-toggle', on=False,
                              label='Pass Tracking is Off',
                              labelPosition='right',
                              className='mb-2',
                              color='green'
                              ),
            html.Hr(className="my-2"),
            dcc.Dropdown(
                id='player-select', multi=False, placeholder='Select Player...',
                # options=player_options,
                options=[],
                searchable=True,
                clearable=False,
                value=2544,
                persistence=True,
            ),
            html.Hr(className="my-2"),
            daq.ToggleSwitch(id='coordinate-toggle',
                             label='Input Pass Received Coordinates',
                             labelPosition='top',
                             disabled=True
                             ),
            html.Div(id='shotclock-container',
                     className='text-center',
                     # style={'margin-top': 20}
                     ),
            dcc.Slider(
                id='shotclock-select', min=0, max=24, step=1, value=12,
                marks={
                    0: '0s',
                    6: '6s',
                    12: '12s',
                    18: '18s',
                    24: '24s'
                },
                # className='bg-dark'
            ),
            html.Div(id='numdribble-container',
                     className='text-center',
                     # style={'margin-top': 20}
                     ),
            dcc.Slider(
                id='numdribble-select', min=0, max=20, step=1, value=5,
                marks={
                    0: '0',
                    5: '5',
                    10: '10',
                    15: '15',
                    20: '20'
                },
                # className='bg-dark'
            ),
            html.Hr(className="my-2"),
            html.P(
                "Select Data Tags:",
                className='m-2 text-center'
            ),

            html.Div([
                dbc.RadioItems(
                    id="hand-select",
                    className="btn-group",
                    labelClassName="btn btn-info",
                    labelCheckedClassName="active",
                    inputClassName="btn-check",
                    options=[
                        {'label': 'Left - Hand', 'value': 'Left', 'disabled': 'True'},
                        {'label': 'Both - Hands', 'value': 'Both', 'disabled': 'True'},
                        {'label': 'Right - Hand', 'value': 'Right', 'disabled': 'True'},
                    ],
                    style={'width': '100%'},  # <---  for external <div>
                    labelStyle={'width': '100%'},  # <---  for <input>
                )
            ],
                className="radio-group",
                style={"margin-top": "5px", "margin-bottom": "5px"}
            ),
            html.Div([
                dbc.RadioItems(
                    id="pr-select",
                    className="btn-group",
                    labelClassName="btn btn-info",
                    labelCheckedClassName="active",
                    inputClassName="btn-check",
                    options=[
                        {'label': 'Pick & Roll', 'value': True, 'disabled': 'True'},
                        {'label': 'Not Pick & Roll', 'value': False, 'disabled': 'True'},
                    ],
                    style={'width': '100%'},  # <---  for external <div>
                    labelStyle={'width': '100%'},  # <---  for <input>
                )
            ],
                className="radio-group",
                style={"margin-top": "5px", "margin-bottom": "5px"}
            ),
            html.Div([
                dbc.RadioItems(
                    id="cs-select",
                    className="btn-group",
                    labelClassName="btn btn-info",
                    labelCheckedClassName="active",
                    inputClassName="btn-check",
                    options=[
                        {'label': 'Catch & Shoot', 'value': True, 'disabled': 'True'},
                        {'label': 'Other', 'value': False, 'disabled': 'True'},
                    ],
                    style={'width': '100%'},  # <---  for external <div>
                    labelStyle={'width': '100%'},  # <---  for <input>
                ),
            ],
                className='radio-group mb-2'
            ),
            html.Hr(className="my-2"),
            html.Div([
                dbc.Button(
                    "Prev. Play", id='previous-btn', className='mr-3 mb-2', color="primary",
                    n_clicks=0, style={'width': '50%'}),
                dbc.Button(
                    "Next Play", id='next-btn', className='mb-2', color="primary",
                    n_clicks=0, style={'width': '50%'}),
                dbc.Button(
                    "Update Dataset", id='update-btn', className='mb-2 btn btn-outline-success', color="link",
                    n_clicks=0, style={'width': '100%'}, disabled=True),
            ]),
        ],
            width=2,
            className='mr-3'
        ),
        dbc.Col([
            html.H3("Video Playback", className='mt-2 text-center'),
            html.Center([
                html.Video(
                    id='video-playback',
                    controls=True,
                    src='',
                    loop='loop',
                    autoPlay=False,
                    width='100%',
                    height='100%'
                ),
            ]),
            dbc.Row([
                daq.BooleanSwitch(id='autoplay-toggle', on=False,
                                  label='AutoPlay On',
                                  labelPosition='right',
                                  className='mb-2',
                                  color='#9B51E0',
                                  style={'width': '15%'}
                                  ),
                daq.NumericInput(
                    id='row-id-input',
                    min=0,
                    max=99999999,
                    value=0,
                    size=80,
                    className='mr-2',
                    style={'width': '10%'}
                ),
                dbc.Button("Fetch Video", id='video-btn',
                           color='link',
                           className='mb-2 mr-2 btn btn-outline-success',
                           disabled=False,
                           style={'width': '20%'}),
            ]),

            html.Div([
                "Play-Tracking Progress Bar:"
            ]),

            dbc.Progress(
                id='tracking-progress',
                label="Loading...", value=100,
                striped=True,
                className='mb-3'
            ),

            dbc.Alert(
                "Cannot update Dataset. Please make you've selected all the required data tags.",
                id="data-alert",
                dismissable=True,
                fade=True,
                is_open=False,
                duration=7500,
                color='danger'
            ),

            dbc.Alert(
                "Cannot find Video with that ID! Please refer to row_id column in the Data Table for valid Video IDs.",
                id="id-alert",
                dismissable=True,
                fade=True,
                is_open=False,
                duration=7500,
                color='danger'
            ),

            dbc.Alert(
                "Updated Table with new Tracked Data Tags!",
                id="update-alert",
                dismissable=True,
                fade=True,
                is_open=False,
                duration=5000,
                color='success'
            ),

            dbc.Toast(
                "Updated Table with new Tracked Data Tags!",
                id="update-toast",
                header="Positioned toast",
                is_open=False,
                dismissable=True,
                icon="danger",
                # top: 66 positions the toast below the navbar
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            ),

            html.Div(id='output-container2+',
                     className='text-center',
                     ),
        ])
    ])

], fluid=True)

##############################################################################
################################# Table Tab ##################################
##############################################################################

table_tab = html.Div([
    dash_table.DataTable(
        id='tracking-table',
        fixed_rows={'headers': False},
        style_table={'overflowX': 'auto',
                     'overflowY': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],

        page_size=23,

        # sort_action='custom',
        # sort_mode='multi',
        # sort_by=[]
        # columns=[{"name": i, "id": i} for i in trackingdata_df.columns],
    ),
    html.Center([
        dbc.Button("Download CSV", id='download-btn',
                   color='link',
                   className='mb-2 mr-2 btn btn-outline-success', ),
        dcc.Download(id='download-dataframe-csv'),
        dbc.Button("Update Data to Cloud", id='save-btn',
                   color='link',
                   className='mb-2 btn btn-outline-success',
                   disabled=False),
        dbc.Toast(
            "Unable to Update Database on the back-end with new Tracked Data Tags! "
            "Please try again or reach out to the admin if you are having issues.",
            id="no-save-toast",
            header="Database Update:",
            is_open=True,
            dismissable=True,
            duration=5000,
            icon="danger",
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "bottom": 95, "right": 790, "width": 350},
        ),
        dbc.Toast(
            "Successfully Updated Database on the back-end with new Tracked Data Tags!",
            id="save-toast",
            header="Database Update:",
            is_open=True,
            dismissable=True,
            duration=5000,
            icon="success",
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "bottom": 95, "right": 790, "width": 350},
        ),
    ]),
])

##############################################################################
################################# Main Page ##################################
##############################################################################

main_page = dbc.Tabs([
    dbc.Tab(tracking_tab, label="Track Plays", tab_id='tracking-page'),
    dbc.Tab(table_tab, label="View Raw Tracked Data", tab_id='data-page'),
],
    id='main-page-tabs',
    # active_tab="tracking-page",
)

##############################################################################
######################### Interactive Dashboard Page #########################
##############################################################################

dashboard_page = dbc.Container([
    dcc.Store(id='stored-player-data-2', storage_type='session', data=''),
    dcc.Store(id='filtered-player-data-2', storage_type='session', data=''),
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
                # options=player_options,
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
                value=[0, 24],
                allowCross=False,
                marks={
                    0: '0s',
                    6: '6s',
                    12: '12s',
                    18: '18s',
                    24: '24s',
                },
                # tooltip={'placement': 'top',
                #         'always_visible': True},
                updatemode='drag'
            ),
            html.P("Minute Filter:", className='mt-2 mb-2 text-left font-weight-bolder'),
            dcc.RangeSlider(
                id='time-filter',
                min=0,
                max=720,
                step=1,
                value=[0, 720],
                allowCross=False,
                marks={
                    0: '0:00',
                    180: '3:00',
                    360: '6:00',
                    540: '9:00',
                    720: '12:00',
                },
                # tooltip={'placement': 'top',
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
                        style={"overflow-y": "scroll", "height": "200px",
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
                               'LongMidRange', 'AtRim'],
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
                            # {'label': 'Pick and Roll', 'value': 'PR'},
                            # {'label': 'Non-Pick and Roll', 'value': 'NoPR'},
                            {'label': 'Catch and Shoot', 'value': 'CS'},
                            {'label': 'Non-Catch and Shoot', 'value': 'NoCS'},
                            # {'label': 'Wide Open', 'value': 'Wide Open'},
                            # {'label': 'Contested', 'value': 'Contested'},
                        ],
                        value=['CS', 'NoCS',
                               # 'Wide Open','Contested'
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
            ], ),
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
                        value=[1, 2, 3, 4],
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
                        style={"overflow-y": "scroll", "height": "200px"},
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
                        value=['OffFTMiss', 'OffFTMake', 'OffArc3Miss', 'OffArc3Make', 'OffArc3Block',
                               'OffCorner3Miss', 'OffCorner3Make', 'OffCorner3Block',
                               'OffAtRimMiss', 'OffAtRimMake', 'OffAtRimBlock',
                               'OffShortMidRangeMiss', 'OffShortMidRangeMake', 'OffShortMidRangeBlock',
                               'OffLongMidRangeMiss', 'OffLongMidRangeMake', 'OffLongMidRangeBlock',
                               'OffTimeout', 'OffLiveBallTurnover', 'OffDeadball'],
                        labelStyle={'display': 'block'},
                        inputStyle={"margin-right": "5px"},
                        style={"overflow-y": "scroll", "height": "200px"},
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
                "Essentially imagine the player is facing South. "
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
                "Feel free to click on any scatter point on the court for a Circular KDE "
                "representation of passing tendencies at that particular spot on the floor.",
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
                "Click on a Scatter Point on the Court before clicking this button to view video of the play. ",
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
        # dbc.Button("About This App", id="open-offcanvas", n_clicks=0),
        dbc.NavLink('About This App', href='/home', active='exact', id='home-navlink'),
        dbc.NavLink('Create User', href='/create', active='exact', id='create-navlink'),
        dbc.NavLink("Track Plays", href="/tracking", id='track-navlink'
                    ),
        dbc.NavLink("Interactive Dashboard", href="/dashboard", active='exact', id='dashboard-'
                    ),
        dbc.Button("Logout", href='/login', id='logout-btn', disabled=True, outline=False)
    ],
        dark=True,
        color='primary',
        brand='Tracking Plays App',
        brand_href='#',
        className='py-lg-0',
    )
)

content = html.Div(id='page-content', children=[login])

tracking_columns = ['pass_x', 'pass_y', 'pass_rec_x', 'pass_rec_y',
                    'pass_shotclock', 'catch_and_shoot', 'pick_and_roll',
                    'handedness', 'courtside', 'pass_distance',
                    'pass_angle', 'pass_shot_distance', 'direction',
                    'pass_dist_range', 'num_dribbles', 'row_id']

app.layout = html.Div([
    dcc.Store(id='is-admin', storage_type='session', data=''),
    dcc.Store(id='processed-distance-data', storage_type='session', data=''),
    dcc.Store(id='processed-shottype-data', storage_type='session', data=''),
    dcc.Store(id='stored-player-data', storage_type='session', data=''),
    dcc.Store(id='distances_df_template', storage_type='session',
              data=pd.DataFrame(product(directions, distances, [0]),
                                columns=['Direction', 'Pass Distance', 'Frequency']).to_dict('records')),
    dcc.Store(id='shottypes_df_template', storage_type='session',
              data=pd.DataFrame(product(directions, shottypes, [0]),
                                columns=['Direction', 'Shot Type', 'Frequency']).to_dict('records')),
    dcc.Store(id='stored-player-id', storage_type='session'),
    dcc.Store(id='stored-video-url', storage_type='session', data=''),
    dcc.Store(id='row-id', storage_type='session', data=0),
    dcc.Store(id='pass-received-coordinates', storage_type='session', data=[]),
    dcc.Store(id='pass-thrown-coordinates', storage_type='session', data=[]),
    dcc.Store(id='tracked-cols', storage_type='session', data=['pass_x', 'pass_y', 'pass_rec_x', 'pass_rec_y',
                                                               'pass_shotclock', 'catch_and_shoot', 'pick_and_roll',
                                                               'handedness', 'pass_distance',
                                                               'pass_angle', 'pass_shot_distance', 'direction',
                                                               'pass_dist_range', 'num_dribbles', 'row_id']),

    dcc.Store(id='player-options', storage_type='session', data=[]),
    dcc.Store(id='team-options', storage_type='session', data=[]),
    dcc.Store(id='tracked-player-options', storage_type='session', data=[]),
    dcc.Location(id='url', refresh=False),
    navigation_bar,
    content])


##############################################################################
############################### App Callbacks ################################
##############################################################################

@app.callback(
    Output(component_id="page-content", component_property="children"),
    Output(component_id='logout-btn', component_property='disabled'),
    Input(component_id="url", component_property="pathname"),
    State(component_id='is-admin', component_property='data'),
)
def render_page_content(pathname, is_admin):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    print('-----------------')
    print(current_user, current_user.is_authenticated)
    if pathname == '/login' and current_user.is_authenticated:
        print('showing login screen and user is authenticated', pathname)
        logout_user()
        return login, True
    elif pathname == '/login' or current_user.is_authenticated == False:
        print('showing login screen, but user is not authenticated', pathname)
        return login, True
    elif pathname == '/create' and current_user.is_authenticated:
        if is_admin == False:
            print('showing create screen, but user has no admin access', pathname)
            return html.Div(
                dbc.Container(
                    [
                        html.H1("You do not have access to this page.", className="text-danger"),
                        html.Hr(),
                        html.P("Please contact the Admin if you believe you were suppose to be "
                               "granted access to this page."),
                    ],
                    fluid=True,
                    className="py-3",
                ),
                className="p-3 bg-light rounded-3",
            ), False
        print('showing create screen and user has admin access', pathname)
        return create, False
    elif pathname == '/home' and current_user.is_authenticated:
        print('showing home screen after logging in', pathname)
        return home, False
    elif pathname == '/tracking' and current_user.is_authenticated:
        if is_admin == False:
            print('showing tracking screen, but user has no admin access', pathname)
            return html.Div(
                dbc.Container(
                    [
                        html.H1("You do not have access to this page.", className="text-danger"),
                        html.Hr(),
                        html.P("Please contact the Admin if you believe you were suppose to be "
                               "granted access to this page."),
                    ],
                    fluid=True,
                    className="py-3",
                ),
                className="p-3 bg-light rounded-3",
            ), False
        print('showing tracking screen and user has admin access', pathname)
        return main_page, False
    elif pathname == '/dashboard' and current_user.is_authenticated:
        print('showing dashboard screen', pathname)
        return dashboard_page, False
    else:
        print('showing error page', pathname)
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
        ), dash.no_update
    return dash.no_update, dash.no_update


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
    return 'Tooltips are On' if tooltips_toggle else 'Tooltips are Off'


@app.callback(
    Output(component_id='graph-toggle', component_property='label'),
    Input(component_id='graph-toggle', component_property='value'),
)
def update_input_toggle_info(graph_toggle):
    return 'Rose Plot by Pass Distance' if not graph_toggle else 'Rose Plot by Shot Type Created'


@app.callback(
    Output(component_id='stored-player-data-2', component_property='data'),
    Input(component_id='tracked-player-select', component_property='value')
)
def update_player_data2(pid):
    conn = engine_two.connect()
    results = conn.execute("SELECT * FROM nbatrackingdata WHERE assistplayerid = %s", (pid,))
    player_df = pd.DataFrame(results.fetchall(), columns=results.keys())
    player_df = player_df[~player_df['pass_x'].isnull()]
    conn.close()
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
        distcounts_df = player_df.groupby(['direction', 'pass_dist_range']).size().reset_index()
        distcounts_df = distcounts_df.rename({
            'direction': 'Direction', 'pass_dist_range': 'Pass Distance', 0: 'Frequency 2'
        }, axis=1)
        shotcounts_df = player_df.groupby(['direction', 'shottype']).size().reset_index()
        shotcounts_df = shotcounts_df.rename({
            'direction': 'Direction', 'shottype': 'Shot Type', 0: 'Frequency 2'
        }, axis=1)
        distances_df = distances_df.merge(distcounts_df, on=['Direction', 'Pass Distance', ], how='left')
        distances_df['Frequency'] = np.max(distances_df[['Frequency', 'Frequency 2']], axis=1)
        distances_df = distances_df.drop(columns=['Frequency 2'])
        shottypes_df = shottypes_df.merge(shotcounts_df, on=['Direction', 'Shot Type'], how='left')
        shottypes_df['Frequency'] = np.max(shottypes_df[['Frequency', 'Frequency 2']], axis=1)
        shottypes_df = shottypes_df.drop(columns=['Frequency 2'])
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
    data = distance_data if not graph_toggle else shottype_data
    if f_data != []:
        distances_colors = ['#67001f', '#bb2a34', '#e58368', '#fbceb6', '#f7f7f7',
                            '#c1ddec', '#6bacd1', '#2a71b2', '#053061']
        shottype_colors = ['#b7e2ab', '#6fc9a3', '#46879c', '#3e5590', '#2c2037']
        new_fig = px.bar_polar(pd.DataFrame(data), r="Frequency", theta="Direction",
                               color='Pass Distance' if not graph_toggle else 'Shot Type',
                               template="plotly_dark",
                               color_discrete_sequence=distances_colors if not graph_toggle else shottype_colors,
                               title="Passing Tendencies on Assists by %s" % (
                                   'Pass Distance' if not graph_toggle else 'Shot Type'),
                               )
        new_fig.update_layout(legend_title_text='Pass Distance Range' if not graph_toggle else 'Shot Type Created',
                              )
        return new_fig
    return px.bar_polar(template="plotly_dark",
                        title='No Data To Display! Please double check your filters again!')


@app.callback(
    Output(component_id='hist-plot', component_property='figure'),
    Input(component_id='graph-toggle', component_property='value'),
    Input(component_id='filtered-player-data-2', component_property='data'),
)
def update_histogram(graph_toggle, data):
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
                               nbins=len([x for x in range(df['pass_shotclock'].min(), df['pass_shotclock'].max() + 1)])
                               )
        new_fig.update_layout(yaxis_title='Frequency',
                              legend_title_text='Pass Distance Range' if not graph_toggle else 'Shot Type Created',
                              )
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
    conn = engine_two.connect()
    results = conn.execute("SELECT assistplayerid, assist_player, offense_team_id, team, pass_x FROM nbatrackingdata")
    allids_df = pd.DataFrame(results.fetchall(), columns=results.keys())
    conn.close()
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

    tracked_pids_df = pd.DataFrame(
        allids_df[~allids_df['pass_x'].isnull()].groupby(['assistplayerid', 'assist_player']).size(
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
    return team_options, [team['value'] for team in team_options]


@app.callback(
    Output(component_id='tracked-player-select', component_property='options'),
    Input(component_id='tracked-player-options', component_property='data'),
)
def update_pselect2_options(tracked_player_options, ):
    return tracked_player_options


@app.callback(
    Output(component_id='pass-target-filter', component_property='options'),
    Output(component_id='pass-target-filter', component_property='value'),
    Input(component_id='stored-player-data-2', component_property='data'),
)
def update_target_filter(data, ):
    targets_df = pd.DataFrame(pd.DataFrame(data).groupby(['playerid', 'player']).size(
    ).reset_index().rename(columns={0: 'count',
                                    'player': 'label',
                                    'playerid': 'value'}))
    targets_df = targets_df[['label', 'value']].sort_values('label').reset_index(drop=True)
    target_options = targets_df.to_dict('records')
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
        b = y1 - (m * x1)
        x = np.linspace(x1, x2, 250)
        y = m * x + b
        return x, y

    def vonmises_kde(data, kappa, n_bins=100):
        from scipy.special import i0
        bins = np.linspace(-np.pi, np.pi, n_bins)
        x = np.linspace(-np.pi, np.pi, n_bins)
        # integrate vonmises kernels
        kde = np.exp(kappa * np.cos(x[:, None] - data[None, :])).sum(1) / (2 * np.pi * i0(kappa))
        kde /= np.trapz(kde, x=bins)
        return bins, kde

    def circle(r0, theta0, rho, degrees=True):
        ##https://community.plotly.com/t/shapes-on-a-polar-plot-is-it-posible/29155/2
        from numpy import pi, sin, cos, sqrt, arctan2
        # compute the polar coordinates for 100 points on a circle of center (r0, theta0) and radius rho
        if degrees:
            theta0 = theta0 * pi / 180
        phi = np.linspace(0, 2 * pi, 100)
        x = rho * cos(phi) + r0 * cos(theta0)
        y = rho * sin(phi) + r0 * sin(theta0)
        r = sqrt(x ** 2 + y ** 2)

        J = np.where(y < 0)
        theta = arctan2(y, x)
        theta[J] = theta[J] + 2 * pi
        return (r, theta * 180 / pi) if degrees else (r, theta)

    if data != []:
        df = pd.DataFrame(data)
        display_fig.data = []  ##display_fig
        # fig['data'] = [] ##display_fig
        display_fig.add_trace(go.Histogram2dContour(  ##
            x=df['%sx' % graph_type].to_list(),
            y=df['%sy' % graph_type].to_list(),
            colorscale='Inferno',
            xaxis='x2',
            yaxis='y2',
            showscale=False,
            line=dict(width=0),
            hoverinfo='none'
        ))
        display_fig.add_trace(go.Scatter(  ##
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
        # https://chart-studio.plotly.com/~empet/15366/customdata-for-a-few-plotly-chart-types/#/#
        display_fig.update_traces(customdata=new_customdatadf,  ##
                                  selector=dict(type='scatter'),
                                  hovertemplate="<b>Date:</b> %{customdata[4]}<br>" +
                                                "<b>Time:</b> Q%{customdata[2]} | %{customdata[3]} left in the Quarter<br>" +
                                                "<b>Player Assisted:</b> %{customdata[1]}<br>" +
                                                "<b>Shot Type Created:</b> %{customdata[0]}<br>" +
                                                "<b>Pass Distance:</b> %{customdata[6]} ft.<br>" +
                                                "<b>Possession Start Type:</b> %{customdata[5]}<br>" if tooltips_ison else None
                                  )
        try:
            if 'pointNumber' in clickData['points'][0].keys():
                df = pd.DataFrame(data)
                r, ref_x, ref_y = 35, clickData['points'][0]['customdata'][7], clickData['points'][0]['customdata'][8]
                df['within_dist'] = df.apply(lambda x: True if (
                            np.sqrt((ref_x - x['pass_x']) ** 2 + (ref_y - x['pass_y']) ** 2) <= r) else False, axis=1)
                df['pass_angle'] = df['pass_angle'] * (math.pi / 180)
                filtered_df = df[df['within_dist'] == True]
                bins, kde = vonmises_kde(np.array(filtered_df['pass_angle'].to_list()), kappa=10, n_bins=1000)
                x = [ref_x + (r * 100) * math.cos(theta) for r, theta in zip(kde, bins)]
                y = [ref_y + (r * 100) * math.sin(theta) for r, theta in zip(kde, bins)]
                r, theta = circle(0, 0, .1)
                display_fig.add_trace(go.Scatter(  ##
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
            return display_fig  ##
        except:
            return display_fig  ##
    court_fig = go.Figure()
    draw_plotly_court(court_fig, show_title=False, labelticks=False, show_axis=False,
                      glayer='above', bg_color='black', margins=0)
    return court_fig


@app.callback(
    Output(component_id='video-playback-modal', component_property='src'),
    Output(component_id='modal-title', component_property='children'),
    Input(component_id='display-graph', component_property='clickData')
)
def update_video_modal(clickData):
    if clickData:
        try:
            link = clickData['points'][0]['customdata'][-1]
            player = clickData['points'][0]['customdata'][1]
            assist_player = clickData['points'][0]['customdata'][-4]
            date = clickData['points'][0]['customdata'][4]
            date = datetime.fromisoformat(date).strftime('%b %d, %Y')
            opp = clickData['points'][0]['customdata'][-2]
            team = clickData['points'][0]['customdata'][-3]
            title = "%s's assist to %s (%s vs. %s on %s)" % (assist_player, player, team, opp, date)  # [:10])
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
    # prevent_initial_callback=True
)
def filter_player_data(shotclock_filter, minute_filter, hand_filter, target_filter,
                       shottype_filter, opp_team_filter, extra_filter, period_filter,
                       possession_filter, start_date, end_date, data):
    player_df = pd.DataFrame(data)
    player_df['date'] = pd.to_datetime(player_df['date'])
    player_df = player_df[(player_df['date'] > start_date) & (player_df['date'] <= end_date)]
    player_df['time'] = player_df['time'].str.split(':').apply(lambda x: int(x[0]) * 60 + int(x[1]))
    filtered_df = player_df[
        player_df['pass_shotclock'].between(shotclock_filter[0], shotclock_filter[1], inclusive='both')]
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


### login logic

@app.callback(
    Output(component_id='url', component_property='pathname'),
    Output(component_id='is-admin', component_property='data'),
    Input(component_id='login-btn', component_property='n_clicks'),
    State(component_id='uname-box', component_property='value'),
    State(component_id='pwd-box', component_property='value'),
)
def successful(login, input1, input2, ):
    user = Users.query.filter_by(username=input1).first()
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if user:
        if check_password_hash(user.password, input2):
            login_user(user)
            print('user has been logged in')
            return '/home', user.admin
        else:
            return dash.no_update, dash.no_update
    return dash.no_update, dash.no_update


@app.callback(
    # Output(component_id='output-state', component_property='children'),
    Output(component_id='login-alert', component_property='is_open'),
    Input(component_id='login-btn', component_property='n_clicks'),
    State(component_id='uname-box', component_property='value'),
    State(component_id='pwd-box', component_property='value')
)
def update_output(n_clicks, input1, input2):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'login-btn' in changed_id:
        user = Users.query.filter_by(username=input1).first()
        if user:
            if check_password_hash(user.password, input2):
                ##return ''
                return dash.no_update
            else:
                return True
                # return 'Incorrect username or password'
        else:
            return True
            # return 'Incorrect username or password'
    else:
        return dash.no_update
        # return ''


## create logic
@app.callback(
    # Output(component_id='url', component_property='pathname'),
    Output(component_id='create-alert', component_property='is_open'),
    Output(component_id='no-create-alert', component_property='is_open'),
    Input(component_id='create-user-btn', component_property='n_clicks'),
    State(component_id='username', component_property='value'),
    State(component_id='password', component_property='value'),
    State(component_id='email', component_property='value'),
    State(component_id='admin-access', component_property='on'),
    State(component_id='username', component_property='valid'),
    State(component_id='password-confirm', component_property='valid'),
    State(component_id='email', component_property='valid'),
)
def insert_users(n_clicks, un, pw, em, admin, un_valid, cpw_valid, em_valid):
    # hashed_password = generate_password_hash(pw, method='sha256')
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if un is not None and pw is not None and em is not None and admin is not None and un_valid and cpw_valid and em_valid:
        hashed_password = generate_password_hash(pw, method='sha256')
        ins = Users_tbl.insert().values(username=un, password=hashed_password, email=em, admin=admin)
        conn = engine.connect()
        conn.execute(ins)
        conn.close()
        return True, False  # [login]
    elif 'create-user-btn' in changed_id:
        return False, True
    else:
        return dash.no_update, dash.no_update
    # else:
    #    return [html.Div([html.H2('Already have a user account?'), dcc.Link('Click here to Log In', href='/login')])]


@app.callback(
    Output(component_id='username', component_property='valid'),
    Output(component_id='username', component_property='invalid'),
    Input(component_id='username', component_property='value'),
)
def check_username(username, ):
    if username is None or len(username) == 0:
        return None, None
    elif username is not None and Users.query.filter_by(username=username).first() is None:
        return True, None
    else:
        return None, True


@app.callback(
    Output(component_id='password', component_property='valid'),
    Output(component_id='password', component_property='invalid'),
    Input(component_id='password', component_property='value'),
)
def check_password(password, ):
    if password is None or len(password) == 0:
        return None, None
    elif password is not None:
        return True, None
    else:
        return None, True


@app.callback(
    Output(component_id='password-confirm', component_property='valid'),
    Output(component_id='password-confirm', component_property='invalid'),
    Input(component_id='password-confirm', component_property='value'),
    State(component_id='password', component_property='value'),
)
def check_valid_password(confirm_password, password, ):
    if confirm_password is None or len(confirm_password) == 0:
        return None, None
    elif password == confirm_password and confirm_password is not None:
        return True, None
    else:
        return None, True


@app.callback(
    Output(component_id='email', component_property='valid'),
    Output(component_id='email', component_property='invalid'),
    Input(component_id='email', component_property='value'),
)
def check_email(email, ):
    if email is None or len(email) == 0:
        return None, None
    elif email is not None and re.fullmatch(regex, email):
        return True, None
    else:
        return None, True


# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    print('The current User ID is...', user_id)
    print('Trying to query by ID', Users.query.filter_by(id=user_id).first())
    try:
        print('Querying for that ID specifically...', Users.query.get(user_id))
        return Users.query.get(user_id)
    except:
        print('Did not get any ID at all...')
        return None
    #return Users.query.get(int(user_id))


###main page callbacks

@app.callback(
    Output(component_id='stored-player-id', component_property='data'),
    Input(component_id='player-select', component_property='value'),
)
def update_player_name(pid):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'player-select' in changed_id:
        return pid


@app.callback(
    Output(component_id='stored-player-data', component_property='data'),
    Output(component_id='update-alert', component_property='is_open'),
    Input(component_id='player-select', component_property='value'),
    Input(component_id='update-btn', component_property='n_clicks'),
    State(component_id='cs-select', component_property='value'),
    State(component_id='pr-select', component_property='value'),
    State(component_id='hand-select', component_property='value'),
    State(component_id='shotclock-select', component_property='value'),
    State(component_id='numdribble-select', component_property='value'),
    State(component_id='tracked-cols', component_property='data'),
    State(component_id='stored-player-data', component_property='data'),
    State(component_id='row-id', component_property='data'),
    State(component_id='update-alert', component_property='is_open')
)
def update_player_data(pid, btn, cs_val, pr_val, hand_val, shotclock_val,
                       num_dribbles, tracking_cols, player_data, row, is_open):
    def calc_pass_data(throw_x, throw_y, rec_x, rec_y, shot_x, shot_y, ):
        points = ["E", "ENE", "NE", "NEN", "N", "NWN", "NW", "WNW",
                  "W", "WSW", "SW", "SWS", "S", "SES", "SE", "ESE", ]
        pass_x, pass_y = rec_x - throw_x, rec_y - throw_y
        pass_shot_x, pass_shot_y = shot_x - rec_x, shot_y - rec_y
        pass_dist = round(np.sqrt(pass_x ** 2 + pass_y ** 2) / 10, 1)
        pass_angle = round(np.arctan2(pass_y, pass_x) * (180 / math.pi),
                           2)  # if courtside_val == 'Frontcourt' else round(np.arctan2(pass_y, pass_x) * (180/math.pi) + 180, 2)
        pass_shot_dist = round(np.sqrt(pass_shot_x ** 2 + pass_shot_y ** 2) / 10, 1)
        pass_dist_range = (str(int(pass_dist // 10 * 10)) + '-'
                           + str(int(((pass_dist // 10 * 10) + 10))) + ' ft.')
        direction = points[int((pass_angle + 11.25) / 22.5)]
        return pass_dist, pass_angle, pass_shot_dist, direction, pass_dist_range

    def get_coordinates():
        throw_x, throw_y = fig.data[scatter_names.index('thrown')]['x'][0], \
                           fig.data[scatter_names.index('thrown')]['y'][0]
        rec_x, rec_y = fig.data[scatter_names.index('received')]['x'][0], \
                       fig.data[scatter_names.index('received')]['y'][0]
        return throw_x, throw_y, rec_x, rec_y

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'player-select' in changed_id:
        conn = engine_two.connect()
        results = conn.execute("SELECT * FROM nbatrackingdata WHERE assistplayerid = %s", (pid,))
        player_df = pd.DataFrame(results.fetchall(), columns=results.keys())
        conn.close()
        return player_df.reset_index(drop=True).to_dict('records'), is_open
    elif 'update-btn' in changed_id and cs_val != None and pr_val != None and hand_val != None:
        updated_player_df = pd.DataFrame(player_data)
        try:
            scatter_names = [data['name'] for data in fig.data]
            throw_x, throw_y, rec_x, rec_y = get_coordinates()
            shot_x, shot_y = updated_player_df.iloc[row]['x'], updated_player_df.iloc[row]['y']
            pass_dist, pass_angle, pass_shot_dist, direction, pass_dist_range = calc_pass_data(throw_x, throw_y,
                                                                                               rec_x, rec_y,
                                                                                               shot_x, shot_y)
            input_values = [round(throw_x, 0), round(throw_y, 0),
                            round(rec_x, 0), round(rec_y, 0),
                            shotclock_val, cs_val, pr_val, hand_val, pass_dist, pass_angle,
                            pass_shot_dist, direction, pass_dist_range, num_dribbles]
            for (col_name, value) in zip(tracking_cols[:-1], input_values):
                updated_player_df.at[row, col_name] = value
            row_updates_df = updated_player_df[~updated_player_df['pass_dist_range'].isnull()]
            row_updates_df.to_sql("newtrackeddata", con=engine_two, if_exists='replace', index=False)
            return updated_player_df.to_dict('records'), not is_open
        except:
            return dash.no_update
    return dash.no_update, is_open


@app.callback(
    Output(component_id='player-select', component_property='options'),
    Input(component_id='player-options', component_property='data'),
)
def update_pselect_options(player_options, ):
    return player_options


@app.callback(
    Output(component_id='tracking-table', component_property='data'),
    Output(component_id='tracking-table', component_property='columns'),
    Input(component_id='stored-player-data', component_property='data'),
    State(component_id='tracked-cols', component_property='data'),
    # Input(component_id='tracking-table', component_property='sort_by')
)
def update_trackingtable(data, tracking_columns, ):  # sort_by):
    non_tracking_filters = ['date', 'period', 'time', 'x', 'y', 'margin', 'shottype',
                            'possession_start_type', 'closest_def_dist',
                            'shot_clock', 'touch_time', 'dribble_range',
                            'player', 'team', 'opponent', 'assist_player']
    df = pd.DataFrame(data)
    # if len(sort_by):
    #    df = pd.DataFrame(data)
    #    dff = df.sort_values(
    #        sort_by[0]['column_id'],
    #        ascending=sort_by[0]['direction'] == 'asc',
    #        inplace=False
    #    )
    #    dff = dff[non_tracking_filters+tracking_columns]
    #    return dff.to_dict('records'), [{"name": i, "id": i} for i in dff.columns]
    dff = df[non_tracking_filters + tracking_columns]
    return dff.to_dict('records'), [{"name": i, "id": i} for i in dff.columns]


@app.callback(
    Output(component_id='video-playback', component_property='src'),
    Output(component_id='row-id-input', component_property='value'),
    Output(component_id='video-playback', component_property='autoPlay'),
    Output(component_id='row-id', component_property='data'),
    Output(component_id='id-alert', component_property='is_open'),
    # detects button clicks
    Input(component_id='previous-btn', component_property='n_clicks'),
    Input(component_id='next-btn', component_property='n_clicks'),
    Input(component_id='video-btn', component_property='n_clicks'),
    Input(component_id='player-select', component_property='value'),
    Input(component_id='autoplay-toggle', component_property='on'),
    Input(component_id='stored-player-data', component_property='data'),
    State(component_id='row-id', component_property='data'),
    State(component_id='row-id-input', component_property='value')
)
def update_video_playback(btn1, btn2, btn3, pselect, autoplay, data, row, video_id):
    changed_ids = [p['prop_id'] for p in callback_context.triggered]
    changed_id = changed_ids[0]
    if 'next-btn' in changed_id and len(changed_ids) == 1:
        return pd.DataFrame(data).iloc[row + 1]['video_url'], \
               pd.DataFrame(data).iloc[row + 1]['row_id'], dash.no_update, row + 1, False
    elif 'previous-btn' in changed_id and row != 0 and len(changed_ids) == 1:
        return pd.DataFrame(data).iloc[row - 1]['video_url'], \
               pd.DataFrame(data).iloc[row - 1]['row_id'], dash.no_update, row - 1, False
    elif 'player-select' in changed_id and len(changed_ids) == 1:
        return pd.DataFrame(data).iloc[0]['video_url'], \
               pd.DataFrame(data).iloc[0]['row_id'], dash.no_update, 0, False
    elif 'stored-player-data' in changed_id:
        return pd.DataFrame(data).iloc[row]['video_url'], \
               pd.DataFrame(data).iloc[row]['row_id'], dash.no_update, row, False
    elif 'autoplay-toggle' in changed_id:
        return dash.no_update, dash.no_update, autoplay, dash.no_update, False
    elif 'video-btn' in changed_id:
        try:
            df = pd.DataFrame(data)
            new_row = df[df['row_id'] == video_id].index.to_list()[0]
            return pd.DataFrame(data).iloc[new_row]['video_url'], \
                   pd.DataFrame(data).iloc[new_row]['row_id'], dash.no_update, new_row, False
        except:

            return pd.DataFrame(data).iloc[row]['video_url'], \
                   pd.DataFrame(data).iloc[row]['row_id'], dash.no_update, row, True
    return pd.DataFrame(data).iloc[row]['video_url'], \
           pd.DataFrame(data).iloc[row]['row_id'], dash.no_update, row, False


@app.callback(
    Output(component_id='court-graph', component_property='figure'),
    Input(component_id='court-graph', component_property='clickData'),
    State(component_id='track-toggle', component_property='on'),
    State(component_id='coordinate-toggle', component_property='value'),
    State(component_id='stored-player-data', component_property='data'),
    State(component_id='row-id', component_property='data'),
    prevent_initial_callbacks=True
)
def plot_inputs(clickData, track_toggle, input_toggle, data, row_id):
    if clickData != None and track_toggle:
        temp_fig_data, temp_fig_shapes = list(
            fig.data), list(fig.layout['shapes'])
        scatter_names = [data['name'] for data in temp_fig_data]
        shape_names = [shape['name'] for shape in temp_fig_shapes]
        input_type = 'thrown' if not input_toggle else 'received'
        print('------------------')
        print(scatter_names)
        print(shape_names)
        print(input_toggle)
        if len(fig.data) != 1 and input_type in scatter_names:
            try:
                temp_fig_shapes.pop(shape_names.index('pass-vector'))
                fig.layout['shapes'] = temp_fig_shapes
                temp_fig_data.pop(scatter_names.index(input_type))
                fig.data = temp_fig_data
                print('passed try case')
            except:
                temp_fig_data.pop(scatter_names.index(input_type))
                fig.data = temp_fig_data
                print('na we finished except case instead')
        fig.add_scatter(x=[round(clickData['points'][0]['x'], 2)],
                        y=[round(clickData['points'][0]['y'], 2)],
                        mode='markers',
                        marker={
                            'size': 7, 'color': 'orange' if not input_toggle else 'black'},
                        name=input_type)
        print('added new data point', round(clickData['points'][0]['x'], 2), round(clickData['points'][0]['y'], 2))
        try:
            print(fig.data[1]['x'][0], fig.data[1]['y'][0],
                  fig.data[2]['x'][0], fig.data[2]['y'][0],)
        except:
            print(fig.data[1]['x'][0], fig.data[1]['y'][0])
        if len(fig.data) == 3:
            fig.add_shape(type='line', name='pass-vector', layer='below',
                          x0=fig.data[1]['x'][0], y0=fig.data[1]['y'][0],
                          x1=fig.data[2]['x'][0], y1=fig.data[2]['y'][0],
                          line=dict(color='blue', width=2, dash='dot'))
            print('creating a new line vector between points')
        print(scatter_names)
        print(shape_names)
        return fig
    return dash.no_update


@app.callback(
    Output(component_id='track-toggle', component_property='label'),
    Input(component_id='track-toggle', component_property='on')
)
def update_track_toggle_info(track_toggle):
    return 'Pass Tracking is On' if track_toggle else 'Passing Track is Off'


@app.callback(
    Output(component_id='coordinate-toggle', component_property='label'),
    Input(component_id='coordinate-toggle', component_property='value'),
)
def update_input_toggle_info(input_toggle):
    return 'Input Pass Thrown Coords' if not input_toggle else 'Input Pass Received Coords'


@app.callback(
    Output(component_id='autoplay-toggle', component_property='label'),
    Input(component_id='autoplay-toggle', component_property='on')
)
def autoplay_toggle(autoplay):
    return 'AutoPlay On' if autoplay else 'AutoPlay Off'


@app.callback(
    Output(component_id='pr-select', component_property='options'),
    Output(component_id='cs-select', component_property='options'),
    Output(component_id='hand-select', component_property='options'),
    Output(component_id='pr-select', component_property='value'),
    Output(component_id='cs-select', component_property='value'),
    Output(component_id='hand-select', component_property='value'),
    Output(component_id='update-btn', component_property='disabled'),
    Output(component_id='coordinate-toggle', component_property='disabled'),
    Input(component_id='track-toggle', component_property='on'),
    State(component_id='pr-select', component_property='options'),
    State(component_id='cs-select', component_property='options'),
    State(component_id='hand-select', component_property='options'),
)
def toggle_panel(track_toggle, pr_options, cs_options, hand_options, ):
    for options in [pr_options, cs_options, hand_options, ]:
        for option in options:
            option['disabled'] = not track_toggle
    return pr_options, cs_options, hand_options, '', '', '', not track_toggle, not track_toggle


@app.callback(
    Output(component_id='download-dataframe-csv', component_property='data'),
    Input(component_id='download-btn', component_property='n_clicks'),
    State(component_id='stored-player-data', component_property='data'),
    State(component_id='stored-player-id', component_property='data'),
    prevent_initial_call=True,
)
def download_data(n_clicks, data, pid):
    return dcc.send_data_frame(pd.DataFrame(data).to_csv,
                               '%s_trackingdata.csv' % pid
                               )


@app.callback(
    Output(component_id='tracking-progress', component_property='value'),
    Output(component_id='tracking-progress', component_property='label'),
    Input(component_id='next-btn', component_property='n_clicks'),
    Input(component_id='previous-btn', component_property='n_clicks'),
    Input(component_id='update-btn', component_property='n_clicks'),
    Input(component_id='row-id', component_property='data'),
    State(component_id='tracked-cols', component_property='data'),
    State(component_id='stored-player-data', component_property='data'),
)
def update_tracking_progressbar(btn1, btn2, btn3, row, tracked_cols, data):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    df = pd.DataFrame(data)
    df = df.replace({np.nan: None})
    vals = []
    if changed_id.split('.')[0] in ['next-btn', 'previous-btn', 'update-btn', 'row-id']:
        for col in tracked_cols[:-1]:
            vals.append(df.iloc[row][col])
    while True:
        try:
            perct = round((len(vals) - vals.count(None) - vals.count('')) / len(vals) * 100, 1)
            return perct, str(perct) + '% of the Available Manual Data Tags have been added.'
        except:
            pass

@app.callback(
    Output(component_id="save-toast", component_property="is_open"),
    Output(component_id='no-save-toast', component_property="is_open"),
    Output(component_id='save-btn', component_property='disabled'),
    Input(component_id='save-btn', component_property='n_clicks'),
    State(component_id="save-toast", component_property="is_open"),
    State(component_id='stored-player-data', component_property='data'),
    State(component_id='stored-player-id', component_property='data'),
)
def save_data_to_sql(n_clicks, is_open, player_data, pid, ):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    print('saving triggered', changed_id)
    if 'save-btn' in changed_id:
        attempts = 0
        while attempts < 10:
            try:
                conn = engine_two.connect()
                conn.execute("""
                UPDATE nbatrackingdata
                SET pass_x = u.pass_x, pass_y = u.pass_y,
                pass_rec_x = u.pass_rec_x, pass_rec_y = u.pass_rec_y, pass_shotclock = u.pass_shotclock,
                catch_and_shoot = u.catch_and_shoot, pick_and_roll = u.pick_and_roll,
                handedness = u.handedness, courtside = u.courtside, pass_distance = u.pass_distance,
                pass_angle = u.pass_angle, pass_shot_distance = u.pass_shot_distance,
                direction = u.direction, pass_dist_range = u.pass_dist_range,
                num_dribbles = u.num_dribbles
                FROM newtrackeddata as u 
                WHERE u.row_id = nbatrackingdata.row_id""")
                conn.close()
                break
            except Exception as e:
                attempts+=1
                conn.close()
        if attempts == 10:
            return is_open, not is_open, is_open
        return not is_open, is_open, not is_open
    return False, False, False

if __name__ == '__main__':
    app.run_server(debug=True)