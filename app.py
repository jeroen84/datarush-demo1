import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from plotly_express import line
from plotly.subplots import make_subplots
import pandas as pd


_URL = {"ABP": "https://www.abp.nl/over-abp/financiele-situatie/dekkingsgraad/",
        "PFZW": "https://www.pfzw.nl/over-ons/dit-presteren-we/dekkingsgraad.html"}


def getActueleDekkingsgraden():

    # dic for changing the date (Maanden) values
    _DIC = {"januari ": "31-01-",
            "februari ": "28-02-",
            "maart ": "31-03-",
            "april ": "30-04-",
            "mei ": "31-05-",
            "juni ": "30-06-",
            "juli ": "31-07-",
            "augustus ": "31-08-",
            "september ": "30-09-",
            "oktober ": "31-10-",
            "november ": "30-11-",
            "december ": "31-12-"}

    # get data from html pages

    abp_df = pd.read_html(_URL["ABP"],
                          header=0,
                          thousands=".",
                          decimal=",")[0]

    pfzw_df = pd.read_html(_URL["PFZW"],
                           header=0,
                           thousands=".",
                           decimal=",")[0]

    # change column values from string to float
    abp_df["Dekkingsgraad"] = abp_df["Dekkingsgraad"].str.replace(",", ".")
    abp_df["Dekkingsgraad"] = abp_df["Dekkingsgraad"].str.rstrip("%").astype(float)

    # manipulate certain columns in order to process properly
    pfzw_df["Maand"] = pfzw_df["Maand"].str.lower()
    pfzw_df["Maand"] = pfzw_df["Maand"].str.strip("\u200b")

    pfzw_df["Dekkingsgraad"] = \
        pfzw_df["Dekkingsgraad"].str.strip("\u200b")  # remove width spaces
    pfzw_df["Dekkingsgraad"] = \
        pfzw_df["Dekkingsgraad"].str.replace(",", ".")
    pfzw_df["Dekkingsgraad"] = \
        pfzw_df["Dekkingsgraad"].str.rstrip("%").astype(float)

    # merge two dataframes
    df = abp_df.merge(pfzw_df,
                      how="left",
                      left_on="Maanden",
                      right_on="Maand",
                      suffixes=("_ABP", "_PFZW"))

    # keep the necessary columns
    df = df[["Maanden",
             "Dekkingsgraad_ABP",
             "Dekkingsgraad_PFZW"]].dropna()

    # find and replace
    for x in _DIC:
        df["Maanden"] = df["Maanden"].str.replace(x, _DIC[x])

    # change strings to datetime format
    df["Maanden"] = df["Maanden"].astype('datetime64[ns]')

    # rename column Maanden to Datum
    df.rename(columns={"Maanden": "Datum",
                      "Dekkingsgraad_ABP": "ABP",
                      "Dekkingsgraad_PFZW": "PFZW"}, inplace=True)

    # need to return a melted df in order for
    # plotly to plot multiple lines in chart
    df_melt = df.melt(id_vars="Datum", value_vars=["ABP", "PFZW"])
    df_melt.rename(columns={"value": "dekkingsgraad",
                            "variable": "fonds"}, inplace=True)
    return df_melt


# load the dataset, ignoring empty datapoints
df = pd.read_csv("marketdata.csv", index_col="Date").dropna()

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
                x="Date",
                y="Correlation",
                title="Correlation Equities vs interest rates")

# create the third graph, showing the 'Dekkingsgraden'
df_dgr = getActueleDekkingsgraden()
fig_dgr = line(df_dgr,
               x="Datum",
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
