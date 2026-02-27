from flask import Flask, render_template, request
import math

app = Flask(__name__)

def clamp(x, lo=1, hi=99):
    return max(lo, min(hi, x))
def risk_category(risk_percent: float) -> str:
    if risk_percent < 35:
        return "Low"
    elif risk_percent < 65:
        return "Medium"
    else:
        return "High"
def calc_bmi(height_cm: float, weight_kg: float) -> float:
    h_m = height_cm / 100.0
    return weight_kg / (h_m * h_m + 1e-9)

def risk_percent(age: int, sex: str, height_cm: float, weight_kg: float,
                 smoker: str, fam_diabetes: str, fam_cancer: str,
                 chest_pain: str, sbp_str: str) -> float:
    """
    Educational demo scoring (NOT medical diagnosis).
    Uses a logistic-style score -> percent.
    """

    bmi = calc_bmi(height_cm, weight_kg)

    # Base score (negative = low baseline risk)
    score = -6.0

    # Age
    score += 0.05 * (age - 30)   # risk rises after ~30

    # Sex (rough demo placeholder; not a clinical rule)
    if sex == "male":
        score += 0.35

    # BMI influence
    score += 0.08 * (bmi - 25)

    # Smoking
    if smoker == "yes":
        score += 0.85

    # Family history (simple yes/no for demo)
    if fam_diabetes == "yes":
        score += 0.55
    if fam_cancer == "yes":
        score += 0.25

    # Chest pain
    if chest_pain == "yes":
        score += 0.90

    # Optional blood pressure (SBP)
    sbp_str = (sbp_str or "").strip()
    if sbp_str != "":
        try:
            sbp = float(sbp_str)
            score += 0.03 * (sbp - 120)  # higher SBP increases score
        except ValueError:
            pass  # ignore if user typed non-number

    # Convert to probability
    prob = 1 / (1 + math.exp(-score))
    return round(clamp(prob * 100), 0)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
@app.route("/predict", methods=["POST"])
def predict():
    # Required fields
    age = int(request.form["age"])
    sex = request.form["sex"]
    height_cm = float(request.form["height_cm"])
    weight_kg = float(request.form["weight_kg"])

    # Optional/Yes-No fields
    sbp = request.form.get("sbp", "")
    smoker = request.form.get("smoker", "no")
    fam_diabetes = request.form.get("fam_diabetes", "no")
    fam_cancer = request.form.get("fam_cancer", "no")
    chest_pain = request.form.get("chest_pain", "no")

    risk = risk_percent(
        age=age,
        sex=sex,
        height_cm=height_cm,
        weight_kg=weight_kg,
        smoker=smoker,
        fam_diabetes=fam_diabetes,
        fam_cancer=fam_cancer,
        chest_pain=chest_pain,
        sbp_str=sbp
    )

    category = risk_category(risk)
    bmi = round(calc_bmi(height_cm, weight_kg), 1)

    return render_template("result.html", risk=risk, bmi=bmi, category=category)


if __name__ == "__main__":
    app.run(debug=True)