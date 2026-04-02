import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_absolute_error


# Load the data
df = pd.read_csv('silver_prices_data.csv')

# Drop the Date column
X = df.drop('Date', axis=1)

#High label as y
y = X['High']


# Features: all columns except high
X = X.drop('High', axis=1)


# Train test split
X_train,X_test,y_train,y_test = train_test_split(X, y, test_size=0.2, random_state=2)

#Standardizing the data
scaler=StandardScaler()
X_train=scaler.fit_transform(X_train)
X_test=scaler.transform(X_test)

#svr model
model=SVR(kernel='linear')
model.fit(X_train,y_train)

#predicting the test data
y_test_prediction= model.predict(X_test)

comparison = pd.DataFrame({
    'Actual_High': y_test.values,
    'Predicted_High': y_test_prediction,
    'Difference_Error': np.abs(y_test.values - y_test_prediction)
})

print("--- Comparison of Test Data (Unseen by Model) ---")
print(comparison.head(10)) # Shows the first 10 predictions

# Final Test Metrics
print(f"\nFinal Test R-squared: {r2_score(y_test, y_test_prediction):.4f}")
print(f"Final Test Error: ${mean_absolute_error(y_test, y_test_prediction):.2f}")

# Fixed Function: Matching the Column Order [Close, Low, Open, Volume]
def get_high_prediction(o, c, v, l):
    # The order MUST be: Close, Low, Open, Volume
    input_data = np.array([[c, l, o, v]]) 
    scaled_input = scaler.transform(input_data)
    prediction = model.predict(scaled_input)
    return prediction[0]

# Testing again with the random input
c,l,o,v = 35.00, 29.00, 30.00, 0
predicted_high = get_high_prediction(c,l,o,v)
print(f"\nCorrected Predicted High: ${predicted_high:.2f}")


df['Price_Range'] = df['High'] - df['Low']

# THE MATH
calc_range = predicted_high - l

# STATISTICAL STANDARDIZATION

r_mean, r_std = df['Price_Range'].mean(), df['Price_Range'].std()
v_mean, v_std = df['Volume'].mean(), df['Volume'].std()

# Calculate Z-Scores
z_range = (calc_range - r_mean) / r_std
z_volume = (v - v_mean) / v_std  # Changed actual_v_value to 'v'

# FINAL SPOOF SCORE
spoof_score = z_range - z_volume

# OUTPUT THE REPORT
print("\n" + "="*35)
print(f"PREDICTED HIGH: ${predicted_high:.2f}")
print(f"SPOOF SCORE:    {spoof_score:.2f}")

if spoof_score > 2.5:
    print("VERDICT: ⚠️ MANIPULATED")
else:
    print("VERDICT: ✅ NORMAL MARKET")
print("="*35)