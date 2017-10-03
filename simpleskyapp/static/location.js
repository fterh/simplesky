if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(loadPosition);
} else {
    alert("Gelocation not supported");
}

function loadPosition(position) {
    document.getElementById("latitude").innerHTML = position.coords.latitude;
    document.getElementById("longitude").innerHTML = position.coords.longitude;
}
