from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import requests
import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError


app = Flask(__name__)


# ---------------------------------------------------------
# LOAD ML MODEL
# ---------------------------------------------------------

MODEL_PATH = "model/flood_model.joblib"

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
FEATURES = model_data["features"]


# ---------------------------------------------------------
# DEFAULT LOCATION DATA
# ---------------------------------------------------------

ZONES = {
    "Anand Vihar": {
        "lat": 28.6469,
        "lng": 77.3160,
        "elevation": 35,
        "slope": 1.2,
        "builtup": 88,
        "drainage": 38,
        "road_density": 82,
        "historical_floods": 9,
        "soil_absorption": 28
    },

    "Noida Sector 62": {
        "lat": 28.6270,
        "lng": 77.3649,
        "elevation": 205,
        "slope": 2.1,
        "builtup": 82,
        "drainage": 55,
        "road_density": 75,
        "historical_floods": 6,
        "soil_absorption": 35
    },

    "Ghaziabad": {
        "lat": 28.6692,
        "lng": 77.4538,
        "elevation": 190,
        "slope": 2.5,
        "builtup": 78,
        "drainage": 48,
        "road_density": 70,
        "historical_floods": 7,
        "soil_absorption": 32
    },

    "Delhi Gate": {
        "lat": 28.6405,
        "lng": 77.2409,
        "elevation": 216,
        "slope": 3.0,
        "builtup": 91,
        "drainage": 42,
        "road_density": 90,
        "historical_floods": 10,
        "soil_absorption": 25
    },

    "Dwarka": {
        "lat": 28.5921,
        "lng": 77.0460,
        "elevation": 225,
        "slope": 2.8,
        "builtup": 75,
        "drainage": 64,
        "road_density": 62,
        "historical_floods": 4,
        "soil_absorption": 42
    },

    "Gurugram": {
        "lat": 28.4595,
        "lng": 77.0266,
        "elevation": 220,
        "slope": 3.2,
        "builtup": 84,
        "drainage": 46,
        "road_density": 79,
        "historical_floods": 8,
        "soil_absorption": 30
    }
}


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def classify_risk(score):

    if score < 30:
        return "LOW"

    if score < 55:
        return "MODERATE"

    if score < 75:
        return "HIGH"

    return "CRITICAL"


def get_recommendations(score):

    if score >= 75:
        return [
            "Avoid low-lying roads.",
            "Move vehicles to elevated parking.",
            "Authorities should inspect drainage infrastructure.",
            "Residents should prepare for temporary waterlogging."
        ]

    if score >= 55:
        return [
            "Avoid unnecessary travel.",
            "Monitor rainfall conditions.",
            "Check alternative routes.",
            "Inspect nearby drainage points."
        ]

    if score >= 30:
        return [
            "Stay alert during heavy rainfall.",
            "Monitor the risk map.",
            "Keep emergency contacts available."
        ]

    return [
        "Current flood risk is relatively low.",
        "Continue monitoring weather conditions."
    ]


def calculate_risk(zone, rainfall):

    features = [
        rainfall,
        rainfall * 2.1,
        rainfall * 3.7,
        zone["elevation"],
        zone["slope"],
        zone["builtup"],
        zone["drainage"],
        zone["road_density"],
        zone["historical_floods"],
        zone["soil_absorption"]
    ]

    prediction = model.predict(
        np.array(features).reshape(1, -1)
    )[0]

    prediction = float(np.clip(prediction, 0, 100))

    return prediction


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        zones=ZONES
    )


# ---------------------------------------------------------
# FLOOD PREDICTION API
# ---------------------------------------------------------

@app.route("/api/predict", methods=["POST"])
def predict():

    data = request.get_json()

    zone_name = data.get("zone", "Anand Vihar")
    rainfall = float(data.get("rainfall", 50))

    if zone_name not in ZONES:
        return jsonify({
            "error": "Unknown zone"
        }), 400

    zone = ZONES[zone_name]

    risk = calculate_risk(
        zone,
        rainfall
    )

    category = classify_risk(risk)

    recommendations = get_recommendations(risk)

    return jsonify({
        "zone": zone_name,
        "risk": round(risk, 1),
        "category": category,
        "rainfall": rainfall,
        "latitude": zone["lat"],
        "longitude": zone["lng"],
        "recommendations": recommendations
    })


# ---------------------------------------------------------
# LIVE WEATHER
# ---------------------------------------------------------

@app.route("/api/weather")
def weather():

    lat = request.args.get("lat", "28.6469")
    lng = request.args.get("lng", "77.3160")

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lng}"
        "&current=temperature_2m,relative_humidity_2m,"
        "precipitation,rain,wind_speed_10m"
        "&hourly=precipitation"
        "&forecast_days=1"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return jsonify(response.json())

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# AI ENVIRONMENTAL ASSISTANT
# ---------------------------------------------------------

@app.route("/api/assistant", methods=["POST"])
def assistant():

    data = request.get_json()

    question = data.get(
        "question",
        ""
    ).lower()

    zone_name = data.get(
        "zone",
        "Anand Vihar"
    )

    rainfall = float(
        data.get(
            "rainfall",
            50
        )
    )

    zone = ZONES.get(
        zone_name,
        ZONES["Anand Vihar"]
    )

    risk = calculate_risk(
        zone,
        rainfall
    )

    category = classify_risk(risk)

    if "why" in question:

        answer = (
            f"{zone_name} currently has a "
            f"{category.lower()} flood risk of "
            f"{risk:.0f}%. The major contributing "
            f"factors are rainfall intensity, urban "
            f"built-up coverage, drainage capacity and "
            f"historical waterlogging patterns."
        )

    elif "what should" in question or "do" in question:

        recommendations = get_recommendations(
            risk
        )

        answer = "Recommended actions: " + " ".join(
            recommendations
        )

    elif "rain" in question:

        answer = (
            f"The current simulation uses "
            f"{rainfall:.0f} mm rainfall. "
            f"At this rainfall level, the predicted "
            f"risk for {zone_name} is "
            f"{risk:.0f}% ({category})."
        )

    else:

        answer = (
            f"FloodGuard AI predicts "
            f"{risk:.0f}% flood risk for "
            f"{zone_name}. The current category is "
            f"{category.lower()}. Ask me why the area "
            f"is risky or what actions are recommended."
        )

    return jsonify({
        "answer": answer,
        "risk": round(risk, 1),
        "category": category
    })


# ---------------------------------------------------------
# AWS S3 HEALTH CHECK
# ---------------------------------------------------------

@app.route("/api/aws-status")
def aws_status():

    bucket = os.getenv("AWS_S3_BUCKET")

    if not bucket:

        return jsonify({
            "connected": False,
            "message": "AWS S3 is not configured yet."
        })

    try:

        s3 = boto3.client("s3")

        s3.head_bucket(
            Bucket=bucket
        )

        return jsonify({
            "connected": True,
            "message": "AWS S3 connected successfully."
        })

    except (
        BotoCoreError,
        ClientError
    ) as error:

        return jsonify({
            "connected": False,
            "message": str(error)
        })


# ---------------------------------------------------------
# RENDER
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )