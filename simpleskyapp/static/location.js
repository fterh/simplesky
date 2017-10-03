$(document).ready(function() {

    // gets location
    // needs refinement in error handling
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(positionAcquired, showError);
    } else {
        alert("Geolocation is not supported by this browser; please select location manually");
    }

    // location errors
    function showError(error) {
        switch (error.code) {
            case error.PERMISSION_DENIED:
                alert("Unable to get your location; please select location manually");
                break;
            case error.POSITION_UNAVAILABLE:
                alert("Unable to get your location; please select location manually");
                break;
            case error.TIMEOUT:
                alert("Unable to get your location; please select location manually");
                break;
            case error.UNKNOWN_ERROR:
                alert("Unknown error; please select location manually");
        }
    }

    // position acquired
    function positionAcquired(position) {
        displayPosition(position);
        postLocation(position);
    }

    // displays location
    function displayPosition(position) {
        $("#latitude").html(position.coords.latitude);
        $("#longitude").html(position.coords.longitude);
    }

    // POSTs location
    function postLocation(position) {
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
        ajax(position, csrftoken);
    }

        // AJAX
    function ajax(position, csrftoken) {
        url = window.location + "ajax/";
        $.ajax({
            method: "POST",
            url: url,
            headers: {"X-CSRFToken": csrftoken},
            data: {"lat": position.coords.latitude,
                "long": position.coords.longitude}
        }).done(function(data) {
            json = JSON.parse(data)
            $("#location").html(json["location"]);
            $("#nowcast").html(json["nowcast"]);
            $("#lastupdated_2h").html(json["lastupdated_2h"]);
        })
    }

    // manual location selection
        // nowcast
    $("#select_2h").change(function() {
        val = $(this).val();
        
    })
})