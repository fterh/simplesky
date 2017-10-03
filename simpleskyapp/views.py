import os
from django.shortcuts import render

import xml.etree.ElementTree as etree

import requests
from geopy.distance import vincenty

def index(request):
    #initialize
    api = (os.environ.get("API"))
    loc_list = ""
    req_baseurl = "http://api.nea.gov.sg/api/WebAPI/"
    req_payloads = {"keyref": api}

    #2-hour nowcast
    req_payloads["dataset"] = "2hr_nowcast"
    req_2h = requests.get("http://api.nea.gov.sg/api/WebAPI/", params = req_payloads)
    tree_2h = etree.XML(req_2h.text)
    forecastissue_2h = tree_2h.find("item").find("forecastIssue")
    print(forecastissue_2h.attrib["date"])

    #Populate location dropdown list
    weatherforecast_2h = tree_2h.find("item").find("weatherForecast")
    for child in weatherforecast_2h:
        #print(child.attrib["name"])
        loc_list += r"<option value=\"" + child.attrib["name"] + "\">" + child.attrib["name"] + "</option>"

    #24-hour forecast
    #4-day outlook


    return render(request, "index.html", {
        "loc_list": loc_list,
        "lastupdateddate_2h": forecastissue_2h.attrib["date"],
        "lastupdatedtime_2h": forecastissue_2h.attrib["time"],
        "output_2h": "filler",
    })
