from flask import Flask, render_template, request, session, redirect, flash
import requests
import pickle

model = pickle.load(open("model.pkl", "rb"))

app = Flask(__name__)
app.secret_key = "nutrihealth"

# ---------------------------
# API Setup
# ---------------------------
API_KEY = "CLquy8xmBjTN+BQn0a+xHg==Xh5u7NhVt5J4uHY2"
API_URL = "https://api.calorieninjas.com/v1/nutrition"
HEADERS = {"X-Api-Key": API_KEY}

# ---------------------------
# Home Page
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------------------
# Reset daily totals
# ---------------------------
@app.route("/reset")
def reset():
    session.pop('daily_totals', None)
    flash(" Daily totals reset!")
    return redirect("/")

# ---------------------------
# Result Page
# ---------------------------
@app.route("/result", methods=["POST"])
def result():
    # Get form data
    meal_text = request.form.get("meal")
    meal_time = request.form.get("meal_time")
    bp = request.form.get("bp")
    sugar = request.form.get("sugar")
    thyroid = request.form.get("thyroid")
    weight = request.form.get("weight")
    age = request.form.get("age")
    gender = request.form.get("gender")
    activity = request.form.get("activity")

    # ---------------------------
    # Input Validation
    if not meal_text:
        flash(" Please enter your meal.")
        return redirect("/")
    if not meal_time:
        flash(" Please select a meal type.")
        return redirect("/")
    meal_time = meal_time.strip().title()

    try:
        weight = float(weight)
        age = int(age)
        if weight <= 0 or age <= 0:
            flash(" Weight and Age must be greater than 0.")
            return redirect("/")
    except:
        flash(" Invalid Age or Weight.")
        return redirect("/")

    # ---------------------------
    # Initialize session storage safely
    if 'daily_totals' not in session:
        session['daily_totals'] = {
            "Breakfast": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
            "Lunch": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
            "Dinner": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
            "Snack": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        }

    # Ensure current meal exists and is a dict
    if meal_time not in session['daily_totals'] or not isinstance(session['daily_totals'][meal_time], dict):
        session['daily_totals'][meal_time] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

    # ---------------------------
    # Call API for each food separately
    unknown_food = []
    total_calories = total_protein = total_carbs = total_fat = 0
    items = []

    food_list = [x.strip() for x in meal_text.split(',')]

    for food in food_list:
        response = requests.get(API_URL, headers=HEADERS, params={"query": food})
        if response.status_code == 200:
            data = response.json()
            if not data.get("items"):
                unknown_food.append(food)

            else:
                for item in data['items']:
                    items.append(item)
                    total_calories += item.get("calories", 0)
                    total_protein += item.get("protein_g", 0)
                    total_carbs += item.get("carbohydrates_total_g", 0)
                    total_fat += item.get("fat_total_g", 0)
        else:
             unknown_food.append(food)
    
     # ---------------- WRONG INPUT FIX ----------------
    # ❗ STRICT VALIDATION (even 1 wrong item → reject everything)
    if unknown_food:
        flash(f"⚠️ Invalid food item(s): {', '.join(unknown_food)}. Please enter correct meal.")
        return redirect("/")



    # ---------------------------
    # Round totals to 1 decimal place
    total_calories = round(total_calories, 1)
    total_protein = round(total_protein, 1)
    total_carbs = round(total_carbs, 1)
    total_fat = round(total_fat, 1)

    # ---------------------------
    # Update session totals for this meal
    session['daily_totals'][meal_time]['calories'] += total_calories
    session['daily_totals'][meal_time]['protein'] += total_protein
    session['daily_totals'][meal_time]['carbs'] += total_carbs
    session['daily_totals'][meal_time]['fat'] += total_fat
    session.modified = True  # make sure session updates

    # ---------------------------
    # Round session totals safely
    for meal, vals in session['daily_totals'].items():
        if isinstance(vals, dict):
            for key in vals:
                vals[key] = round(vals[key], 1)

    # ---------------------------
    # Calculate overall totals safely
    overall_totals = {
        "calories": round(sum(m['calories'] for m in session['daily_totals'].values() if isinstance(m, dict)), 1),
        "protein": round(sum(m['protein'] for m in session['daily_totals'].values() if isinstance(m, dict)), 1),
        "carbs": round(sum(m['carbs'] for m in session['daily_totals'].values() if isinstance(m, dict)), 1),
        "fat": round(sum(m['fat'] for m in session['daily_totals'].values() if isinstance(m, dict)), 1)
    }

    # ---------------------------
    # Risk Levels (Low / Medium / High)
    # ---------------------------
    diabetes_risk = "Low"
    bp_risk = "Low"

    try:
        
        if bp and "/" in bp:
            sys, dia = map(int, bp.split("/"))
            if sys >= 160 or dia >= 100:
                bp_risk = "High"
            elif sys >= 140 or dia >= 90:
                bp_risk = "Medium"

        if sugar and sugar.isdigit():
            sugar_val = int(sugar)
            # Features: sugar, carbs, bmi, bp
            prediction = model.predict([[sugar_val, overall_totals["carbs"], bmi, sys]])
            diabetes_risk = prediction[0]
            
    except:
        pass


    # ---------------------------
    # Recommended daily intake (simple rules)
    if gender == "Female":
        base_cal = 1800
    else:
        base_cal = 2200

    if activity == "Active":
        base_cal += 300
    elif activity == "Sedentary":
        base_cal -= 200

    recommended_calories = base_cal
    recommended_protein = round(weight * 0.8, 1)  # g/day

    # ---------------------------
    # Nutrient Deficiency / Excess Alerts
    # ---------------------------
    nutrition_alerts = []

    if overall_totals["calories"] < 0.75 * recommended_calories:
        nutrition_alerts.append(" Low calorie intake today.")

    if overall_totals["protein"] < recommended_protein:
        nutrition_alerts.append(" Protein deficiency detected.")

    if overall_totals["carbs"] > 300:
        nutrition_alerts.append(" Excess carbohydrate intake today.")

    if overall_totals["fat"] > (0.35 * overall_totals["calories"] / 9):
        nutrition_alerts.append(" Fat intake is too high.")


    # ---------------------------
    # Risk Assessment Messages
    # ---------------------------
    risk_alerts = []

    if diabetes_risk == "High":
        risk_alerts.append(" High diabetes risk. Current meals may spike blood sugar.")
    elif diabetes_risk == "Medium":
        risk_alerts.append(" Moderate diabetes risk. Control carbs and sugar.")

    if bp_risk == "High":
        risk_alerts.append(" High BP risk. Avoid salty and fried foods.")
    elif bp_risk == "Medium":
        risk_alerts.append(" Moderate BP risk. Limit salt intake.")

    if thyroid == "Low":
        risk_alerts.append(" Low thyroid: low calories may cause fatigue.")
    elif thyroid == "High":
        risk_alerts.append(" High thyroid: avoid excess caffeine and sugar.")

    # ---------------------------
    # Preventive Healthcare Messages (Long-term focus)
    # ---------------------------
    preventive_messages = []

#  Heart Health
    if bp_risk in ["High", "Medium"] or overall_totals["fat"] > (0.35 * overall_totals["calories"] / 9):
        preventive_messages.append(" Heart health: reduce oily foods and include walking or light exercise daily.")

# Diabetes Prevention
    if diabetes_risk in ["High", "Medium"] or overall_totals["carbs"] > 250:
        preventive_messages.append(" Diabetes prevention: prefer whole grains, vegetables, and avoid sugary drinks.")

#  Digestion Health
    if overall_totals["protein"] < recommended_protein or total_calories > 800:
        preventive_messages.append(" Digestion: eat smaller meals, chew well, and include fiber-rich foods.")

#  Sleep Health
    if meal_time == "Dinner" and total_calories > 700:
        preventive_messages.append(" Sleep: avoid heavy dinners and reduce screen time before bed.")

    if not preventive_messages:
        preventive_messages.append(" Good long-term health habits today. Keep following balanced meals and activity.")

    # ---------------------------
    # Suggestions
    suggestions = []

        # ---------------------------
    # STEP 4 — SMART PERSONALIZED SUGGESTIONS (Portion + Replacement)

    # ---- Sugar Risk + Carb Portion Control ----
    if sugar:
        try:
            sugar_val = int(sugar)
            if sugar_val > 140 and total_carbs > 60:
                suggestions.append(" High sugar + high carbs: reduce rice/roti portion and add vegetables or millets.")
            elif sugar_val < 70:
                suggestions.append(" Low sugar: include small frequent meals with complex carbs like oats or fruits.")
        except:
            pass

    # ---- BP Risk + Salt/Fried Food Replacement ----
    if bp and "/" in bp:
        try:
            sys = int(bp.split("/")[0])
            dia = int(bp.split("/")[1])
            if sys > 140 or dia > 90:
                suggestions.append(" High BP: avoid salty/fried foods, choose steamed or home-cooked meals.")
            elif sys < 90 or dia < 60:
                suggestions.append(" Low BP: drink more fluids and avoid skipping meals.")
        except:
            pass

    # ---- Protein Deficiency Fix ----
    if overall_totals["protein"] < recommended_protein:
        suggestions.append(" Protein is low, which can affect muscle and immunity. Add eggs, paneer, dal or tofu.")

    # ---- Fat Control Replacement ----
    if overall_totals["fat"] > (0.35 * overall_totals["calories"] / 9):
        suggestions.append(" High fat intake: replace fried items with grilled or boiled foods.")

    # ---- Thyroid Based Advice ----
    if thyroid == "Low":
        suggestions.append(" Low thyroid: eat fruits, vegetables, and avoid packaged foods.")
    elif thyroid == "High":
        suggestions.append(" High thyroid: avoid excess caffeine and sugary foods; focus on protein.")
    
    # ---------------------------
    # Fiber & Vitamin (Vegetable/Fruit) Suggestion Logic
    veggie_words = ["vegetable", "spinach", "carrot", "beans", "cabbage", "broccoli", "salad", "fruit", "apple", "banana"]

    if total_carbs > 80 and not any(v in meal_text.lower() for v in veggie_words):
        suggestions.append(" High carbs without vegetables detected. Add veggies/fruits for fiber and vitamins.")

    # ---------------------------
    # Portion Size Detection Logic
    large_portion_foods = ["rice", "biryani", "noodles", "fried rice", "pasta", "parotta", "chapati"]

    if any(f in meal_text.lower() for f in large_portion_foods) and total_calories > 600:
        suggestions.append(" Portion seems large. Try reducing rice/noodles/roti quantity and add more vegetables.")

    # ---- BMI Based Portion Advice ----
    height = 1.7
    bmi = weight / (height ** 2)

    if bmi >= 25:
        suggestions.append(" Overweight: reduce portion size and increase vegetables in meals.")
    elif bmi < 18.5:
        suggestions.append(" Underweight: increase calories using healthy fats and protein.")
 
    
    # ---- Activity Based Adjustment ----
    if activity == "Sedentary":
        suggestions.append(" Sedentary: add 20–30 mins walking daily.")
    elif activity == "Moderate":
        suggestions.append(" Moderate activity: maintain protein intake for muscle recovery.")

    # ---- If everything looks okay ----
    if not suggestions:
        suggestions.append(" Your meal and health inputs look balanced. Keep following healthy habits.")

    # ---------------------------
    # STEP — MEAL TIMING OPTIMIZATION (SMART)

    meal_tips = []
    if meal_time == "Breakfast":
        if total_protein < 15:
            meal_tips.append(" Breakfast low in protein. Add eggs, milk, paneer or nuts for better energy.")
        if total_calories < 300:
            meal_tips.append(" Breakfast calories are low. Add whole grains or fruits.")

    #  Lunch Optimization
    if meal_time == "Lunch":
        if total_calories > 800:
            meal_tips.append(" Very heavy lunch may cause sleepiness. Reduce rice and add vegetables.")
        if total_protein < 20:
            meal_tips.append(" Add protein like dal, curd, or paneer to make lunch balanced.")

    #  Dinner Optimization
    if meal_time == "Dinner":
        if total_calories > 700:
            meal_tips.append(" Heavy dinner can disturb sleep. Prefer light, easily digestible foods like soup, chapati, or steamed vegetables.")

        if total_carbs > 80:
            meal_tips.append(" Reduce carbs at night and increase vegetables.")

    #  Snack Optimization
    if meal_time == "Snack":
        if total_calories > 300:
            meal_tips.append(" High calorie snack. Choose fruits, nuts or yogurt instead of fried snacks.")
        if sugar and sugar.isdigit() and int(sugar) > 140:
            meal_tips.append(" With high sugar, avoid sweet snacks. Choose fiber-rich foods.")


    if not meal_tips:
        meal_tips.append(" Meal timing and portion look appropriate for this meal.")

    
    

    # ---------------------------
    # Remaining Calories / Protein
    remaining_calories = recommended_calories - overall_totals["calories"]
    remaining_protein = recommended_protein - overall_totals["protein"]

    if remaining_calories < 0:
        remaining_calories_msg = f" You have crossed your calorie limit by {-remaining_calories} kcal!"
    else:
        remaining_calories_msg = f"{remaining_calories} kcal remaining"

    if remaining_protein < 0:
        remaining_protein_msg = f" You have exceeded your protein target by {-remaining_protein} g!"
    else:
        remaining_protein_msg = f"{remaining_protein} g remaining"

        # ---------------------------
    # STEP 5 — AI STYLE RISK LEVELS

    diabetes_risk = "Low"
    bp_risk = "Low"

    # Diabetes risk based on sugar + carbs
    try:
        if sugar and int(sugar) > 140 and total_carbs > 60:
            diabetes_risk = "High"
        elif sugar and int(sugar) > 110:
            diabetes_risk = "Medium"
    except:
        pass

    # BP risk based on BP values
    if bp and "/" in bp:
        try:
            sys = int(bp.split("/")[0])
            dia = int(bp.split("/")[1])
            if sys > 140 or dia > 90:
                bp_risk = "High"
            elif sys > 120 or dia > 80:
                bp_risk = "Medium"
        except:
            pass
    #thyroid risk level
    thyroid_risk = "Normal"

    if thyroid == "Low":
        thyroid_risk = "Low"
    elif thyroid == "High":
        thyroid_risk = "High"

    # ---------------------------
    # STEP 1 — Preventive Nutrition Score (0–100)
    diet_score = 100

    # Calories check
    if overall_totals["calories"] < 0.8 * recommended_calories or overall_totals["calories"] > 1.2 * recommended_calories:
        diet_score -= 20

