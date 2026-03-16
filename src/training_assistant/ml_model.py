import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score


def train_boundary_model(df):

    data = df.copy()

    # Create target variable
    data["is_boundary"] = data["runs_off_bat"].apply(
        lambda x: 1 if x in [4, 6] else 0
    )

    # Select features
    features = data[[
        "striker",
        "bowler",
        "batting_team",
        "bowling_team",
        "venue"
    ]]

    target = data["is_boundary"]

    # Encode categorical features
    encoders = {}

    for col in features.columns:
        le = LabelEncoder()
        features[col] = le.fit_transform(features[col].astype(str))
        encoders[col] = le

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestClassifier()

    model.fit(X_train, y_train)

    # Test accuracy
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("Model Accuracy:", accuracy)

    return model, encoders