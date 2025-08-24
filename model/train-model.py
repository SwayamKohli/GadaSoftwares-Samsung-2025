import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder

with open('rcbmodel.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

with open('rcbscaler.pkl', 'rb') as f:
    loaded_scaler = pickle.load(f)

print("Model and scaler loaded successfully.")
le = LabelEncoder()
le.fit(['real-time', 'non-real-time'])
new_data_point = pd.DataFrame({
    'Source.Port': [12345], 
    'Destination.Port': [80], 
    'Flow.Duration': [1000],
    'Total.Fwd.Packets': [10], 
    'Total.Backward.Packets': [8],
    'Flow.Packets.s': [1800], 
    'Fwd.Packet.Length.Max': [500],
    'Flow.IAT.Max': [1000],
    'Bwd.Packet.Length.Max': [450], 
    'Init_Win_bytes_forward': [29200], 
    'Init_Win_bytes_backward': [25700],
    'Timestamp_Formatted': [1672531200]
})
scaled_new_data = loaded_scaler.transform(new_data_point)
print("New data has been scaled.")
predicted_encoded_value = loaded_model.predict(scaled_new_data)
predicted_label = le.inverse_transform(predicted_encoded_value)

print(f"The predicted category is: {predicted_label[0]}")