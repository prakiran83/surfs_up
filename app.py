# ----- Import  dependencies -----
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# ----- Set up the Database -----
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# ----- Set up Flask -----
app = Flask(__name__)
#"Instance" is a general term in programming to refer to a singular version of something
#The __name__ variable denotes the name of the function
#Variables with underscores before and after them are called magic methods in Python

#Define the stating point or root
#The foward slash denotates tht we we want to put our data at the root of our routes
@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')
#When creating routes, we follow the naming convention /api/v1.0/ followed by the name of the route.
#This convention signifies that this is version 1 of our application.

# ----- Precipation Route -----
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)
#prev_year allows us to calculate the date one year ago from the most recent date in the database.
#.\ signifies that we want our query to continue on the next line.

# ----- Stations Route -----
#Start by unravelling the results into a one-dimensional array.
#Then, convert the unraveled results into a list using list() and jsonify it.
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)
#.all() allows us to retrieve all the stations in the database.


# ----- Monthly Temperature Route -----
#Query the primary station for all the temperature observations from the previous year.
#Then, unravel the results into an array, covert the array into a list, then jsonify
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.unravel(results))
    return jsonify(temps=temps)

# ----- Statistics Route -----
#Create a query to select the minimum, average, and maximum temperatures
#To determine the starting and ending date, add an if-not statement.
#The asterik here is used to indicate there will be multiple results for the query: min, avg, and max
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
#Calculate the temp min, avg, and max with the start and end dates. Use the sel list.
    results = session.query(*sel).\
         filter(Measurement.date >= start).\
         filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)