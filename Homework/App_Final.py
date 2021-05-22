import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
sqlLite = "../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{sqlLite}")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    output = (
        f"THIS IS A FUN PAGE!!!!<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startDate       (format: 'yyyy-mm-dd')<br/>"
        f"/api/v1.0/startDate/endDate       (formats: 'yyyy-mm-dd')"
    )
    return (output)

#########################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # ADDING DATE FITERING AS THE RUBIC SAYS IT'S NEEDED.  THIS WAS NOT CLEAR IN THE INSTRUCTIONS
    # Get max date
    row = session.query(func.max(measurement.date)).all()

    # Set variables to pass into the main query
    maxDate = row[0][0]

    beginDate = dt.datetime.strptime(str(maxDate), "%Y-%m-%d") - dt.timedelta(days=365)
    beginDate.strftime("%Y-%m-%d")
        
    # Query all measurement
    results = session.query(measurement.date, measurement.prcp) \
                        .filter(measurement.date >= beginDate) \
                        .order_by(measurement.date) \
                        .all()

    # Close session
    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    all_prcps = []
    for date, prcp in results:
        prcps_dict = {}
        prcps_dict[date] = prcp
        all_prcps.append(prcps_dict)

    return jsonify(all_prcps)

#########################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all station names
    results = session.query(station.name).all()

    # Close session
    session.close()

    #Append list of names together
    all_names = []
    for name in results:
        name_dict = {}
        name_dict["station"] = name
        all_names.append(name_dict)

    return jsonify(all_names)

#########################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get most active station with its max date
    row = session.query(measurement.station \
                        ,func.count(measurement.station)
                        ,func.max(measurement.date) )\
                .group_by(measurement.station) \
                .order_by(desc(func.count(measurement.station))).all()

    # Set variables to pass into the query
    activeStation = row[0][0]
    maxDate = row[0][2]

    beginDate = dt.datetime.strptime(str(maxDate), "%Y-%m-%d") - dt.timedelta(days=365)
    beginDate.strftime("%Y-%m-%d")

    # Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(measurement.date \
                            ,measurement.tobs) \
                    .filter_by(station = activeStation) \
                    .filter(measurement.date >= beginDate) \
                    .all()

    # Capture and append results into list of dicts
    all_temps = []
    for date, temp in results:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["temp"] = temp
        all_temps.append(temps_dict)

    # Close session
    session.close()

    return jsonify(all_temps)

#########################################
@app.route("/api/v1.0/<start>")
def getsTempStart(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to get the results by the start date
    results = session.query(func.min(measurement.tobs).label("tmin") \
                            ,func.max(measurement.tobs).label("tmax")  \
                            ,func.round(func.avg(measurement.tobs),1).label("tavg") ) \
                    .filter(measurement.date >= start) \
                    .all()

        # Capture and append results into list of dicts
    all_temps = []
    for tmin, tmax, tavg in results:
        temps_dict = {}
        temps_dict["tmin"] = tmin
        temps_dict["tmax"] = tmax
        temps_dict["tavg"] = tavg
        all_temps.append(temps_dict)

     # Close session
    session.close()

    return jsonify(all_temps)

#########################################
@app.route("/api/v1.0/<start>/<end>")
def getsTempRange(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to get the results by the start date
    results = session.query(func.min(measurement.tobs).label("tmin") \
                            ,func.max(measurement.tobs).label("tmax")  \
                            ,func.round(func.avg(measurement.tobs),1).label("tavg") ) \
                    .filter(measurement.date.between(start,end)) \
                    .all()

        # Capture and append results into list of dicts
    all_temps = []
    for tmin, tmax, tavg in results:
        temps_dict = {}
        temps_dict["tmin"] = tmin
        temps_dict["tmax"] = tmax
        temps_dict["tavg"] = tavg
        all_temps.append(temps_dict)

     # Close session
    session.close()

    return jsonify(all_temps)


if __name__ == '__main__':
    app.run(debug=True)
