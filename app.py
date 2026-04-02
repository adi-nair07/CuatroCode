import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

print("Loading data and training LSTM model. This may take a minute...")
try:
    df = pd.read_csv('super_gold_prices_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').dropna().reset_index(drop=True)
    
    # Use the columns already present in super_gold_prices_data.csv
    features = ['Close', 'Open', 'High', 'Low', 'Volume', 'RSI', 'MACD', 'Upper_Band', 'Lower_Band', 'Lag_1']
    
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[features + ['Target']])
    
    X, y = [], []
    window = 30
    for i in range(window, len(scaled_data)):
        X.append(scaled_data[i-window:i, :-1])
        y.append(scaled_data[i, -1])
        
    X, y = np.array(X), np.array(y)
    split = int(len(X) * 0.8)
    X_train, y_train = X[:split], y[:split]
    
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    
    # Training with 5 epochs for quicker startup testing
    model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=0)
    print("LSTM Model trained successfully.")
    
except Exception as e:
    print(f"Error during model training: {e}")
    model, scaler, df, features, scaled_data = None, None, None, None, None

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/predict', methods=['GET'])
def predict():
    if model is None or scaler is None:
        return jsonify({'error': 'Model not trained or data missing.'}), 500
        
    try:
        # Get the last 30 days from the dataset
        last_30 = scaled_data[-30:, :-1]
        last_30_reshaped = np.expand_dims(last_30, axis=0) # shape: (1, 30, 10)
        
        # Predict scaled target
        scaled_pred = model.predict(last_30_reshaped)
        
        # Inverse transform
        dummy = np.zeros((1, len(features) + 1))
        dummy[0, -1] = scaled_pred[0][0]
        actual_prediction = scaler.inverse_transform(dummy)[0][-1]
        
        today_close = df.iloc[-1]['Close']
        trend = "UP" if actual_prediction > today_close else "DOWN"
        
        return jsonify({
            'current_price': round(today_close, 2),
            'predicted_tomorrow': round(actual_prediction, 2),
            'trend': trend
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
