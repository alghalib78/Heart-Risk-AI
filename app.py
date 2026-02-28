import os
from flask import Flask, render_template, request

app = Flask(__name__)

def calc_bmi(height_cm: float, weight_kg: float) -> float:
    h_m = height_cm / 100.0
    if h_m <= 0:
        return 0.0
    return weight_kg / (h_m * h_m)

def estimate_risk(age: int, bmi: float, sbp: float, smoker: str, diabetes: str) -> float:
    # Simple demo risk score (NOT medical advice)
    score = 0.0

    # Age
    if age >= 60:
        score += 18
    elif age >= 50:
        score += 12
    elif age >= 40:
        score += 7
    elif age >= 30:
        score += 3

    # BMI
    if bmi >= 35:
        score += 10
    elif bmi >= 30:
        score += 7
    elif bmi >= 25:
        score += 3

    # SBP
    if sbp >= 160:
        score += 12
    elif sbp >= 140:
        score += 8
    elif sbp >= 130:
        score += 4

    # Smoking / diabetes
    if smoker == "yes":
        score += 10
    if diabetes == "yes":
        score += 10

    # Convert to 0–100-ish “percent”
    risk = min(95.0, max(1.0, score))
    return round(risk, 1)

def risk_category(risk: float) -> str:
    if risk < 10:
        return "Low"
    if risk < 25:
        return "Moderate"
    if risk < 45:
        return "High"
    return "Very High"

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Use .get() so we NEVER crash with 400 BadRequestKeyError
    age_str = request.form.get("age", "").strip()
    height_str = request.form.get("height_cm", "").strip()
    weight_str = request.form.get("weight_kg", "").strip()
    sbp_str = request.form.get("sbp", "").strip()
    smoker = request.form.get("smoker", "no").strip().lower()
    diabetes = request.form.get("diabetes", "no").strip().lower()

    # Basic validation
    if not age_str or not height_str or not weight_str or not sbp_str:
        return render_template("index.html", error="Please fill in all fields.")

    try:
        age = int(age_str)
        height_cm = float(height_str)
        weight_kg = float(weight_str)
        sbp = float(sbp_str)
    except ValueError:
        return render_template("index.html", error="Numbers look invalid. Please try again.")

    bmi = round(calc_bmi(height_cm, weight_kg), 1)
    risk = estimate_risk(age, bmi, sbp, smoker, diabetes)
    category = risk_category(risk)

    return render_template(
        "result.html",
        risk=risk,
        category=category,
        bmi=bmi,
        age=age,
        height_cm=height_cm,
        weight_kg=weight_kg,
        sbp=sbp,
        smoker=smoker,
        diabetes=diabetes
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)