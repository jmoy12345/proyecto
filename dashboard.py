import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px

engine = create_engine('mysql+pymysql://a:a@localhost:3306/ufc')

# Traer los datos desde la base de datos
df_weight_classes = pd.read_sql("""
    SELECT wc.class,
           COUNT(DISTINCT fgtr.id) AS count_fighters
    FROM fights f
    JOIN fighters fgtr 
        ON f.fighter_1_id = fgtr.id OR f.fighter_2_id = fgtr.id
    JOIN weight_classes wc ON f.weight_class_id = wc.id
    GROUP BY wc.class 
    ORDER BY count_fighters DESC;
""", con=engine)

df_age_vs_wins = pd.read_sql("""
    SELECT fgtr.fighter_name,
        YEAR(e.event_date) AS fight_year,
        TIMESTAMPDIFF(YEAR, fgtr.date_of_birth, e.event_date) AS age,
        SUM(CASE 
                WHEN (fs.fighter_1_fight_conclusion = 'W' AND f.fighter_1_id = fgtr.id) OR
                        (fs.fighter_2_fight_conclusion = 'W' AND f.fighter_2_id = fgtr.id) 
                THEN 1 
                ELSE 0 
            END) AS wins_at_year
    FROM fighters fgtr
    JOIN fights f ON f.fighter_1_id = fgtr.id OR f.fighter_2_id = fgtr.id
    JOIN events e ON f.event_id = e.id
    JOIN fight_stats fs ON f.id = fs.fight_id
    WHERE fgtr.date_of_birth IS NOT NULL AND fgtr.wins IS NOT NULL
    GROUP BY fgtr.fighter_name, YEAR(e.event_date)
    ORDER BY fgtr.fighter_name DESC, fight_year DESC;
""", con=engine)

df_victories_losses = pd.read_sql("""
    SELECT wc.class,
           SUM(CASE WHEN f1.fighter_1_fight_conclusion = 'W' THEN 1 ELSE 0 END) + 
           SUM(CASE WHEN f1.fighter_2_fight_conclusion = 'F' THEN 1 ELSE 0 END) AS wins,
           SUM(CASE WHEN f1.fighter_1_fight_conclusion = 'F' THEN 1 ELSE 0 END) + 
           SUM(CASE WHEN f1.fighter_2_fight_conclusion = 'W' THEN 1 ELSE 0 END) AS losses
    FROM fights f
    JOIN weight_classes wc ON f.weight_class_id = wc.id
    JOIN fight_stats f1 ON f.id = f1.fight_id
    WHERE f1.fighter_1_fight_conclusion IN ('W', 'F')
       OR f1.fighter_2_fight_conclusion IN ('W', 'F')
    GROUP BY wc.class
    ORDER BY wins DESC;
""", con=engine)

df_fight_performance = pd.read_sql("""
    SELECT
        fgtr.fighter_name,
        fgtr.height,
        fgtr.weight,
        fgtr.wins,
        fgtr.losses
    FROM fighters fgtr
    WHERE fgtr.height IS NOT NULL
      AND fgtr.weight IS NOT NULL;
""", con=engine)

df_fight_probability = pd.read_sql("""
    SELECT 
        fgtr.id,
        fgtr.fighter_name,
        fgtr.wins,
        fgtr.losses,
        (fgtr.wins + fgtr.losses + fgtr.draws) AS total_fights,
        IF(fgtr.wins + fgtr.losses > 0, fgtr.wins / (fgtr.wins + fgtr.losses), 0) AS win_probability
    FROM fighters fgtr
    WHERE fgtr.wins + fgtr.losses + fgtr.draws > 0
    ORDER BY win_probability DESC;
""", con=engine)

df_victory_methods = pd.read_sql("""
    SELECT 
        wc.class, 
        m.method,
        COUNT(f.id) AS fight_count
    FROM fights f
    JOIN weight_classes wc ON f.weight_class_id = wc.id
    JOIN methods m ON f.method_id = m.id
    GROUP BY wc.class, m.method
    ORDER BY wc.class, fight_count DESC;
""", con=engine)

