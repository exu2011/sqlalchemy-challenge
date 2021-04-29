import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import os.path

##----------------------------------------------------------------------------------
# Database Setup
# Note: Need to use full path to the sqlite db. Relative Path doesn't work.
##----------------------------------------------------------------------------------
# db_path = 'users/eugene 1/Desktop/sqlalchemy-challenge/hawaii.sqlite'
# db_path = '\Desktop\SQLAlCHEMY-CHALLENGE\hawaii.sqlite'
# db_path = '/Users/eugene\ 1/Desktop/sqlalchemy-challenge/hawaii.sqlite'
# engine = sqlalchemy.create_engine('sqlite:///' + db_path)
engine = create_engine('sqlite:///./Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# print(Base.classes.keys())
print (Base.classes.keys())

# Save reference to the table
# Note: the follow two statements error out because neither of them has primary key.
Measurement = Base.classes.measurement
Station = Base.classes.station

##--------------------------------------------
# Flask Setup
##--------------------------------------------
app = Flask(__name__)

##--------------------------------------------
## Flask Routes: 
##  a) Home page. 
##  b) List all routes that are available
##--------------------------------------------

@app.route("/")
def index():
    return (
        f"Available Routes:<br/>"
        f"- Precipitation: /api/v1.0/precipitation<br/>"
        f"- Station List: /api/v1.0/stations<br/>"
        f"- Temperature for the Past Year: /api/v1.0/tobs<br/>"
        f"- Temperature Info from a Start Date: /api/v1.0/start_date<br/>"
        f"- Temperature Info between a Start and End Date: /api/v1.0/start_date/end_date"
    )

##-------------------------------------------------------------------------------------------
## /api/v1.0/precipitation: 
##   a) Convert the query results to a dictionary using date as the key and prcp as the value.
##   b) Return the JSON representation of your dictionary.
##-------------------------------------------------------------------------------------------
@app.route("/api/v1.0/precipitation")
def precipitation():
    ## Create our session (link) from Python to the DB
    session = Session(engine)

    ## Use the query developed in the precipitation analysis
    ## Get the most recent date in Measurement
    mostRecentDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    ## 1) Calculate the date 1 year ago from the last data point in the database
    mostRecentDate_obj = dt.datetime.strptime(mostRecentDate[0], '%Y-%m-%d')
    sqlQueryDate = dt.date(mostRecentDate_obj.year - 1, mostRecentDate_obj.month, mostRecentDate_obj.day)
    
    ## 2) Perform a query to retrieve the dat3 and precipitation scores
    sel = [Measurement.date, Measurement.prcp]
    date_precipitation_resultset = session.query(*sel).filter(Measurement.date >= sqlQueryDate).\
        order_by(Measurement.date).all()
    
    ## Convert the query results to a dictionary using date as the key and prcp as the value."""
    precipitation_and_date = []
    for date, prcp in date_precipitation_resultset:
        date_prcp_dict = {}
        date_prcp_dict['Date'] = date
        date_prcp_dict['Precipitation'] = prcp
        precipitation_and_date.append(date_prcp_dict)

    session.close()
    return jsonify(precipitation_and_date)

##----------------------------------------------------------------------
## /api/v1.0/stations: 
#   Return a JSON list of stations from the dataset.
## ---------------------------------------------------------------------
@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude ]
    results = session.query(*sel).all()
    session.close()

    ## Build a dict and print the results
    station_lst = []

    for station, name, lat, longi in results:
        station_list_dict = {}
        station_list_dict["Station"] = station
        station_list_dict["Name"] = name
        station_list_dict["Latitute"] = lat
        station_list_dict["Longitute"] = longi
        station_lst.append(station_list_dict)

    ## Convert list of tuples into normal list
    all_stations = list(np.ravel(station_lst))
    return jsonify(all_stations)

##---------------------------------------------------------------------------------------------------------
# /api/v1.0/tobs: 
#   a) Query the dates and temperature observations of the most active station for the last year of data.
#   b) Return a JSON list of temperature observations (TOBS) for the previous year.
##--------------------------------------------------------------------------------------------------------
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    
    ## use previously constructed SQL query to get the date: 
    ## Get the most recent date in Measurement
    mostRecentDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    ## 1) Calculate the date 1 year ago from the last data point in the database
    mostRecentDate_obj = dt.datetime.strptime(mostRecentDate[0], '%Y-%m-%d')
    sqlQueryDate = dt.date(mostRecentDate_obj.year - 1, mostRecentDate_obj.month, mostRecentDate_obj.day)
    
    ## 2) Perform a query to retrieve the dat3 and precipitation scores
    sel = [Measurement.date, Measurement.tobs]
    date_temp_resultset = session.query(*sel).filter(Measurement.date >= sqlQueryDate).\
        order_by(Measurement.date).all()
    session.close()

    tobs_info_lst = []
    for date, tobs in date_temp_resultset:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['Tobs'] = tobs
        tobs_info_lst.append(tobs_dict)
   
    return jsonify(tobs_info_lst)

##-----------------------------------------------------------------------------------------------------------------------------
# /api/v1.0/<start> and /api/v1.0/<start>/<end>: 
#   a) Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start 
#      or start-end range.
#   b) When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#   c) When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date 
#      inclusive.
##-----------------------------------------------------------------------------------------------------------------------------
@app.route('/api/v1.0/start_date')
def get_tobs_startdate():
    ## Pick a start date: 2017-04-01
    start_date = dt.date(2017, 4, 1)
    session = Session(engine)
    sel = [Measurement.date, 
        func.min(Measurement.tobs), 
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ]

    tobs_startdate_resultset = session.query(*sel).filter(Measurement.date >= start_date).\
        group_by(Measurement.date).order_by(Measurement.date).all()
    session.close()

    ## extract temperature and display it using jsonify
    tobs_lst = []
    for tdate, tmin, tavg, tmax in tobs_startdate_resultset:
        tobs_dict = {}
        tobs_dict['TDATE'] = tdate
        tobs_dict['TMIN'] = tmin
        tobs_dict['TAVG'] = tavg
        tobs_dict['TMAX'] = tmax
        tobs_lst.append(tobs_dict)

    return jsonify(tobs_lst)


@app.route('/api/v1.0/start_date/end_date')
def get_tobs_start_end_date():
    ## Pick a start and an end date: 2017-04-01 to 2017-04-08
    start_date = dt.date(2017, 4, 1)
    end_date = dt.date(2017, 4, 8)

    session = Session(engine)
    sel = [Measurement.date, 
        func.min(Measurement.tobs), 
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ]

    tobs_start_end_date_resultset = session.query(*sel).filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).group_by(Measurement.date).order_by(Measurement.date).all()
    session.close()

    ## extract temperature and display it using jsonify
    tobs_start_end_lst = []
    for tdate, tmin, tavg, tmax in tobs_start_end_date_resultset:
        tobs_dict = {}
        tobs_dict['TDATE'] = tdate
        tobs_dict['TMIN'] = tmin
        tobs_dict['TAVG'] = tavg
        tobs_dict['TMAX'] = tmax
        tobs_start_end_lst.append(tobs_dict)

    return jsonify(tobs_start_end_lst)

if __name__ == '__main__':
    app.run(debug=True)
