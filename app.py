import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# Note: the follow two statements error out because neither of them has primary key.
# Measurement = Base.classes.measurement
# Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
## /: a) Home page. b) List all routes that are available
##
@app.route("/")
def index():
    return (
        f"Available Routes:<br/>"
        f"- Precipitation: /api/v1.0/precipitation<br/>"
        f"- Station List: /api/v1.0/stations<br/>"
        f"- Temperature for the Past Year: /api/v1.0/tobs<br/>"
        f"- Temperature info from the Start Date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"- Temperature info between the Start and End Date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
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
        precipitation_and_date.append(data_prcp_dict)

    session.close()
    return jsonify(precipitation_and_date)

if __name__ == '__main__':
    app.run(debug=True)
