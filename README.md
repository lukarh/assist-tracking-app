# assist-tracking-app

## Motivation

In the public realm, our access to spatial data is limited to shot coordinates. You've probably already seen the [beautiful visualizations](https://www.instagram.com/kirkgoldsberry/?hl=en) that Kirk Goldsberry has produced over the past few years with this data, but what about spatial data looking at pass coordinates? Passing is such an integral part of the game and [it's what makes the game so beautiful to watch](https://www.youtube.com/watch?v=NsBGF1fjXvY&ab_channel=EvinGualberto). So how can we visualize passing location data? Can we create any interesting player insights using pass coordinates the way shot charts do?

The lack of public access to this type of data motivated the development of this robust and user-friendly application. This web-based application allows users to manually hand-track pass coordinate data without having to deal with the logistics of data management or data manipulation themselves, while also having the capacity to track other data points not captured through tracking cameras via Second Spectrum in NBA Arenas.

## Development

- Code: Python
- Framework: Dash (A Python Framework)
- Libraries: Flask, SQLAlchemy, Plotly, Pandas, SQLite3, NumPy, Dash, Numpy, Dash Bootstrap, Dash Authentication
- Database: PostgreSQL via Heroku
- Deployment: Heroku

#### Useful Links
- [Dash DAQ](https://dash.plotly.com/dash-daq)
- [Dash Framework](https://plotly.com/dash/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

## Deployment
In a terminal at this directory, run the following command to install all necessary libraries / packages:

```pip install -r requirements.txt```

To test the app locally, run the following command:

```python dashboard-app.py```

Deploy the App to Heroku, use the [tutorial that outlines the instructions here](https://drive.google.com/file/d/1kowjMGKN6rbxh9n-5q1cP3BkcZ2yOAvo/view).

**NOTE: This Repository does not have access to database key**

## Application

The web-based application includes features such as:

#### Manual Play Tracking (Admin Access)
Users can view video playback of plays, manually track plays with new data tags, preview the data, and update the database all in one page. Other features include being able to switch between different players to track for using the dropdown menu and also skipping toward a specific play by specifying a specific video ID. Unfortunately, this page is unavailable to the public to maintain data authenticity and security.

Available Data Tags: Passer Location, Receiver Location, Handedness of Pass, Number of Dribbles Prior, Shotclock Left, Pick And Roll, Catch & Shoot

![tracking-ui](https://user-images.githubusercontent.com/65103724/163692808-90f4c48a-3e3b-4c8d-b4ca-1e19b0cd1792.png)

#### Live Dashboard for Player Reports
The Interactive Dashboard builds a player report showing their directional passing tendencies, passing hotspots on the floor, and preferred timing for passes during assist plays. Users can apply multiple filters such as opponent team, date, shot type created, shot clock, minute left in the period, etc. and the dashboard will dynamically update accordingly.

![dashboard-ui](https://user-images.githubusercontent.com/65103724/163692815-85a7d1e1-f601-417f-801c-277c355b471f.png)

#### Create User Login (Admin Access)
A simple create user feature was added to the application to provide certain users with admin access. While creating an account, the web application can automatically provide feedback as to whether or not the new login credentials are valid to create an access account with.

![login-ui](https://user-images.githubusercontent.com/65103724/163692813-f7f4f118-1137-4ca4-af5e-bd02189fdabc.gif)

###

## Data Source & Manipulation

Thanks to Darryl Blackport, the current available shot tracking data has been made accessible on his site at [tracking.pbpstats](tracking.pbpstats.com). That dataset was then filtered for all assisted shots and new columns were created to keep track of new data tags. The manual hand-tracking process was done for 8 players during the 2020-21 season (Julius Randle, Bam Adebayo, Nikola Jokic, Draymond Green, LeBron James, LaMelo Ball, Chris Paul, and James Harden), totaling to 2292 manually tracked data points.

## Implications
This application has the capacity to keep track of data points not recorded via the tracking cameras via Second Spectrum. (e.g. limbs, handedness of passes, etc.) Furthermore, this application has the possibility to be scaled upwards and distributed to teams, trainers, and coaches, who do not have the money to install tracking cameras at their gym provided that they have parsed video footage of gameplay.

## Future Development / Considerations
- Squash any bugs
- Create an audit log of changes by user
- Animated Diagrams
- Improve Code Readability
- Better Visualizations
- Add additional features such as drag / drop to expand SQL database with .csv file

## Analysis

Please click here for the article showcasing the analysis.

## [View the application](https://tracking-dashboard-app.herokuapp.com/home)

Note: It might take awhile to load.
