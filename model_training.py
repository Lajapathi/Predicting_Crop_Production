import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import pickle
import re


# Load crop data
df = pd.read_csv('/Users/apple/Documents/Guvi/Projects/Predicting Crop Production/FAOSTAT_data - FAOSTAT_data_en_12-29-2024.csv')

def split_items(row):
    if pd.isna(row['Item']):
        return [None]
    # Split on commas or 'and', handling extra whitespace
    items = re.split(r',\s*|\s+and\s+', row['Item'])
    return [i.strip() for i in items if i.strip()]

# Create a new column with split item lists
df['Item List'] = df.apply(split_items, axis=1)

# Explode the DataFrame to get one item per row
df = df.explode('Item List')

# Replace original 'Item' column with split version
df['Item'] = df['Item List']
df.drop(columns=['Item List'], inplace=True)

# Reset index
df.reset_index(drop=True, inplace=True)

df=df.dropna(subset=['Value'])

df=df[(df['Flag']=='A')]
# Keep only the necessary columns
df = df[['Area Code (M49)', 'Item', 'Year', 'Element', 'Value']]

# Pivot the table: turn 'Element' values into column headers
df_wide = df.pivot_table(
    index=['Area Code (M49)', 'Item', 'Year'],
    columns='Element',
    values='Value'
).reset_index()

# Rename columns for clarity
df_wide = df_wide.rename(columns={
    'Area Code (M49)': 'Region',
    'Item': 'Crop',
    'Area harvested': 'Area Harvested (ha)',
    'Yield': 'Yield (kg/ha)',
    'Production': 'Production (tons)'
})

# Ensure the final dataframe looks like what you want
df_wide = df_wide[['Region', 'Crop', 'Year', 'Area Harvested (ha)', 'Yield (kg/ha)', 'Production (tons)']]

df_wide['Area Harvested (ha)']=df_wide['Area Harvested (ha)'].fillna(0)
df_wide['Yield (kg/ha)']=df_wide['Yield (kg/ha)'].fillna(0)
df_wide['Production (tons)']=df_wide['Production (tons)'].fillna(0)

# Encoding (One Hot Encoding)

encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoder.fit(df_wide[['Crop']])
encoded_crop = encoder.transform(df_wide[['Crop']])
encoded_crop_df = pd.DataFrame(
    encoded_crop,
    columns=encoder.get_feature_names_out(['Crop'])
)
df_wide_encoded = pd.concat([df_wide.drop('Crop', axis=1), encoded_crop_df], axis=1)

# Save encoding

import joblib
joblib.dump(encoder, 'crop_encoder.pkl')

# Model training

x=df_wide_encoded.drop(['Production (tons)'],axis=1)
y=df_wide_encoded['Yield (kg/ha)']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

#dtree_model_crop=DecisionTreeRegressor( splitter='best', max_depth=35, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=None, random_state=42, max_leaf_nodes=None)
dtree_model_crop=DecisionTreeRegressor(random_state=42)

dtree_model_crop.fit(x_train,y_train)

y_pred=dtree_model_crop.predict(x_test)

r2_score_value=r2_score(y_test,y_pred)

print(r2_score_value)

# Save model 
with open('dtree_model_crop.pkl', 'wb') as file:
    pickle.dump(dtree_model_crop, file)