df_events_by_country = pd.read_sql("""
    SELECT 
        c.state,
        COUNT(e.id) AS event_count
    FROM events e
    JOIN countries c ON e.country_id = c.id
    GROUP BY c.state
    ORDER BY event_count DESC;
""", con=engine)

df_fights_per_year = pd.read_sql("""
    SELECT 
        YEAR(e.event_date) as year,
        COUNT(f.id) AS fight_count
    FROM fights f 
    JOIN events e ON e.id = f.event_id
    GROUP BY YEAR(e.event_date)
    ORDER BY YEAR(e.event_date) DESC;
""", con=engine)

# Inicializar la app Dash
load_figure_template('morph')
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH], suppress_callback_exceptions=True)

# Layout de la app
app.layout = html.Div([
    html.Div([
        # Sidebar
        html.Div([
            html.H2("UFC Dashboard"),
            html.Div([
                html.Button("Clases de Peso", id='btn-weight-class', n_clicks=0),
                html.Button("Edad vs Victorias", id='btn-age-wins', n_clicks=0),
                html.Button("Distribución de Victorias y Derrotas", id='btn-victories', n_clicks=0),
                html.Button("Métodos de Victoria", id='btn-victories-method', n_clicks=0),
                html.Button("Luchadores por Peso y Rendimiento", id='btn-performance', n_clicks=0),
                html.Button("Probabilidad de Victoria por Luchador", id='btn-fight-probability', n_clicks=0),
                html.Button("Eventos UFC por País", id='btn-event-country', n_clicks=0),
                html.Button("Luchas por Año", id='btn-fight-by-year', n_clicks=0),
            ], style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'})
        ], style={
            'width': '20%',
            'background': '#f8f8f8',
            'padding': '20px',
            'position': 'fixed',
            'height': '100vh',
            'boxShadow': '2px 0px 10px rgba(0,0,0,0.1)'
        }),

        # contenido central
        html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ], style={
            'marginLeft': '20%',  # Para dejar espacio al sidebar
            'padding': '20px'
        })

    ], style={'display': 'flex'})
])

# Definir los dashboards correspondientes para cada consulta SQL

# Dashboard de Clases de Peso
def weight_class_dashboard():
    return html.Div([
        html.H1('Clases de Peso con Mayor Cantidad de Luchadores'),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='weight-class-dropdown',
                    options=[{'label': x, 'value': x} for x in df_weight_classes['class'].unique()],
                    value=df_weight_classes['class'].head(5).unique(),  # Valor predeterminado, todas las clases seleccionadas
                    multi=True,  # Permite selección multiple
                    placeholder="Selecciona las clases de peso",
                    style={'width': '100%', 'padding': '10px'}
                ),
            ], style={'width': '30%', 'padding-right': '20px'}),  


            html.Div([
                dcc.Graph(id='pie-chart')
            ], style={'width': '70%'})
        ], style={'display': 'flex', 'align-items': 'center'})
    ])

@app.callback(
    Output('pie-chart', 'figure'),
    [Input('weight-class-dropdown', 'value')]
)
def update_pie_chart(selected_classes):
    filtered_df = df_weight_classes[df_weight_classes['class'].isin(selected_classes)]
    
    return {
        'data': [
            {'labels': filtered_df['class'], 
             'values': filtered_df['count_fighters'], 
             'type': 'pie'}
        ],
        'layout': {
            'title': 'Distribución de Luchadores por Clase de Peso'
        }
    }



# Dashboard de edad vs victorias
def age_vs_wins_dashboard():
    default_fighters = df_age_vs_wins['fighter_name'].head(3).unique()

    fig = px.scatter(
        df_age_vs_wins[df_age_vs_wins['fighter_name'].isin(default_fighters)],
        x='fight_year',
        y='age',
        color='fighter_name',
        size='wins_at_year',
        hover_data=['fighter_name', 'wins_at_year'],
        trendline='ols',
        trendline_scope='overall'
    )

    fig.update_layout(
        title='Edad de los Luchadores a lo Largo de los Años',
        xaxis_title='Año de la pelea',
        yaxis_title='Edad del luchador',
        legend_title='Luchador',
        hovermode='closest'
    )

    return html.Div([
        html.H1('Evolución de la Edad por Año de Pelea'),
        dcc.Dropdown(
            id='fighters-dropdown',
            options=[{'label': fighter, 'value': fighter} for fighter in df_age_vs_wins['fighter_name'].unique()],
            value=default_fighters,  # seleccionados por defecto
            multi=True,  # Multiple seleccion
            placeholder="Selecciona luchadores"
        ),
        dcc.Graph(id='age-vs-year-scatter', figure=fig) 
    ])

