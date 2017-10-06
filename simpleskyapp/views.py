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
loc_matrix_temp, loc_matrix_rh, loc_matrix_2h = [], [], []
api = (os.environ.get("API"))
req_headers = {"api-key": api}
now = datetime.datetime.now(pytz.timezone("Singapore")). \
    strftime("%Y-%m-%dT%H:%M:%S")
print(now) #to remove

# temp
url_temp = "https://api.data.gov.sg/v1/environment/air-temperature"
req_payloads_temp = {"date_time": now}
req_temp = requests.get(url_temp, params=req_payloads_temp, headers=req_headers)
json_temp = json.loads(req_temp.text)

# relative humidity
url_rh = "https://api.data.gov.sg/v1/environment/relative-humidity"
req_payloads_rh = {"date_time": now}
req_rh = requests.get(url_rh, params=req_payloads_rh, headers=req_headers)
json_rh = json.loads(req_rh.text)

# PSI
url_psi = "https://api.data.gov.sg/v1/environment/psi"
req_payloads_psi = {"date_time": now}
req_psi = requests.get(url_psi, params=req_payloads_psi, headers=req_headers)
json_psi = json.loads(req_psi.text)
psi_north = json_psi["items"][0]["readings"]["psi_twenty_four_hourly"]["north"]
psi_south = json_psi["items"][0]["readings"]["psi_twenty_four_hourly"]["south"]
psi_east = json_psi["items"][0]["readings"]["psi_twenty_four_hourly"]["east"]
psi_west = json_psi["items"][0]["readings"]["psi_twenty_four_hourly"]["west"]
psi_central = json_psi["items"][0]["readings"]["psi_twenty_four_hourly"]["central"]

# PM2.5
url_pm25 = "https://api.data.gov.sg/v1/environment/pm25"
req_payloads_pm25 = {"date_time": now}
req_pm25 = requests.get(url_pm25, params=req_payloads_pm25, headers=req_headers)
json_pm25 = json.loads(req_pm25.text)
pm25_north = json_pm25["items"][0]["readings"]["pm25_one_hourly"]["north"]
pm25_south = json_pm25["items"][0]["readings"]["pm25_one_hourly"]["south"]
pm25_east = json_pm25["items"][0]["readings"]["pm25_one_hourly"]["east"]
pm25_west = json_pm25["items"][0]["readings"]["pm25_one_hourly"]["west"]
pm25_central = json_pm25["items"][0]["readings"]["pm25_one_hourly"]["central"]

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

    # populate loc_matrix_rh
    for station in json_rh["metadata"]["stations"]:
        loc_matrix_rh.append(
            {"id": station["id"],
            "lat": str(station["location"]["latitude"]),
            "long": str(station["location"]["longitude"])}
        )

    # generate dropdown list of locations using 2h stations
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
        "psi_north": psi_north,
        "psi_south": psi_south,
        "psi_east": psi_east,
        "psi_west": psi_west,
        "psi_central": psi_central,
        "pm25_north": pm25_north,
        "pm25_south": pm25_south,
        "pm25_east": pm25_east,
        "pm25_west": pm25_west,
        "pm25_central": pm25_central
    })

def ajax(request):
    user_coords = (request.POST["lat"], request.POST["long"])

    # calculate distances to temp stations
    for station in loc_matrix_temp:
        station_coords = (station["lat"], station["long"])
        distance = vincenty(station_coords, user_coords).miles
        station["distance"] = distance

    locmatrix_sorted_temp = sorted(loc_matrix_temp, key=lambda x: x["distance"])

    # calculate distances to relative humidity stations
    for station in loc_matrix_rh:
        station_coords = (station["lat"], station["long"])
        distance = vincenty(station_coords, user_coords).miles
        station["distance"] = distance

    locmatrix_sorted_rh = sorted(loc_matrix_rh, key=lambda x: x["distance"])

    # calculate distances to 2h stations
    for area in loc_matrix_2h:
        area_coords = (area["lat"], area["long"])
        distance = vincenty(area_coords, user_coords).miles
        area["distance"] = distance

    locmatrix_sorted_2h = sorted(loc_matrix_2h, key=lambda x: x["distance"])

    # temp
    temp = ""
    for station in json_temp["items"][0]["readings"]:
        if station["station_id"] == locmatrix_sorted_temp[0]["id"]:
            temp = str(station["value"])
            break

    # relative humidity
    rh = ""
    for station in json_rh["items"][0]["readings"]:
        if station["station_id"] == locmatrix_sorted_rh[0]["id"]:
            rh = str(station["value"])
            break

    # 2-hour nowcast
    nowcast = ""
    for area in json_2h["items"][0]["forecasts"]:
        if area["area"] == locmatrix_sorted_2h[0]["name"]:
            nowcast = area["forecast"]
            break

    response = {
        "location": locmatrix_sorted_2h[0]["name"], \
        "temp": temp + "&deg;C", \
        "rh": rh + "%", \
        "nowcast": nowcast, \
    }
    return HttpResponse(json.dumps(response))
