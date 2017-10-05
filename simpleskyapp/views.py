import os
import datetime
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, Template

import pytz
import requests
from geopy.distance import vincenty

# declare global variables
loc_matrix_temp, loc_matrix_2h = [], []
api = (os.environ.get("API"))
req_headers = {"api-key": api}
now = datetime.datetime.now(pytz.timezone("Singapore")). \
    strftime("%Y-%m-%dT%H:%M:%S")

# temp
url_temp = "https://api.data.gov.sg/v1/environment/air-temperature"
req_payloads_temp = {"date_time": now}
req_temp = requests.get(url_temp, params=req_payloads_temp, headers=req_headers)
json_temp = json.loads(req_temp.text)

# 2-hour nowcast
url_2h = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
req_payloads_2h = {"date_time": now}
req_2h = requests.get(url_2h, params=req_payloads_2h, headers=req_headers)
json_2h = json.loads(req_2h.text)

def index(request):
    # populate loc_matrix_temp
    for station in json_temp["metadata"]["stations"]:
        loc_matrix_temp.append(
            {"id": station["id"],
            "lat": str(station["location"]["latitude"]),
            "long": str(station["location"]["longitude"])}
        )

    # generate locations list using 2h stations
    loc_list = '<option>Select</option>'
    for area in json_2h["area_metadata"]:

        loc_list += '<option value="' + area['name'] \
        + '" data-lat="' + str(area['label_location']['latitude']) \
        + '" data-long="' + str(area['label_location']['longitude']) + '">' \
        + area['name'] + '</option>'

        loc_matrix_2h.append(
            {"name": area["name"],
            "lat": area["label_location"]["latitude"],
            "long": area["label_location"]["longitude"]
            })

    return render(request, "index.html", {
        "loc_list": loc_list,
        #"lastupdateddate_2h": forecastissue_2h.attrib["date"],
        #"lastupdatedtime_2h": forecastissue_2h.attrib["time"],
        #"output_2h": "filler",
    })

def ajax(request):
    user_coords = (request.POST["lat"], request.POST["long"])

    # calculate distances to temp stations
    for station in loc_matrix_temp:
        station_coords = (station["lat"], station["long"])
        distance = vincenty(station_coords, user_coords).miles
        station["distance"] = distance

    locmatrix_sorted_temp = sorted(loc_matrix_temp, key=lambda x: x["distance"])

    # calculate distances to 2h stations
    for area in loc_matrix_2h:
        area_coords = (area["lat"], area["long"])
        distance = vincenty(area_coords, user_coords).miles
        area["distance"] = distance

    locmatrix_sorted_2h = sorted(loc_matrix_2h, key=lambda x: x["distance"])

    # temp
    temp, lastupdated_temp = "", ""
    for station in json_temp["items"][0]["readings"]:
        if station["station_id"] == locmatrix_sorted_temp[0]["id"]:
            temp = str(station["value"])
            break

    # 2-hour nowcast
    nowcast, lastupdated_2h = "", ""
    for area in json_2h["items"][0]["forecasts"]:
        if area["area"] == locmatrix_sorted_2h[0]["name"]:
            nowcast = area["forecast"]
            break

    lastupdated_2h = json_2h["items"][0]["update_timestamp"]

    response = {
        "location": locmatrix_sorted_2h[0]["name"], \
        "temp": temp, \
        "nowcast": nowcast, \
        "lastupdated_2h": lastupdated_2h
        }
    return HttpResponse(json.dumps(response))
