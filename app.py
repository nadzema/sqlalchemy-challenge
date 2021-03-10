#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
# Python SQL toolkit and Object Relational Mapper
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc
import matplotlib.pyplot as plt


# In[2]:


# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# In[3]:


# reflect an existing database into a new model
Database = automap_base()


# In[4]:


# reflect the tables
Database.prepare(engine, reflect=True)


# In[5]:


# View all of the classes that automap found
Database.classes.keys()


# In[6]:


# Save references to each table
Measurement = Database.classes.measurement
Station = Database.classes.station


# In[7]:


# Create our session (link) from Python to the DB
session = Session(bind=engine)
inspector = inspect(engine)


# In[8]:


inspector.get_columns('measurement')


# In[9]:


app = Flask(__name__)


# In[10]:


@app.route("/")
def page():
   return (
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/<start><br/>"
       f"/api/v1.0/<start>/<end><br/>"
) 


# In[11]:


@app.route("/api/v1.0/precipitation")
def precip():
    
    session = Session(bind=engine)
    
    # STEP 1: Starting from the most recent data point in the database. 
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # STEP 2: Calculate the date one year from the last date in data set.
    twelvemo = dt.datetime.strptime(recent_date[0],'%Y-%m-%d') - dt.timedelta(days=365)

    # STEP 3: Perform a query to retrieve the data and precipitation scores
    precip12mo = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > twelvemo).all()
    
    
    # STEP 4: Save the query results as a Pandas DataFrame and set the index to the date column
    precip_df = pd.DataFrame(precip12mo, columns = ['date', 'prcp'])


    # STEP 5: Sort the dataframe by date
    precip_df.set_index('date').sort_values('date', ascending=False)
   
    #Step 5b: Find max precipitation within twelve months
    prec_max = max(precip_df['prcp'])
    
    #Step 5c: For loop each output with Year-Month
    year_month = []
    for date in precip_df['date']:
        year_month.append(date[0:7])
    precip_df ['year_month'] = year_month
   
    #append a  list to return jsonify
    precip_json = []
    for date, prcp in precip12mo:
        precip_dict = {date: prcp}
        precip_json.append(precip_dict)
    return jsonify(precip_json)

    session.close()


# In[12]:


@app.route
def station():
    session = Session(bind=engine)
    station_json = []
    active_stations = session.query(Station.name).all()
    
    for place in active_stations:
        station_json.append(place)
        
    return jsonify(station_json)
    
    session.close()


# In[16]:


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(bind=engine)
    
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    active_id = active_stations[0][0]
    name_station = session.query(Station.name).filter_by(station = active_id)
    year_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == active_id).filter(Measurement.date > twelvemo).order_by(Measurement.date).all()
    
    active_stations_json = []
    
    for date, tobs in year_temp:
        tobs_dict = {date: tobs}
        active_stations_json.append(tobs_dict)
    return jsonify(active_stations_json)
    
    session.close()


# In[17]:


@app.route("/api/v1.0/<start>")
def start():
    
    session = Session(bind=engine)
    
    start = '2011-05-06'
    end = '2016-05-23'
    
    min_date = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start).all()[0][0]
    
    max_date = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start).all()[0][0]
    
    avg_date = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).all()[0][0]
    
    calc_date_dict = {'Min Temp':min_date, 'Max Temp':max_date, 'Avg Temp':avg_date}
    
    return jsonify(calc_date_dict)

    session.close()


# In[18]:


@app.route("/api/v1.0/<start>/<end>")
def start_end():
    
    session = Session(bind=engine)
    
    start = '2011-05-06'
    end = '2016-05-23'
    
    min_date = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).all()[0][0]
    
    max_date = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).all()[0][0]
    
    avg_date = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).all()[0][0]
    
    calc_date_dict = {'Min Temp':min_date, 'Max Temp':max_date, 'Avg Temp':avg_date}
    
    return jsonify(calc_date_dict)

    session.close()


# In[19]:


if __name__ == '__main__':
    app.run(debug=True)


# In[ ]:




