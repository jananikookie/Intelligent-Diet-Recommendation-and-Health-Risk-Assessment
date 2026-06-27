# NutriHealth – Intelligent-Diet-Recommendation-and-Health-Risk-Assessment

## Problem Statement

Maintaining a healthy lifestyle requires monitoring daily nutrition and understanding potential health risks. However, many people find it difficult to estimate calorie intake, analyze nutritional values, and identify health concerns such as diabetes, high blood pressure, or thyroid-related conditions based on their eating habits.

NutriHealth addresses this challenge by combining nutrition analysis with Machine Learning to provide personalized diet recommendations and health risk assessment. The application helps users make informed dietary decisions by analyzing meal data, tracking nutrient intake, and predicting potential health risks through an interactive web interface.

## Overview:

NutriHealth is a web-based health and nutrition tracking application built using Flask and Machine Learning. It allows users to enter their daily meals and health details such as blood sugar, blood pressure, thyroid status, age, weight, and activity level. The system analyzes the food using a nutrition API and predicts health risks like diabetes and blood pressure using a trained machine learning model. It also provides calorie tracking, dietary suggestions, and a smart dashboard to help users maintain a healthy lifestyle.

## Features:
- Meal-based calorie and nutrition analysis using external API
- Tracks daily intake of calories, protein, carbohydrates, and fat
- Predicts health risks (Diabetes, Blood Pressure, Thyroid) using Machine Learning
- Personalized diet suggestions based on user inputs
- Daily meal-wise tracking (Breakfast, Lunch, Dinner, Snack)
- Interactive dashboard with visual charts
- Shows remaining calorie and protein balance for the day
- Preventive health tips for long-term wellness

## Screenshots

### Landing Page

The home page where users begin their nutrition and health assessment.

![Landing Page](screenshots/landing-page.png)

---

### Health Details Form

Users enter personal health information, activity level, and meal details.

![Health Details Form](screenshots/health-form.png)

---

### Dashboard

Interactive dashboard summarizing daily nutrition and health information.

![Dashboard](screenshots/dashboard.png)

---

### Nutrition Analysis

Provides a meal-wise breakdown of nutritional values to help users monitor their daily dietary intake.

![Meal-wise Nutrition Analysis](screenshots/nutrition-analysis.png)

### Personalized Diet Suggestions

Provides customized dietary recommendations based on user inputs and health conditions.

![Diet Suggestions](screenshots/diet-suggestion.png)

---

### Health Risk Assessment

Machine Learning model predicts potential health risks based on user data.

![Health Risk Analysis](screenshots/health-risk-analysis.png)

---

### Nutrition Charts

Visual representation of calorie and nutrient distribution for better health tracking.

![Nutrition Charts](screenshots/charts.png)

## Tech Stack:

- Programming Language: Python
- Frontend: HTML, CSS, JavaScript
- Backend: Flask (Python)
- Machine Learning: Scikit-learn (Random Forest Classifier)
- Database/Storage: Session (Flask session storage)
- API: CalorieNinjas Nutrition API
- Libraries: Pandas, Requests, Pickle
  
## How to Run

1. Clone this repository:

   ```bash
   git clone <https://github.com/jananikookie/Intelligent-Diet-Recommendation-and-Health-Risk-Assessment>
   ```

2. Navigate to the project directory:

   ```bash
   cd Intelligent-Diet-Recommendation-and-Health-Risk-Assessment
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Train the Machine Learning model:

   ```bash
   python train_model.py
   ```

5. Run the Flask application:

   ```bash
   python app.py
   ```

6. Open your browser and visit:

   ```
   http://127.0.0.1:5000/
   ```

**Note:**

* Ensure `model.pkl` is generated before running the application.
* Keep the HTML files inside the `templates` folder.
* An active internet connection is required for the CalorieNinjas Nutrition API.


## Project Structure

- templates/
- screenshots/
  * index.html
  * result.html 
- app.py
- train_model.py
- model.pkl
- README.md
- health_dataset.csv
- requirements.txt              
 
## ML Model:

- Project uses a Random Forest Classifier for health risk prediction
- It is trained using a custom dataset (health_dataset.csv)
- Input features include: sugar level, carbohydrate intake, BMI, and blood pressure
- Output predicts health risk level: Low, Medium, or High
- The trained model is saved as model.pkl using pickle
- The model is integrated into a Flask web application for real-time prediction
  
## Future Improvements:

- User login and authentication for personalized health tracking
- Deploy the application online using cloud platforms like Render or AWS
- Add graphical reports for weekly and monthly health analysis
- Store user history in a database for long-term tracking
- Make the UI fully mobile responsive for better user experience
  
## Author

**Janani Kumar**
Computer Science Graduate
