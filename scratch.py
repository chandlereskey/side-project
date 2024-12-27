import pandas as pd
import plotly.express as px
from connection import engine
# make a minimal dataframe
df = pd.read_sql('select state, measure_name, sum(raw_value) as total from [dbo].[CountyHealthRankings] group by state, measure_name', engine)




# plot a choropleth with color range by count per state
fig = px.choropleth(df,
                    locations='state',
                    locationmode="USA-states",
                    scope="usa",
                    color='total',
                    color_continuous_scale="Oranges",
                   )
# center the title
fig.update_layout(title_text='Something random', title_x=0.5)
# label states with count
fig.add_scattergeo(
    locations=df['state'],
    locationmode="USA-states",
    text = df['total'],
    featureidkey="properties.NAME_3",
    mode = 'text',
    textfont=dict(
            family="helvetica",
            size=24,
            color="white"
    )) 
fig.show()

# df.to_sql('todos', connection, if_exists='append', index=False)