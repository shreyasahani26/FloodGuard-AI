# 🌊 FloodGuard AI

> AI-powered hyperlocal urban flood risk prediction and emergency action system.

## 🚀 Live Demo

👉 **[Launch FloodGuard AI](https://floodguard-ai-4y41.onrender.com)**

## 💻 GitHub Repository

👉 **[View Source Code](https://github.com/shreyasahani26/FloodGuard-AI)**

---

## 🌧️ Problem

Urban flooding can turn heavy rainfall into dangerous waterlogging within a short period of time. Existing weather systems usually tell people **how much rain is expected**, but they don't clearly answer:

- Which local areas are most vulnerable?
- When could flooding become critical?
- Why is a particular area at higher risk?
- What action should people take?

FloodGuard AI is designed to address this gap by combining rainfall and environmental factors to estimate hyperlocal flood risk.

---

## 💡 Solution

**FloodGuard AI** is an AI-powered environmental risk monitoring platform that predicts flood risk for different urban zones and converts the prediction into actionable information.

The system analyzes multiple environmental factors such as:

- 🌧️ Rainfall intensity
- 💧 Cumulative rainfall
- 🏔️ Elevation
- 📐 Terrain slope
- 🏙️ Built-up area
- 🚰 Drainage conditions
- 🛣️ Road density
- 📊 Historical flood patterns
- 🌱 Soil absorption capacity

The result is converted into a **0–100 Flood Risk Score** and classified as:

🟢 Low → 🟡 Moderate → 🟠 High → 🔴 Critical

---

## 🧠 AI / ML Engine

The current prototype uses a **Random Forest Regressor** to estimate flood-risk scores from environmental features.

### Model Pipeline

```text
Environmental Inputs
        ↓
Feature Processing
        ↓
Random Forest Model
        ↓
Flood Risk Score (0–100)
        ↓
Risk Classification
        ↓
Recommended Action
