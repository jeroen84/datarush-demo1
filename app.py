# from flask import Flask
import dash
import dash_html_components as html
import dash_core_components as dcc
from plotly_express import line
from plotly.subplots import make_subplots
import pandas as pd

df = pd.read_csv("marketdata.csv", index_col="Date")
# remove empty data points, for visualisation purposes
df.dropna(inplace=True)

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
                x='Date',
                y='Correlation',
                title="Correlation Equities vs interest rates")

# set up the server
dash_app = dash.Dash(__name__)
app = dash_app.server

# define the layout of the dashboard
dash_app.title = "Financial dashboard"
dash_app.layout = html.Div(
    [
        dcc.Markdown('''
        # A basic financial data dashboard using Dash!

        Just try out this *simple* dashboard! For more information, \
            please go to https://www.datarush.nl

        ***

        ### **Prices**

        Please find the prices of the FTSE All-World index (LHS) and \
            the 30 year EUR interest rate (RHS).
        '''),
        dcc.Graph(figure=fig),
        dcc.Markdown('''
        ***

        ### **Correlation**

        Please find the 30 day rolling window [correlation]\
            (https://en.wikipedia.org/wiki/Correlation_and_dependence)\
                between the FTSE All-World index and \
                    the 30 year EUR interest rate.

        Note the swings in positive and negative correlations, \
            especially the relatively large negative correlation \
                during the months June, July and August.
        '''),
        dcc.Graph(figure=fig_corr)
    ]
)

# run the dashboard
if __name__ == '__main__':
    dash_app.run_server(debug=True)
