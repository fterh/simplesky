import os
import datetime
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, Template

import pytz
import requests
from geopy.distance import vincenty

def index(request):
    # initialize
    api = (os.environ.get("API"))
    req_headers = {"api-key": api}
    loc_list = ""
    loc_matrix = []
    now = datetime.datetime.now(pytz.timezone("Singapore")). \
        strftime("%Y-%m-%dT%H:%M:%S")

    # 2-hour nowcast
    url_2h = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
    req_payloads = {"date_time": now}
    req_2h = requests.get(url_2h, params=req_payloads, headers=req_headers)
    json_2h = json.loads(req_2h.text)

    # location magic
    i = 0
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
    context = RequestContext(request)
    return HttpResponse(template.render(context))
