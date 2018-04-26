# import dependencies
import datetime as dt 
import numpy as np 
import pandas as pd 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, Markup

#####################################################################
# Database setup
#####################################################################

engine = create_engine("sqlite:///hawaii3.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.hawaii_measurement
Stations = Base.classes.stations 

# Create a session
session = Session(engine)

####################################################################
# Flask Setup

app = Flask(__name__)

####################################################################
# Flask Routes

@app.route("/")
def welcome():
    return (
        f" <b>Available Routes:</b><br>"
        f" Precipitation Data for previous year :<b> /api/v1.0/precipitation </b><br>"
        f" Names of Stations for which data is available : <b> /api/v1.0/stations </b><br>"
        f" Temperature Observations for the previous year : <b>/api/v1.0/tobs</b><br>"
        f" Min, Max and Avg Temp observations for dates greater than requested date :<b> /api/v1.0/'<'start-date'>'</b><br>"
        f" Min, Max and Avg Temp observations for a given date range : <b>/api/v1.0/'<'start'>'/'<'end'>' </b> <br>"
        f" <i> Copy the route and append it to the URL to see the respective data.</i><br>"
        f" Date format to be used in the URL for start and end dates : <b>yyyy-mm-dd</b>" 
    )


# route : /api/v1.0/precipitation
    # Query for the dates and temperature observations from the last year.
    # Convert the query results to a Dictionary using date as the key and tobs as the value.
    # Return the json representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).filter((Measurement.date > '2016-12-31') & (Measurement.date < '2018-01-01') & (Measurement.prcp > 0)).all()
    return (jsonify(dict(results)))


# route : /api/v1.0/stations
    #  Return a json list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    results = []
    #Query unique stations in Measurements Table.
    stations_data = session.query(Measurement.station).distinct(Measurement.station).all()
    # for unique stations in Measurement, query the stations table to retrieve the station name
    for station in stations_data:
        station_name = session.query(Stations.station,Stations.name).filter(Stations.station == station[0]).all()
        results.append(station_name[0])

    return jsonify(dict(results))
    
    
# route : /api/v1.0/tobs
    # Return a json list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.date > '2016-12-31') & (Measurement.date < '2018-01-01') ).all()
    return (jsonify(dict(results)))


# route : /api/v1.0/<start> 
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def single_stats(start):
    stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date > start).all()
    stats_dict = {'Min': stats[0][0], 'Max': stats[0][1], 'Average': stats[0][2]}
    return jsonify(stats_dict)


# route : /api/v1.0/<start>/<end>
    # Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.  
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def stats(start, end):
    stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter((Measurement.date > start)& (Measurement.date < end)).all()
    stats_dict = {'Min': stats[0][0], 'Max': stats[0][1], 'Average': stats[0][2]}
    return jsonify(stats_dict)

if __name__ == "__main__" :
    app.run(debug=True)
