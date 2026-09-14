const sosButton = document.getElementById("sosButton");
const message = document.getElementById("message");

function getCSRFToken() {
    const meta = document.querySelector(
        'meta[name="csrf-token"]'
    );

    return meta ? meta.getAttribute("content") : "";
}

sosButton.addEventListener("click", function () {

    message.innerText = "📍 Getting your location...";

    if (!navigator.geolocation) {
        message.innerText =
            "❌ Location services are not supported by this browser.";
        return;
    }

    navigator.geolocation.getCurrentPosition(

        function (position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            message.innerText =
                "📍 Location received. Creating emergency alert...";

            fetch("/api/sos", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude
                })
            })

            .then(response => response.json())

            .then(data => {

                if (data.success) {

                    message.innerText =
                        "🚨 Emergency Created! Incident ID: " +
                        data.incident_id +
                        " | Status: " +
                        data.status;

                } else {

                    message.innerText =
                        "❌ " + data.message;

                }

            })

            .catch(error => {

                console.error(error);

                message.innerText =
                    "❌ Unable to contact the SafeShield server.";

            });

        },

        function (error) {

            message.innerText =
                "❌ Location permission is required to activate SOS.";

            console.error(error);

        }

    );

});