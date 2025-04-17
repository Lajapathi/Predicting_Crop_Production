import pandas as pd
import streamlit as st
import plotly.express as px
from dataframe import crop_production_data
from model_prediction import model_pediction

## streamlit run crop_production_ui.py

@st.cache_data
def crop_production_new():
    data_df=crop_production_data()
    return data_df
crop_df=crop_production_new()

st.title("🚜 Crop Production Analysis")

# sedebar filters
#st.sidebar.header("Filters")
year=st.sidebar.multiselect('Select year',crop_df['year'].unique(),default=crop_df['year'].unique())


# for no filter selection

if not year:
    year=crop_df['year'].unique()


# filter dataframe
crop_df_filtered=crop_df[crop_df['year'].isin(year)]

#st.dataframe(crop_df_filtered)
df=crop_df_filtered
# --- 1. Crop Distribution Analysis ---
def analyze_crop_distribution(df):
    st.subheader("🌾 Crop Distribution Analysis")
    crop_counts = df['item'].value_counts().reset_index()
    crop_counts.columns = ['item', 'count']
    fig = px.bar(crop_counts.head(20), x='item', y='count', title="Top 20 Most Cultivated Crops")
    st.plotly_chart(fig, use_container_width=True)

# --- 2. Geographical Distribution ---
def analyze_geographical_distribution(df):
    st.subheader("🗺️ Geographical Crop Distribution")
    area_crop = df.groupby(['area', 'item'])['value'].sum().reset_index()
    fig = px.treemap(area_crop, path=['area', 'item'], values='value', title="Crop Production by Area")
    st.plotly_chart(fig, use_container_width=True)

# --- 3. Yearly Trends ---
def analyze_yearly_trends(df):
    st.subheader("📈 Yearly Trends in Area, Yield & Production")
    element_filter = st.selectbox("Select Element", df['element'].unique())
    yearly = df[df['element'] == element_filter].groupby('year')['value'].sum().reset_index()
    fig = px.line(yearly, x='year', y='value', title=f"Yearly Trend of {element_filter}")
    st.plotly_chart(fig, use_container_width=True)

# --- 4. Growth Analysis ---
def analyze_growth_analysis(df):
    st.subheader("🌱 Growth Trends by Crop or Region")
    crop_or_area = st.radio("Analyze by", ["item", "area"])
    selected = st.selectbox(f"Select {crop_or_area.title()}", df[crop_or_area].unique())
    subset = df[df[crop_or_area] == selected]
    for element in ['Area harvested', 'Yield', 'Production']:
        data = subset[subset['element'] == element].groupby('year')['value'].sum().reset_index()
        fig = px.line(data, x='year', y='value', title=f"{element} Trend for {selected}")
        st.plotly_chart(fig, use_container_width=True)

# --- 5. Environmental Relationships ---
def analyze_environmental_relationship(df):
    st.subheader("🌍 Area Harvested vs Yield")
    area_df = df[df['element'] == 'Area harvested']
    yield_df = df[df['element'] == 'Yield']
    merged = pd.merge(area_df, yield_df, on=['area', 'item', 'year'], suffixes=('_area', '_yield'))
    fig = px.scatter(merged, x='value_area', y='value_yield', color='item', 
                     title="Area Harvested vs Yield")
    st.plotly_chart(fig, use_container_width=True)

# --- 6. Input-Output Relationships ---
def analyze_input_output_relationship(df):
    st.subheader("🔁 Area vs Yield vs Production")
    area_df = df[df['element'] == 'Area harvested']
    yield_df = df[df['element'] == 'Yield']
    prod_df = df[df['element'] == 'Production']
    merged = area_df.merge(yield_df, on=['area', 'item', 'year'], suffixes=('_area', '_yield'))
    merged = merged.merge(prod_df, on=['area', 'item', 'year'])
    merged.rename(columns={'value': 'value_production'}, inplace=True)
    fig = px.scatter_3d(merged, x='value_area', y='value_yield', z='value_production', color='item',
                        title="3D View: Area vs Yield vs Production")
    st.plotly_chart(fig, use_container_width=True)

# --- 7. Comparative Yield Analysis ---
def compare_crop_yields(df):
    st.subheader("🌾 Compare Crop Yields")
    yield_df = df[df['element'] == 'Yield']
    mean_yields = yield_df.groupby('item')['value'].mean().reset_index().sort_values(by='value', ascending=False)
    fig = px.bar(mean_yields.head(20), x='item', y='value', title="Top 20 High-Yield Crops")
    st.plotly_chart(fig, use_container_width=True)

