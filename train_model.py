import os
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


# =========================================================
# FLOODGUARD AI
# Prototype Environmental Risk Model
# =========================================================

np.random.seed(42)

N = 8000


# =========================================================
# 1. GENERATE ENVIRONMENTAL FEATURES
# =========================================================

rainfall_1h = np.random.uniform(0, 120, N)

rainfall_3h = (
    rainfall_1h * np.random.uniform(1.4, 2.4, N)
)

rainfall_6h = (
    rainfall_3h * np.random.uniform(1.3, 2.0, N)
)

elevation = np.random.uniform(10, 250, N)

slope = np.random.uniform(0.2, 10, N)

builtup = np.random.uniform(20, 100, N)

drainage = np.random.uniform(20, 100, N)

road_density = np.random.uniform(10, 100, N)

historical_floods = np.random.uniform(0, 15, N)

soil_absorption = np.random.uniform(15, 90, N)


# =========================================================
# 2. NORMALIZE ENVIRONMENTAL SIGNALS
# =========================================================

rain_score = np.clip(
    rainfall_1h / 120,
    0,
    1
)

cumulative_score = np.clip(
    rainfall_6h / 350,
    0,
    1
)

low_elevation_score = np.clip(
    1 - elevation / 250,
    0,
    1
)

builtup_score = builtup / 100

drainage_stress = 1 - drainage / 100

road_score = road_density / 100

history_score = np.clip(
    historical_floods / 15,
    0,
    1
)

low_absorption_score = 1 - soil_absorption / 100

slope_score = 1 - np.clip(
    slope / 10,
    0,
    1
)


# =========================================================
# 3. ENVIRONMENTAL RISK SCORE
# =========================================================

raw_risk = (

    rain_score * 0.30

    + cumulative_score * 0.16

    + low_elevation_score * 0.12

    + builtup_score * 0.10

    + drainage_stress * 0.13

    + road_score * 0.04

    + history_score * 0.07

    + low_absorption_score * 0.05

    + slope_score * 0.03

)


# Convert to 0-100

risk = raw_risk * 100


# Add small environmental noise

risk += np.random.normal(
    0,
    2.5,
    N
)


risk = np.clip(
    risk,
    0,
    100
)


# =========================================================
# 4. CREATE DATAFRAME
# =========================================================

data = pd.DataFrame({

    "rainfall_1h":
        rainfall_1h,

    "rainfall_3h":
        rainfall_3h,

    "rainfall_6h":
        rainfall_6h,

    "elevation":
        elevation,

    "slope":
        slope,

    "builtup":
        builtup,

    "drainage":
        drainage,

    "road_density":
        road_density,

    "historical_floods":
        historical_floods,

    "soil_absorption":
        soil_absorption,

    "flood_risk":
        risk

})


# =========================================================
# 5. FEATURES
# =========================================================

FEATURES = [

    "rainfall_1h",

    "rainfall_3h",

    "rainfall_6h",

    "elevation",

    "slope",

    "builtup",

    "drainage",

    "road_density",

    "historical_floods",

    "soil_absorption"

]


X = data[FEATURES]

y = data["flood_risk"]


# =========================================================
# 6. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42

)


# =========================================================
# 7. RANDOM FOREST
# =========================================================

model = RandomForestRegressor(

    n_estimators=300,

    max_depth=16,

    min_samples_split=6,

    min_samples_leaf=2,

    random_state=42,

    n_jobs=-1

)


print()
print("=" * 55)
print("        FLOODGUARD AI MODEL TRAINING")
print("=" * 55)
print()

print("Training environmental risk model...")

model.fit(
    X_train,
    y_train
)


# =========================================================
# 8. MODEL EVALUATION
# =========================================================

predictions = model.predict(
    X_test
)

mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print()
print("-" * 55)
print("MODEL PERFORMANCE")
print("-" * 55)

print(
    f"MAE      : {mae:.2f}"
)

print(
    f"R2 Score : {r2:.4f}"
)

print("-" * 55)


# =========================================================
# 9. SAVE MODEL
# =========================================================

os.makedirs(
    "model",
    exist_ok=True
)


joblib.dump(

    {
        "model": model,
        "features": FEATURES
    },

    "model/flood_model.joblib"

)


print()
print("Model saved successfully:")
print(
    "model/flood_model.joblib"
)

print()
print("=" * 55)
print("TRAINING COMPLETE")
print("=" * 55)