@app.callback(
    Output('age-vs-year-scatter', 'figure'),
    Input('fighters-dropdown', 'value')
)
def update_age_vs_year(selected_fighters):
    if len(selected_fighters) < 3:
        selected_fighters = df_age_vs_wins['fighter_name'].head(3).unique()

    filtered_df = df_age_vs_wins[df_age_vs_wins['fighter_name'].isin(selected_fighters)]

    fig = px.scatter(
        filtered_df,
        x='fight_year',
        y='age',
        color='fighter_name',
        size='wins_at_year',
        hover_data=['fighter_name', 'wins_at_year'],
        trendline='ols',
        trendline_scope='overall'
    )

    fig.update_layout(
        title='Edad de los Luchadores a lo Largo de los Años',
        xaxis_title='Año de la pelea',
        yaxis_title='Edad del luchador',
        legend_title='Luchador',
        hovermode='closest'
    )

    return fig  # Return the updated figure



# Dashboard de Distribución de Victorias y Derrotas
def victories_dashboard():
    default_classes = df_victories_losses['class'].head(3).unique()

    return html.Div([
        html.H1('Distribución de Victorias y Derrotas por Clase de Peso'),
        dcc.Dropdown(
            id='victories-dropdown',
            options=[{'label': x, 'value': x} for x in df_victories_losses['class'].unique()],
            value=list(default_classes),
            multi=True,
            placeholder="Selecciona clases de peso"
        ),
        dcc.Graph(id='stacked-bar-chart')
    ])

@app.callback(
    Output('stacked-bar-chart', 'figure'),
    Input('victories-dropdown', 'value')
)
def update_victories_bar_chart(selected_classes):
    if not selected_classes or len(selected_classes) == 0:
        selected_classes = df_victories_losses['class'].head(3).unique()

    filtered_df = df_victories_losses[df_victories_losses['class'].isin(selected_classes)]

    df_melted = filtered_df.melt(id_vars='class', value_vars=['wins', 'losses'], var_name='Resultado', value_name='Cantidad')

    fig = px.bar(
        df_melted,
        x='class',
        y='Cantidad',
        color='Resultado',
        barmode='stack',
        labels={'class': 'Clase de peso'},
        title='Victorias y Derrotas por Clase de Peso'
    )

    fig.update_layout(xaxis_title='Clase de peso', yaxis_title='Cantidad de peleas')

    return fig



# Dashboard de Métodos de Victoria
def victories_methods_dashboard():
    default_classes = df_victory_methods['class'].unique()[:3]
    default_methods = df_victory_methods['method'].unique()[:3]

    return html.Div([
        html.H1('Métodos de Victoria por Clase de Peso'),

        html.Div([
            html.Div([
                html.Label('Selecciona clases de peso:'),
                dcc.Dropdown(
                    id='victories-method-class-dropdown',
                    options=[{'label': c, 'value': c} for c in df_victory_methods['class'].unique()],
                    value=list(default_classes),
                    multi=True,
                    placeholder='Clases de peso'
                )
            ], className='col-12 col-md-6'),

            html.Div([
                html.Label('Selecciona métodos de victoria:'),
                dcc.Dropdown(
                    id='victories-method-dropdown',
                    options=[{'label': m, 'value': m} for m in df_victory_methods['method'].unique()],
                    value=list(default_methods),
                    multi=True,
                    placeholder='Métodos de victoria'
                )
            ], className='col-12 col-md-6')
        ], className='row mb-3'),

        dcc.Graph(id='bar-method-chart')
    ])


