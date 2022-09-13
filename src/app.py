import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import json
import pandas as pd
import plotly
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from copy import deepcopy
import squarify
import matplotlib.pyplot as plt


st.title("Renewable energy in Switzerland" )


#Load the data

@st.cache
def load_data(path):
    if '.csv' in path:
        df = pd.read_csv(path)
        return df
    if '.geojson' in path:
        geojson = json.load(open(path))
        return geojson




mpg_df_raw = load_data(path="./data/raw/renewable_power_plants_CH.csv")
df = deepcopy(mpg_df_raw)

geojson_raw = load_data(path="./data/raw/georef-switzerland-kanton.geojson")
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

st.header("Total of " + str('{:.0f}'.format(res['electrical_capacity'].sum()))+' MW')
#Group data for first map
df_grouped=res.groupby(['canton','code','canton_name','energy_source_level_1']).agg({'electrical_capacity':'sum'})
df_grouped=df_grouped.reset_index()

df_grouped2=res.groupby(['canton','code','canton_name','energy_source_level_1','energy_source_level_2']).agg({'electrical_capacity':'sum'})
df_grouped2=df_grouped2.reset_index()
df_grouped3=df_grouped2.pivot_table(index=['canton_name','code'], columns='energy_source_level_2', values='electrical_capacity')
df_grouped3=df_grouped3.fillna(0)
df_grouped3['total']=df_grouped3['Bioenergy']+df_grouped3['Hydro']+df_grouped3['Solar']+df_grouped3['Wind']
df_grouped3=df_grouped3.sort_values(by='total', ascending=False).reset_index()
df_grouped_sq=res.groupby('energy_source_level_2')['electrical_capacity'].sum().reset_index().sort_values(by='electrical_capacity',ascending=False)
df_grouped_sq['label']=df_grouped_sq.apply(lambda row: (row['energy_source_level_2']+ " "+ str('{:.0f}%'.format(row['electrical_capacity']/df_grouped_sq['electrical_capacity'].sum()*100))), axis=1)


fig10, ax = plt.subplots(nrows=1, ncols=1,figsize=(10,5))

ax=squarify.plot(sizes=df_grouped_sq['electrical_capacity'], label=df_grouped_sq['label'], alpha=.8 ,
                 color=['orange','blue','lightgreen','grey'],pad=1,
                     text_kwargs={'fontsize': 10})


plt.axis('off')
plt.subplots_adjust(left=-0.5)
plt.tight_layout()

st.pyplot(fig10)

types=['All','Solar','Hydro','Wind','Bioenergy']
level1=st.radio(label='Show by type', options=types, horizontal=True)
for type in types[1:]:
    if level1==type:
        color=type
        fig=  px.choropleth_mapbox(df_grouped3,geojson=geojson,mapbox_style="carto-positron", color=type,
                            locations="code",featureidkey="properties.kan_code",
                           center={"lat": 46.8182, "lon": 8.2275},zoom=6,
                            #hover_name='canton_name',
                           hover_data={type: ':.1f', 'code': False},
                           color_continuous_scale='YlGn',
                           #labels={'type': 'elec capacity (KW)'}
                        )
        break
    else:
        fig = px.choropleth_mapbox(df_grouped, geojson=geojson, mapbox_style="carto-positron", color='electrical_capacity',
                                   locations="code", featureidkey="properties.kan_code",
                                   center={"lat": 46.8182, "lon": 8.2275}, zoom=6,
                                   hover_name='canton_name',
                                   hover_data={'electrical_capacity': ':.1f', 'code': False},
                                   color_continuous_scale='YlGn',
                                   labels={'electrical_capacity': 'elec capacity (KW)'})

fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0})
fig.update_layout(title='Renewable Energy Capacity by Canton (MW)')




# Setting up columns




# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)
#if st.checkbox("Show Dataframe"):
#    st.subheader("This is my dataset:")
#    st.dataframe(data=df_grouped)





fig7 = go.Figure(data=[
    go.Bar(x=df_grouped3.index, y=df_grouped3['Hydro'],name='hydro',marker_color='blue'),
    go.Bar(x=df_grouped3.index, y=df_grouped3['Solar'],name='solar',marker_color='orange'),
    go.Bar(x=df_grouped3.index, y=df_grouped3['Wind'],name='wind',marker_color='grey'),
    go.Bar(x=df_grouped3.index, y=df_grouped3['Bioenergy'],name='bioenergie',marker_color='lightgreen')])
fig7.update_layout(margin={"r":0,"t":45,"l":0,"b":0})
# Update the layout

fig7.update_layout(
    barmode="stack",
    plot_bgcolor="white",
    hovermode="x unified",
    title={'text': "Renewable energy by type", "font": {"size": 24}}
)



st.plotly_chart(fig)

st.plotly_chart(fig7)

