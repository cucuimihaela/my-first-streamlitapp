import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import json
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from copy import deepcopy



#Load the data

@st.cache
def load_data(path):
    if '.csv' in path:
        df = pd.read_csv(path)
        return df
    if '.geojson' in path:
        geojson = json.load(open(path))
        return geojson




mpg_df_raw = load_data(path="../data/raw/renewable_power_plants_CH.csv")
df = deepcopy(mpg_df_raw)

geojson_raw = load_data(path="../data/raw/georef-switzerland-kanton.geojson")
geojson = deepcopy(geojson_raw)

#Connect the geojson to the dataframe

codes=[]
name=[]
for index in range (26):
    codes.append(geojson['features'][index]['properties']['kan_code'])
    name.append(geojson['features'][index]['properties']['kan_name'])

abbr=['GE','SH','UR','BE','FR','AG','GR','LU','BS','TI','OW','AR','SO','SZ','JU','SG','VS','TG','VD','BL','ZH','NW','GL','NE','ZG','AI']
df_kan=pd.DataFrame({'code':codes,'canton_name':name,'canton':abbr})
df_kan.reset_index()
res=pd.merge(df,df_kan, how='left', on='canton')

#Group data for first map
df_grouped=res.groupby(['canton','code','canton_name','energy_source_level_1']).agg({'electrical_capacity':'sum'})
df_grouped=df_grouped.reset_index()

fig=  px.choropleth_mapbox(df_grouped,geojson=geojson,mapbox_style="carto-positron", color='electrical_capacity',
                            locations="code",featureidkey="properties.kan_code",
                           center={"lat": 46.8182, "lon": 8.2275},zoom=6.8,
                            hover_name='canton_name',
                            hover_data={'electrical_capacity':':.1f','code':False},
                           color_continuous_scale='greens')

fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0})
#fig.update_layout(title_text='Renewable Energy Capacity by Canton (MW)')

st.title("Renewable energy in Switzerland")
st.header("Electrical Capacity by canton")

st.plotly_chart(fig)