@app.callback(
    Output('bar-method-chart', 'figure'),
    Input('victories-method-class-dropdown', 'value'),
    Input('victories-method-dropdown', 'value')
)
def update_method_chart(selected_classes, selected_methods):
    # Fallback en caso de que el usuario borre todo
    if not selected_classes:
        selected_classes = df_victory_methods['class'].head(3).unique()
    if not selected_methods:
        selected_methods = df_victory_methods['method'].head(3).unique()
    filtered_df = df_victory_methods[
        df_victory_methods['class'].isin(selected_classes) &
        df_victory_methods['method'].isin(selected_methods)
    ]

    fig = px.bar(
        filtered_df,
        x='class',
        y='fight_count',
        color='method',
        barmode='group',
        labels={
            'class': 'Clase de peso',
            'fight_count': 'Cantidad de peleas',
            'method': 'Método de victoria'
        },
        title='Métodos de Victoria por Clase de Peso'
    )

    fig.update_layout(xaxis_title='Clase de peso', yaxis_title='Cantidad de peleas')

    return fig

# Dashboard de Rendimiento en función de Altura y Peso
def fight_performance_dashboard():
    default_fighters = df_fight_performance['fighter_name'].unique()[:3]  # Selecciona 3 por defecto

    return html.Div([
        html.H1('Relación entre Altura, Peso y Rendimiento'),
        dcc.Dropdown(
            id='performance-fighter-dropdown',
            options=[{'label': name, 'value': name} for name in df_fight_performance['fighter_name'].unique()],
            value=list(default_fighters),
            multi=True
        ),
        dcc.Graph(id='performance-scatter')
    ])

@app.callback(
    Output('performance-scatter', 'figure'),
    [Input('performance-fighter-dropdown', 'value')]
)
def update_performance_scatter(selected_fighters):
    filtered_df = df_fight_performance[df_fight_performance['fighter_name'].isin(selected_fighters)]

    fig = px.scatter(
        filtered_df,
        x='height',
        y='weight',
        size='wins',
        color='fighter_name',
        hover_data=['fighter_name', 'wins', 'losses'],
        labels={
            'height': 'Altura (In)',
            'weight': 'Peso (Libs)',
            'wins': 'Victorias',
            'losses': 'Derrotas'
        },
        title='Altura vs Peso con Indicador de Victorias'
    )

    fig.update_layout(hovermode='closest')

    return fig



# Dashboard de Probabilidad de Victoria vs Total de Peleas
def fight_probability_dashboard():
    default_fighters = df_fight_probability['fighter_name'].head(3).unique()

    return html.Div([
        html.H1('Relación entre Total de Peleas y Probabilidad de Victoria'),
        dcc.Dropdown(
            id='fight-probability-dropdown',
            options=[{'label': name, 'value': name} for name in df_fight_probability['fighter_name'].unique()],
            value=list(default_fighters),
            multi=True
        ),
        dcc.Graph(id='fight-probability-graph')
    ])
@app.callback(
    Output('fight-probability-graph', 'figure'),
    [Input('fight-probability-dropdown', 'value')]
)
def update_fight_probability_graph(selected_fighters):
    filtered_df = df_fight_probability[df_fight_probability['fighter_name'].isin(selected_fighters)]

    fig = px.scatter(
        filtered_df,
        x='total_fights',
        y='win_probability',
        color='fighter_name',
        hover_data=['fighter_name', 'wins', 'losses', 'total_fights'],
        labels={
            'total_fights': 'Total de Peleas',
            'win_probability': 'Probabilidad de Victoria'
        },
        title='Probabilidad de Victoria en función del Número de Peleas'
    )

    fig.update_layout(hovermode='closest')

    return fig


# Dashboard eventos por pais
# All states must be changed from the db error, should  be country
def events_by_country_dashboard():
    default_countries = df_events_by_country['state'].unique()[:3]

    return html.Div([
        html.H1('Eventos de UFC por País'),

        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': c, 'value': c} for c in df_events_by_country['state'].unique()],
            value=list(default_countries),
            multi=True,
            placeholder='Selecciona uno o más países'
        ),

        dcc.Graph(id='country-events-bar')
    ])
