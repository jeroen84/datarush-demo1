import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from plotly_express import line
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3

_URL = {"ABP": "https://www.abp.nl/over-abp/financiele-situatie/dekkingsgraad/",
        "PFZW": "https://www.pfzw.nl/over-ons/dit-presteren-we/dekkingsgraad.html"}

# load the dataset, ignoring empty datapoints
conn = sqlite3.connect("marketdata.db")
_query = "SELECT date, name, value FROM marketdata"
df = pd.read_sql(_query, conn, index_col="date")
df = df.pivot_table(values="value", index="date", columns="name").dropna()

# load the dekkingsgraden dataset
_query2 = "SELECT date, name, value FROM dekkingsgraad"
df_dgr = pd.read_sql(_query2, conn).sort_values("date")
df_dgr["value"] = df_dgr["value"] * 100
df_dgr.rename(columns={"name": "fonds",
                       "value": "dekkingsgraad"}, inplace=True)
# close connection
conn.close()

# create a df with the correlations
df_corr = pd.DataFrame(df["FTSEAW"].rolling(30).corr(df["EUSA30"]))
df_corr.rename(columns={0: "Correlation"}, inplace=True)
df_corr.reset_index(inplace=True)

# make the first graph, showing the prices of the two drivers
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_scatter(secondary_y=False, x=df.index, y=df["FTSEAW"],
                marker_color="blue", name="FTSE All-World")
fig.add_scatter(secondary_y=True,  x=df.index, y=df["EUSA30"],
                marker_color="red", name="30Y interest rate")
fig.update_layout(title_text="Equities vs interest rates")

# create the second graph, showing the correlation
fig_corr = line(df_corr,
                x="date",
                y="Correlation",
                title="Correlation Equities vs interest rates")

# create the third graph, showing the 'Dekkingsgraden'

fig_dgr = line(df_dgr,
               x="date",
               y="dekkingsgraad",
               color="fonds",
               title="Actuele dekkingsgraden")

# set up the server, using a bootstrap theme
dash_app = dash.Dash(__name__,
                     external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server

# define the layout of the dashboard
dash_app.title = "Financial dashboard"
dash_app.layout = dbc.Container(children=[
        dcc.Markdown('''

        # A basic financial data dashboard using Dash!

        Just try out this *simple* dashboard! For more information, \
            please go to https://www.datarush.nl

        ***
        '''),
        dcc.Tabs(children=[
            dcc.Tab(label="Pensioenfondsen", children=[
                dbc.Row(children=[
                    dbc.Col(children=[
                        dcc.Markdown('''
                                    _(Dutch)_

                                    Overzicht van de actuele dekkinsgraden \
                                    van de twee grootste pensioenfondsen van \
                                    Nederland: **ABP** en \
                                    **PFZW**.

                                    Bronnen:
                                    * [ABP](%s)
                                    * [PFZW](%s)
                                    ''' % (_URL["ABP"], _URL["PFZW"]))
                    ], width=4),
                    dbc.Col(children=[
                        dcc.Graph(figure=fig_dgr)
                    ])
                ])
            ]),
            dcc.Tab(label="Risk factors", children=[
                dbc.Row(children=[
                    dbc.Col(children=[
                        dcc.Markdown('''
                        Please find the prices of the FTSE All-World index \
                        (LHS) and the 30 year EUR interest rate (RHS).
                        ''')
                    ], width=4),
                    dbc.Col(children=[
                        dcc.Graph(figure=fig)
                    ])
                ])
            ]),
            dcc.Tab(label="Correlations", children=[
                dbc.Row(children=[
                    dbc.Col(children=[
                        dcc.Markdown('''
                        Please find the 30 day rolling window [correlation]\
                            (https://en.wikipedia.org/wiki/Correlation_and_dependence)\
                                between the FTSE All-World index and \
                                    the 30 year EUR interest rate.

                        Note the swings in positive and negative correlations, \
                            especially the relatively large negative correlation \
                                during the months June, July and August.
                        ''')
                    ], width=4),
                    dbc.Col(children=[
                        dcc.Graph(figure=fig_corr)
                    ])
                ])
            ])
        ])
])

# run the dashboard
if __name__ == '__main__':
    dash_app.run_server(host="0.0.0.0",
                        debug=True)