# --- 8. Region Production Comparison ---
def compare_region_production(df):
    st.subheader("🌍 Compare Region-wise Production")
    prod_df = df[df['element'] == 'Production']
    region_prod = prod_df.groupby('area')['value'].sum().reset_index().sort_values(by='value', ascending=False)
    fig = px.bar(region_prod.head(20), x='area', y='value', title="Top 20 Productive Regions")
    st.plotly_chart(fig, use_container_width=True)

# --- 9. Productivity Ratios ---
def analyze_productivity(df):
    st.subheader("🧠 Productivity Analysis")
    area_df = df[df['element'] == 'Area harvested']
    prod_df = df[df['element'] == 'Production']
    merged = pd.merge(area_df, prod_df, on=['area', 'item', 'year'], suffixes=('_area', '_prod'))
    merged['productivity'] = merged['value_prod'] / merged['value_area']
    fig = px.box(merged, x='item', y='productivity', title="Productivity (Production / Area Harvested)", points="all")
    st.plotly_chart(fig, use_container_width=True)

# --- 10. Outliers & Anomalies ---
def identify_outliers(df):
    st.subheader("🚨 Outliers in Yield or Production")
    element = st.selectbox("Select Element", ['Yield', 'Production'])
    selected_df = df[df['element'] == element]
    fig = px.box(selected_df, x='item', y='value', title=f"Outlier Detection in {element}", points="all")
    st.plotly_chart(fig, use_container_width=True)
# --- 11. Prediction ---
def production():
    compared_data= pd.read_csv('comapared_data.csv')
    df_wide_option=pd.read_csv('df_wide_option.csv')
    st.subheader("🔮 Predict Crop Production")

    # Dropdowns for Area, Item, and Year
    region = st.selectbox("Select Region", compared_data['Area'].unique())
    year = st.selectbox("Select Year", sorted(crop_df['year'].unique()))
    area_harvest = st.slider("Select Area Harvested", float(df_wide_option['Area Harvested (ha)'].min()), float(df_wide_option['Area Harvested (ha)'].max()))
    yield_value = st.slider("Select Yield (kg/ha)", float(df_wide_option['Yield (kg/ha)'].min()), float(df_wide_option['Yield (kg/ha)'].max()))
    crop = st.selectbox("Select Item", compared_data['Item'].unique())

    if st.button("Predict Production"):
        prediction = model_pediction(region,year,area_harvest,yield_value,crop)
        predicted_value = prediction[1][0]
        # Display the result
        st.success(f"📈 Predicted Production for a area harvest[{area_harvest}] and yield[{yield_value}] of {crop} in {region} ({year}): **{predicted_value}**")


# --- Sidebar Navigation ---

def sidebar_navigation():
    
   
    st.sidebar.title("📊 Analysis Sections")

    selectors = st.sidebar.radio('Choose an Data:', ["Crop Distribution",
    "Geographical Distribution",
    "Yearly Trends",
    "Growth Analysis",
    "Environmental Relationships",
    "Input-Output Relationships",
    "Compare Crop Yields",
    "Compare Region Production",
    "Productivity Analysis",
    "Outliers & Anomalies",
    ":blue[Crop Production Prediction]"])

    if selectors == "Crop Distribution":
        analyze_crop_distribution(crop_df)
    elif selectors == "Geographical Distribution":
        analyze_geographical_distribution(crop_df)
    elif selectors == "Yearly Trends":
        analyze_yearly_trends(crop_df)
    elif selectors == "Growth Analysis":
        analyze_growth_analysis(crop_df)
    elif selectors == "Environmental Relationships":
        analyze_environmental_relationship(crop_df)
    elif selectors == "Input-Output Relationships":
        analyze_input_output_relationship(crop_df)
    elif selectors == "Compare Crop Yields":
        compare_crop_yields(crop_df)
    elif selectors == "Compare Region Production":
        compare_region_production(crop_df)
    elif selectors == "Productivity Analysis":
        analyze_productivity(crop_df)
    elif selectors == "Outliers & Anomalies":
        identify_outliers(crop_df)
    else :
        production()


sidebar_navigation()
