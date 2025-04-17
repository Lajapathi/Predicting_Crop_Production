import pandas as pd
import re



df=pd.read_csv('/Users/apple/Documents/Guvi/Projects/Predicting Crop Production/FAOSTAT_data - FAOSTAT_data_en_12-29-2024.csv')

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

df.dropna(subset=['Value'], inplace=True)
campre_data = df[(df['Flag']=='A')&(df['Element']=='Production')]
campre_data.drop(columns=['Domain Code','Domain','Element Code','Element','Year Code','Unit','Flag','Flag Description','Note','Year','Value'],inplace=True)
campre_data['Item Code (CPC)'] = campre_data['Item Code (CPC)'].astype(str).str.extract('(\d+)')

campre_data.to_csv('comapared_data.csv',index=False)


# prediction option csv
df=pd.read_csv('/Users/apple/Documents/Guvi/Projects/Predicting Crop Production/FAOSTAT_data - FAOSTAT_data_en_12-29-2024.csv')


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
df_wide_option = df_wide[['Region', 'Crop', 'Year', 'Area Harvested (ha)', 'Yield (kg/ha)', 'Production (tons)']]
df_wide_option.to_csv('df_wide_option.csv', index=False)