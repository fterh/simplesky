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
loc_matrix = []
api = (os.environ.get("API"))
req_headers = {"api-key": api}
now = datetime.datetime.now(pytz.timezone("Singapore")). \
    strftime("%Y-%m-%dT%H:%M:%S")

# 2-hour nowcast
url_2h = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
req_payloads = {"date_time": now}
req_2h = requests.get(url_2h, params=req_payloads, headers=req_headers)
json_2h = json.loads(req_2h.text)

def index(request):
    # location magic
    loc_list = ""
    for area in json_2h["area_metadata"]:
        loc_list += "<option value=\"" + area["name"] + "\">" + area["name"] \
            + "</option>"

        loc_matrix.append(
            {"name": area["name"],
            "lat": area["label_location"]["latitude"],
            "long": area["label_location"]["longitude"]
            })

    #print(json_2h["area_metadata"][0]["name"])

    #tree_2h = etree.XML(req_2h.text)
    #forecastissue_2h = tree_2h.find("item").find("forecastIssue")
    #print(forecastissue_2h.attrib["date"])

    # location magic
        #for i in range(0, 4):
            #loc_matrix[] =

        #i++

    #24-hour forecast
    #4-day outlook


    return render(request, "index.html", {
        "loc_list": loc_list,
        #"lastupdateddate_2h": forecastissue_2h.attrib["date"],
        #"lastupdatedtime_2h": forecastissue_2h.attrib["time"],
        #"output_2h": "filler",
    })

def ajax(request):
    # calculate distances to stations
    for area in loc_matrix:
        area_coords = (area["lat"], area["long"])
        user_coords = (request.POST["lat"], request.POST["long"])
        distance = vincenty(area_coords, user_coords).miles
        area["distance"] = distance

    locmatrix_sorted = sorted(loc_matrix, key=lambda x: x["distance"])

    # 2-hour nowcast
    nowcast, lastupdated_2h = "", ""
    for area in json_2h["items"][0]["forecasts"]:
        if area["area"] == locmatrix_sorted[0]["name"]:
            nowcast = area["forecast"]
            break

    lastupdated_2h = json_2h["items"][0]["update_timestamp"]

    response = {
        "location": locmatrix_sorted[0]["name"], \
        "nowcast": nowcast, \
        "lastupdated_2h": lastupdated_2h
        }
    return HttpResponse(json.dumps(response))