# Protein check
    if overall_totals["protein"] < recommended_protein:
        diet_score -= 20

# Diabetes risk
    if diabetes_risk == "High":
        diet_score -= 25
    elif diabetes_risk == "Medium":
        diet_score -= 10

# BP risk
    if bp_risk == "High":
        diet_score -= 25
    elif bp_risk == "Medium":
        diet_score -= 10

# Meal timing issues
    if any("Heavy" in tip or "low" in tip.lower() for tip in meal_tips):
        diet_score -= 10

# Keep score in range
    if diet_score < 0:
       diet_score = 0



    # ---------------------------
    # Render result
    return render_template(
        "result.html",
        meal_text=meal_text,
        items=items,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        meal_time=meal_time,
        bp=bp,
        sugar=sugar,
        thyroid=thyroid,
        weight=weight,
        age=age,
        gender=gender,
        activity=activity,
        recommended_calories=recommended_calories,
        recommended_protein=recommended_protein,
        nutrition_alerts=nutrition_alerts,
        risk_alerts=risk_alerts,
        suggestions=suggestions,
        meal_tips=meal_tips,
        remaining_calories_msg=remaining_calories_msg,
        remaining_protein_msg=remaining_protein_msg,
        unknown_foods=unknown_food,
        diabetes_risk=diabetes_risk,
        bp_risk=bp_risk,
        thyroid_risk=thyroid_risk,
        diet_score=diet_score,
        daily_totals=session['daily_totals'],   # needed for calories per meal chart
        overall_totals=overall_totals,         # needed for macro split chart
        preventive_messages=preventive_messages


    )

# ---------------------------
# Run Server
if __name__ == "__main__":
    app.run(debug=True)
