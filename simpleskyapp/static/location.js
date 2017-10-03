

$(document).ready(function() {

    // gets location
    // needs refinement in error handling
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(positionAcquired);
    } else {
        alert("Gelocation not supported");
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
        url = window.location + "ajax/";
        $.post(url, {lat: position.coords.latitude, long: position.coords.longitude}, function(data) { alert("success!"); });
    }


})
