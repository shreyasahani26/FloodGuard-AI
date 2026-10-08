// ---------------------------------------------------------
// FLOODGUARD AI FRONTEND
// ---------------------------------------------------------

const zoneSelect =
    document.getElementById("zoneSelect");

const rainfallSlider =
    document.getElementById("rainfall");

const rainfallValue =
    document.getElementById("rainfallValue");

const riskScore =
    document.getElementById("riskScore");

const riskCategory =
    document.getElementById("riskCategory");

const recommendations =
    document.getElementById("recommendations");


// ---------------------------------------------------------
// MAP
// ---------------------------------------------------------

const map = L.map("map").setView(
    [28.6469, 77.3160],
    10
);


L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


const zoneData = {
    "Anand Vihar": [28.6469, 77.3160],
    "Noida Sector 62": [28.6270, 77.3649],
    "Ghaziabad": [28.6692, 77.4538],
    "Delhi Gate": [28.6405, 77.2409],
    "Dwarka": [28.5921, 77.0460],
    "Gurugram": [28.4595, 77.0266]
};


const markers = {};


Object.entries(zoneData).forEach(
    ([name, coordinates]) => {

        const marker =
            L.circleMarker(
                coordinates,
                {
                    radius: 10,
                    color: "#ffb84d",
                    fillColor: "#ffb84d",
                    fillOpacity: 0.85,
                    weight: 2
                }
            ).addTo(map);

        marker.bindPopup(
            `<b>${name}</b><br>
             FloodGuard monitoring zone`
        );

        markers[name] = marker;
    }
);


// ---------------------------------------------------------
// RAINFALL SLIDER
// ---------------------------------------------------------

rainfallSlider.addEventListener(
    "input",
    () => {

        rainfallValue.textContent =
            rainfallSlider.value;

    }
);


// ---------------------------------------------------------
// PREDICTION
// ---------------------------------------------------------

async function predictRisk() {

    const zone =
        zoneSelect.value;

    const rainfall =
        Number(rainfallSlider.value);


    riskScore.textContent =
        "...";


    try {

        const response =
            await fetch(
                "/api/predict",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        zone,
                        rainfall
                    })
                }
            );


        const data =
            await response.json();


        if (data.error) {

            alert(data.error);

            return;
        }


        riskScore.textContent =
            Math.round(data.risk);


        riskCategory.textContent =
            data.category;


        recommendations.innerHTML =
            "";


        data.recommendations.forEach(
            item => {

                const li =
                    document.createElement("li");

                li.textContent =
                    item;

                recommendations.appendChild(li);

            }
        );


        updateMarker(
            zone,
            data.risk
        );


        document.getElementById(
            "heroRisk"
        ).textContent =
            `${Math.round(data.risk)}%`;


        document.getElementById(
            "heroCategory"
        ).textContent =
            `${data.category} RISK`;

    }

    catch (error) {

        console.error(error);

        alert(
            "Prediction failed. Check the server."
        );

    }
}


// ---------------------------------------------------------
// MARKER COLOR
// ---------------------------------------------------------

function updateMarker(
    zone,
    risk
) {

    let color =
        "#55d98c";


    if (risk >= 30) {
        color = "#f2cf55";
    }

    if (risk >= 55) {
        color = "#ff9d4d";
    }

    if (risk >= 75) {
        color = "#ff5d65";
    }


    markers[zone].setStyle({
        color,
        fillColor: color
    });


    markers[zone].openPopup();

}


// ---------------------------------------------------------
// SIMULATION
// ---------------------------------------------------------

function setRainfall(value) {

    rainfallSlider.value =
        value;

    rainfallValue.textContent =
        value;

    predictRisk();

}


function runDemo() {

    document.getElementById(
        "dashboard"
    ).scrollIntoView();

    rainfallSlider.value =
        80;

    rainfallValue.textContent =
        80;

    predictRisk();

}


// ---------------------------------------------------------
// AI ASSISTANT
// ---------------------------------------------------------

async function askAI(question) {

    document.getElementById(
        "question"
    ).value = question;

    await sendQuestion();

}


async function sendQuestion() {

    const input =
        document.getElementById(
            "question"
        );

    const question =
        input.value.trim();


    if (!question) {
        return;
    }


    addMessage(
        "You",
        question,
        "user"
    );


    input.value = "";


    const zone =
        zoneSelect.value;


    const rainfall =
        Number(
            rainfallSlider.value
        );


    try {

        const response =
            await fetch(
                "/api/assistant",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question,
                        zone,
                        rainfall
                    })
                }
            );


        const data =
            await response.json();


        addMessage(
            "FloodGuard AI",
            data.answer,
            "ai"
        );

    }

    catch (error) {

        addMessage(
            "FloodGuard AI",
            "Unable to reach the AI service.",
            "ai"
        );

    }

}


function addMessage(
    sender,
    message,
    type
) {

    const chat =
        document.getElementById(
            "chat"
        );


    const div =
        document.createElement(
            "div"
        );


    div.className =
        `message ${type}`;


    div.innerHTML = `
        <strong>${sender}</strong>
        <p>${message}</p>
    `;


    chat.appendChild(div);


    chat.scrollTop =
        chat.scrollHeight;

}


function handleEnter(event) {

    if (event.key === "Enter") {

        sendQuestion();

    }

}


function scrollToDashboard() {

    document.getElementById(
        "dashboard"
    ).scrollIntoView({
        behavior: "smooth"
    });

}


// ---------------------------------------------------------
// INITIAL PREDICTION
// ---------------------------------------------------------

window.addEventListener(
    "load",
    () => {

        setTimeout(
            () => {
                predictRisk();
            },
            500
        );

    }
);