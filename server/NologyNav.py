import os
import sys
import json
import requests
from dotenv import load_dotenv
from flask import Flask, request, render_template

from NologyNav_Methods import retrieve_data_from_google, count_waypoints, distance_travelled, total_time, lat_lng, avg_speed, modes_of_transportation, summary

def create_app():
    app = Flask(__name__, static_folder="../static", template_folder='../templates/')

    @app.route("/")
    def index():
        return render_template('index.html')
    
    @app.route("/get_summary", methods=["POST"], endpoint='get_summary')
    def get_summary():
        locations = request.get_json()
        navigation_data = retrieve_data_from_google(locations) 
        navigation_response = {}

        if "error" in navigation_data:
            return json.dumps(navigation_data, indent=4), 406
        
        navigation_response["origin"] = locations["origin"]
        navigation_response["destination"] = locations["destination"]
        navigation_response["waypoints"] = count_waypoints(navigation_data)
        navigation_response["distance_travelled"] = distance_travelled(navigation_data)
        navigation_response["total_time"] = total_time(navigation_data)
        navigation_response["lat_lng"] = lat_lng(navigation_data)
        navigation_response["avg_speed"] = avg_speed(navigation_data)
        navigation_response["modes_of_transportation"] = modes_of_transportation(navigation_data)
        navigation_response["summary"] = summary(navigation_response)

        return json.dumps(navigation_response, indent=4), 200        

    return app

app = create_app()
            