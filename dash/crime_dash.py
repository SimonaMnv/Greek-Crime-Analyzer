from datetime import date
import pandas as pd
from dash import no_update
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash
import dash_table
from NLP.POS.pos import analyse_victim
from elasticsearchapp.query_results import get_n_raw_data, get_records_per_category
import plotly.express as px

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)

global UNIQUE_TERMS
global END_DATE

UNIQUE_TERMS = ['ΔΟΛΟΦΟΝΙΑ', 'ΝΑΡΚΩΤΙΚΑ', 'ΤΡΟΜΟΚΡΑΤΙΚΗ ΕΠΙΘΕΣΗ', 'ΛΗΣΤΕΙΑ', 'ΣΕΞΟΥΑΛΙΚΟ ΕΓΚΛΗΜΑ']


def generated_data(start_date, end_date, crime_type):
    # load data
    data = get_n_raw_data(crime_type, start_date, end_date)

    for datum in data:
        refactored_date = datum['Date'].split("T")
        datum['Date'] = refactored_date[0]

    df = pd.DataFrame(data=data)
    df.to_csv('data/' + crime_type + '.csv', index=False)

    return df


# top banner
def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.Button(
                        id="learn-more-button", children="Greek Crime Analytics", n_clicks=0
                    ),
                ],
            ),
        ],
    )


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)


def create_card(title, i):
    records = get_records_per_category()

    card = dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className="card-title"),
                html.Br(),
                html.H3(records[i], className="card-subtitle"),
            ]
        ),
    )
    return card


app.layout = html.Div(
    children=[
        html.Div(
            className="left_menu",
            children=[
                html.Div(
                    children=[
                        create_card("Total Crime Articles", 0),
                        create_card("Murder Crime Articles", 1),
                        create_card("Drugs Crime Articles", 2),
                        create_card("Theft Crime Articles", 3),
                        create_card("Terrorism Crime Articles", 4),
                        create_card("Sexual Crime Articles", 5),
                    ],
                ),
            ]
        ),

        html.Div(
            className="right_content",
            children=[
                build_banner(),  # this is the top top part
                dcc.Interval(
                    id="interval-component",
                    interval=2 * 1000,  # in milliseconds
                    n_intervals=50,  # start at batch 50
                    disabled=True,
                ),
                html.Div(id='choices', children=[
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=date(2012, 1, 1),
                        max_date_allowed=date.today(),
                        initial_visible_month=date.today(),
                        display_format='Y-MM-DD',
                        start_date=date(2012, 1, 1),
                        end_date=date(2012, 12, 12)
                    ),
                ]),

                # popup modal
                dcc.Loading(
                    id="loading-2",
                    color='#36505a',
                    type="default",
                    children=[
                        html.Div(
                            id="modal-div",
                            children=[
                                dbc.Modal(
                                    children=[
                                        dbc.ModalFooter(
                                            dbc.Button("Close", id="close", className="ml-auto")
                                        ),
                                    ],
                                    id="modal"
                                ),
                            ]),
                    ]),
                html.Div(
                    id="app-container",
                    children=[
                        html.Div(
                            id="news_table",
                            children=[
                                html.Div(
                                    id="selector",
                                    children=[
                                        # drop down menu
                                        generate_section_banner("Filter by Crime Type"),
                                        dcc.Loading(
                                            id="loading-1",
                                            color='#36505a',
                                            type="default",
                                            children=[
                                                dcc.Dropdown(
                                                    id='crime_type_dd',
                                                    options=[],
                                                    clearable=False,
                                                ),
                                            ]),
                                    ]),
                                dcc.Loading(
                                    id="loading-data",
                                    type="cube",
                                    color='#36505a',
                                    children=[
                                        html.Div(
                                            id="fdk-part",
                                            children=[
                                                html.Button('Apply Filters', id='btn-submit', n_clicks=0,
                                                            style=dict(width='100%')),
                                                generate_section_banner("Results"),
                                                dash_table.DataTable(
                                                    id='crime_table',
                                                    page_size=8,
                                                    fixed_rows={'headers': True},
                                                    style_table={'overflowY': 'scroll'},
                                                    style_header={
                                                        'backgroundColor': '#314b56',
                                                        'color': 'white',
                                                        'fontWeight': 'bold'
                                                    },
                                                    style_as_list_view=True,
                                                    style_cell={
                                                        'backgroundColor': '#1e2130',
                                                        'color': 'white',
                                                        'textAlign': 'left',
                                                        'padding': '15px',
                                                        'font-family': 'sans-serif',
                                                        'minWidth': '180px', 'width': '180px',
                                                        'maxWidth': '450px',
                                                        'overflow': 'hidden',
                                                        'textOverflow': 'ellipsis',
                                                    },
                                                    style_data_conditional=(),
                                                    css=[{
                                                        'selector': '.dash-table-tooltip',
                                                        'rule': 'background-color: black; font-family: sans-serif;'
                                                    }],
                                                    tooltip_delay=0,
                                                    tooltip_duration=None,
                                                ),
                                            ]),
                                        html.Div(
                                            id="chart-part",
                                            children=[
                                                generate_section_banner("Pie-chart Analysis"),
                                                dcc.Dropdown(
                                                    id='chart_values',
                                                    value='Sex',
                                                    options=[{'value': x, 'label': x}
                                                             for x in ['Sex', 'Ages']],
                                                    clearable=False
                                                ),
                                                dcc.Graph(id="pie_chart"),
                                            ], style={"margin-top": "50px", 'display': 'none'}),
                                    ]),
                            ]),
                    ]),
            ],
        ),
    ],
)


