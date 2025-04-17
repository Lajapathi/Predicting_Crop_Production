import pandas as pd
import numpy as np
import pickle
import joblib
def model_pediction(region,year,area_harvest,yield_value,crop):

    campre_data=pd.read_csv('/Users/apple/Documents/Guvi/Projects/Predicting Crop Production/comapared_data.csv')
    matched = campre_data[campre_data['Area'].str.lower() == region.lower()]

    if not matched.empty:
        area_code = matched['Area Code (M49)'].values[0]
        
        
    if area_code is not None :
       
        # Create input array for prediction
        encoder = joblib.load('crop_encoder.pkl')
        
        

        # Combine encoded crop and input

        region_arr = np.array([[area_code,year, area_harvest, yield_value]])                 # (1, 1)
        encoded_crop = encoder.transform([[crop]]) 
        
        user_input = np.concatenate([region_arr, encoded_crop], axis=1)

        with open('dtree_model_crop.pkl', 'rb') as file:
            model = pickle.load(file)

        # Make prediction
        prediction = model.predict(user_input)
        error=''
    else:
        error='Wrong area or Wrong crop'

    return error,prediction
