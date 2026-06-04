import pandas as pd
from sklearn.model_selection import train_test_split
import pickle

# Load dataset
data = pd.read_csv("health_dataset.csv")

# Input features
X = data[['sugar', 'carbs', 'bmi', 'bp']]

# Output
y = data['risk']

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Random Forest
model = RandomForestClassifier(n_estimators=200,max_depth=4, min_samples_leaf=2, random_state=42)
model.fit(X_train, y_train)


print("Train Accuracy:", model.score(X_train, y_train))
print("Test Accuracy:", model.score(X_test, y_test))

pickle.dump(model, open("model.pkl", "wb"))
print("Model saved as model.pkl")
