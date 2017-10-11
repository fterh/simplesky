$(document).ready(function() {

    // gets location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(positionAcquired, showError);
    } else {
        alert("Geolocation is not supported by this browser; please select location manually");
    }

    // location errors
    function showError(error) {
        switch (error.code) {
            case error.PERMISSION_DENIED:
                alert("Unable to get your location (permission denied); please select location manually");
                break;
            case error.POSITION_UNAVAILABLE:
                alert("Unable to get your location (position unavailable); please select location manually");
                break;
            case error.TIMEOUT:
                alert("Unable to get your location (timeout); please select location manually");
                break;
            case error.UNKNOWN_ERROR:
                alert("Unknown error; please select location manually");
        }
    }

    // position acquired
    function positionAcquired(position) {
        displayPosition(position);
        postLocation(position, false);
    }

    // displays location
    function displayPosition(position) {
        $("#latitude").html(position.coords.latitude);
        $("#longitude").html(position.coords.longitude);
    }

    // POSTs location
    function postLocation(position, user_select) {
        // CSRF
        var cookieValue = null;
        var name = "csrftoken";
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    var csrftoken = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        ajax(position, csrftoken, user_select);
    }

    // loads data into page
    function loadData(data) {
        json = JSON.parse(data)
        lastupdated_text_start = "Updated: <time>";
        lastupdated_text_end = "</time>"
        $("#location").html(json["location"]);
        $("#temp").html(json["temp"]);
        $("#rh").html(json["rh"]);
        $("#nowcast").html(json["nowcast"]);
    }

    // AJAX
    function ajax(position, csrftoken, user_select) {
        url = window.location + "ajax/";

        if (user_select == false) {
            $.ajax({
                method: "POST",
                url: url,
                headers: {"X-CSRFToken": csrftoken},
                data: {"lat": position.coords.latitude,
                    "long": position.coords.longitude}
            }).done(function(data) {
                loadData(data);
            })
        }

        else if (user_select == true) {
            $.ajax({
                method: "POST",
                url: url,
                headers: {"X-CSRFToken": csrftoken},
                data: {"lat": position["lat"],
                    "long": position["long"]}
            }).done(function(data) {
                loadData(data);
            })
        }
    }

    // manual location selection
        // nowcast
    $("#select_2h").change(function() {
        lat = $("#select_2h option:selected").attr("data-lat");
        long = $("#select_2h option:selected").attr("data-long");
        var position = [];
        position["lat"] = lat;
        position["long"] = long;
        postLocation(position, true);
    })
})