@app.callback(
    Output("pie_chart", "figure"),
    Output("chart-part", "style"),
    [
        Input('crime_table', 'data'),
        Input('chart_values', 'value'),
    ])
def generate_chart(table_values, chart_values):
    values = []

    if not table_values:
        return {}, {'display': 'none'}
    else:
        if chart_values == 'Sex':
            for data in table_values:
                values.append(data['Victim'])

            df = pd.DataFrame(data=values, columns=['Victim'])
            df['frequency'] = df['Victim'].map(df['Victim'].value_counts())

            fig = px.pie(df, values=df['frequency'], names=df['Victim'],
                         color_discrete_sequence=px.colors.qualitative.T10)
            fig.update_layout(
                plot_bgcolor='rgba(49, 75, 86, 1)',
                paper_bgcolor='rgba(22, 26, 40, 1)',
                font=dict(
                    family="sans-serif",
                    size=13,
                    color="#ffffff"
                ),
            )

            return fig, {'display': 'block'}
        elif chart_values == 'Ages':
            for data in table_values:
                ages = data['Ages']
                for age in ages:
                    values.append(age)

            values = list(map(lambda sub: int(''.join([i for i in sub if i.isnumeric()])), values))  # only numerical

            # converted to age groups
            ages = pd.DataFrame(values, columns=['age'])
            bins = [0, 18, 30, 40, 50, 60, 70, 120]
            labels = ['0-17', '18-29', '30-39', '40-49', '50-59', '60-69', '70+']
            ages['agerange'] = pd.cut(ages.age, bins, labels=labels, include_lowest=True)

            df = pd.DataFrame(data=ages['agerange'].values, columns=['Ages'])
            df['frequency'] = ages['agerange'].map(ages['agerange'].value_counts())

            fig = px.pie(df, values=df['frequency'], names=ages['agerange'])
            fig.update_layout(
                plot_bgcolor='rgba(49, 75, 86, 1)',
                paper_bgcolor='rgba(22, 26, 40, 1)',
                font=dict(
                    family="sans-serif",
                    size=13,
                    color="#ffffff"
                ),
            )

            return fig, {'display': 'block'}


@app.callback(
    [
        Output('crime_table', 'data'),
        Output('crime_table', 'columns'),
        Output('crime_table', 'style_data_conditional')
    ],
    [
        Input("crime_type_dd", "value"),
        Input('btn-submit', 'n_clicks'),
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')
    ],
)
def update_values_and_charts(crime_type, btn, start_date, end_date):
    # apply on each click
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    victims = []
    c_status = []
    acts = []
    ages = []
    dates = []

    if 'btn-submit' in changed_id:
        crime_merged_table = generated_data(start_date, end_date, crime_type)

        for type, body, title in zip(crime_merged_table['Type'], crime_merged_table['Body'],
                                     crime_merged_table['Title']):
            context = title + " " + body
            if crime_type == 'ΔΟΛΟΦΟΝΙΑ':  # elastic top verb similarity mixed with POS analysis and NER analysis
                columns = ['Date', 'Title', 'Body', 'Type', 'Victim', 'Criminal Status', 'Acts', 'Ages', 'Crime Date']

                article_summary, victim_gender, criminal_status, act, age, date = analyse_victim(context, crime_type)
                victims.append(victim_gender)
                c_status.append(criminal_status)
                acts.append([str(x) + " " for x in act])
                ages.append([str(x) + " " for x in age])
                dates.append([str(x) + " " for x in date])

        crime_merged_table['Victim'] = victims
        crime_merged_table['Criminal Status'] = c_status
        crime_merged_table['Acts'] = acts
        crime_merged_table['Ages'] = ages
        crime_merged_table['Crime Date'] = dates

        if len(crime_merged_table) == 0:
            return no_update, no_update, no_update

        data_table = crime_merged_table.to_dict("records")

        return data_table, [{"name": i, "id": i} for i in columns], (
            [
                {
                    "if": {"state": "selected"},  # 'active' | 'selected'
                    "backgroundColor": "rgba(0, 116, 217, 0.3)",
                    "border": "1px solid blue",
                }
            ]
        )

    else:
        return [], [], []


@app.callback(
    [
        Output("modal", "is_open"),
        Output('modal', 'children'),
    ],
    [
        Input("crime_table", "active_cell"),  # open button
        Input("close", "n_clicks"),  # close button
        Input("crime_table", "data"),
    ],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, crime_table, is_open):
    if not crime_table:
        return no_update, no_update

    if n1 is not None:
        if (n1 and n1['column_id'] == 'Title') or n2:
            return not is_open, (
                dbc.ModalHeader("Full Title of Article"),
                dbc.ModalBody(children=[
                    html.Label(html.A(crime_table[n1['row']]['Title']))]
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            )
        elif (n1 and n1['column_id'] == 'Body') or n2:
            return not is_open, (
                dbc.ModalHeader("Full Body of Article"),
                dbc.ModalBody(children=[
                    html.Label(html.A(crime_table[n1['row']]['Body']))]
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            )
        else:
            return is_open, no_update
    else:
        return no_update, no_update


@app.callback([
    Output("crime_type_dd", "options"),
    Output("crime_type_dd", "value"),
],
    [
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')
    ])
def generate_initial_date_terms(start_date, end_date):
    global END_DATE
    END_DATE = end_date

    return [{'value': x, 'label': x}
            for x in UNIQUE_TERMS], UNIQUE_TERMS[0]


if __name__ == '__main__':
    app.run_server(debug=True)