@app.callback(
    Output('country-events-bar', 'figure'),
    Input('country-dropdown', 'value')
)
def update_country_events_chart(selected_countries):
    if not selected_countries:
        selected_countries = df_events_by_country['state'].unique()[:3]

    filtered_df = df_events_by_country[df_events_by_country['state'].isin(selected_countries)]

    fig = px.bar(
        filtered_df,
        x='state',
        y='event_count',
        labels={'country': 'País', 'event_count': 'Eventos'},
        title='Número de Eventos de UFC por País'
    )

    fig.update_layout(xaxis_title='País', yaxis_title='Número de eventos', hovermode='closest')

    return fig

# Dashboard de Peleas por Año
def fights_per_year_dashboard():
    return html.Div([
        html.H1('Evolución de Peleas por Año', style={'textAlign': 'center', 'padding-bottom': '20px'}),
        
        html.Div([
            # Slider para seleccionar el rango
            html.Div([
                html.Label('Selecciona el rango de años:'),
                dcc.RangeSlider(
                    id='year-slider',
                    min=df_fights_per_year['year'].min(),
                    max=df_fights_per_year['year'].max(),
                    step=1,
                    marks=None,
                    value=[df_fights_per_year['year'].min(), df_fights_per_year['year'].max()],  # Valores por defecto
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], style={'width': '60%', 'padding': '20px'}), 

            html.Div([
                dcc.Graph(id='fights-per-year-line-chart')
            ], style={'width': '100%', 'padding': '20px'}),
        ], style={'padding': '20px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
    ])

@app.callback(
    Output('fights-per-year-line-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_fights_line_chart(year_range):
    start_year, end_year = year_range
    
    filtered_df = df_fights_per_year[(df_fights_per_year['year'] >= start_year) & (df_fights_per_year['year'] <= end_year)]
    
    fig = px.line(
        filtered_df,
        x='year',
        y='fight_count',
        markers=True,  #puntos en la línea
        labels={'year': 'Año', 'fight_count': 'Número de peleas'},
        title=f'Número de Peleas de UFC de {start_year} a {end_year}'
    )

    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis_title='Cantidad de Peleas',
        hovermode='x unified',
        width=800, 
        height=500,
    )

    return fig


# Cambiar contenido de page-content con url
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/age-vs-wins':
        return age_vs_wins_dashboard()
    elif pathname == '/victories':
        return victories_dashboard()
    elif pathname == '/victories-method':
        return victories_methods_dashboard()
    elif pathname == "/events_by_country":
        return events_by_country_dashboard()
    elif pathname == "/fights_by_year":
        return fights_per_year_dashboard()
    elif pathname == "/performance":
        return fight_performance_dashboard()
    elif pathname == "/fight_probability":
        return fight_probability_dashboard()
    else:
        return weight_class_dashboard()  # Default dashboard

# Cambiar url con boton
@app.callback(
    Output('url', 'pathname'),
    [Input('btn-weight-class', 'n_clicks'),
     Input('btn-age-wins', 'n_clicks'),
     Input('btn-victories', 'n_clicks'),
     Input('btn-victories-method', 'n_clicks'),
     Input("btn-event-country", 'n_clicks'),
     Input("btn-fight-by-year", 'n_clicks'),
     Input("btn-performance", "n_clicks"),
     Input("btn-fight-probability", "n_clicks")]
)
def update_url(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8):
    ctx = dash.callback_context
    if not ctx.triggered:
        return '/'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-weight-class':
            return '/'
        elif button_id == 'btn-age-wins':
            return '/age-vs-wins'
        elif button_id == 'btn-victories':
            return '/victories'
        elif button_id == 'btn-victories-method':
            return '/victories-method'
        elif button_id == 'btn-event-country':
            return '/events_by_country'
        elif button_id == "btn-fight-by-year":
            return "/fights_by_year"
        elif button_id == 'btn-performance':
            return '/performance'
        elif button_id == "btn-fight-probability":
            return '/fight_probability'

if __name__ == '__main__':
    app.run(debug=True)
