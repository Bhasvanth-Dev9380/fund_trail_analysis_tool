import webbrowser

import pandas as pd
import networkx as nx
from dash import dash_table
from dash import dcc, html
from threading import Timer
import io
import pyautogui
import dash_bootstrap_components as dbc
import numpy as np
from dash.dependencies import Input, Output
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
from plotly.subplots import make_subplots
import plotly.express as px
import dash
import plotly.graph_objects as go
from screeninfo import get_monitors

def get_screen_resolution():
    # Get the screen resolution
    monitor = get_monitors()[0]
    return monitor.width, monitor.height

# Load the English language model in Spacy
nlp = spacy.load('en_core_web_sm')

# Step 1: Load the data
def load_data(file_path):
    # Load data from CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Print basic information about the DataFrame
    print(df.head())
    print(df.info())

    # Preprocessing (drop duplicates, handle missing values, etc. if necessary)
    df = df.drop_duplicates()

    return df
def scale_data(df):
    # Fill NaN values with 0 or any appropriate value based on the context
    df = df.fillna(0)

    # Convert Amount column to numeric (float) to handle any non-numeric values
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    # Convert Transaction_ID column to integers
    df['Transaction_ID'] = df['Transaction_ID'].astype(int)

    # Select only numeric columns for scaling
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    # Handle non-numeric columns (e.g., drop or encode them)
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    if len(non_numeric_cols) > 0:
        print("Non-numeric columns found:", non_numeric_cols)
        # we can choose to drop non-numeric columns if they are not essential for the analysis.
        df = df.drop(columns=non_numeric_cols)

        # Alternatively, we can encode categorical columns using techniques like one-hot encoding.

    # Print basic information about the DataFrame before scaling
    print("Before scaling:")
    print(df[numeric_cols].dtypes)

    # Scaling the data using Min-Max scaling (Normalization) for selected columns
    df_scaled = (df[numeric_cols] - df[numeric_cols].min()) / (df[numeric_cols].max() - df[numeric_cols].min())

    # Replace the scaled values in the original DataFrame
    df[numeric_cols] = df_scaled

    # Check for NaN values
    if df_scaled.isnull().any().any():
        print("NaN values found in the DataFrame.")

    # Print basic information about the DataFrame after scaling
    print("After scaling:")
    print(df[numeric_cols].dtypes)

    return df

# Step 5: Perform network analysis for fraud detection and circular transaction pattern detection
def detect_fraud_network(data):
    # Check if 'Source' and 'Target' columns are present in the data
    Source_Target_cols = ['Source', 'Target']
    if not all(col in data.columns for col in Source_Target_cols):
        raise ValueError("Error: 'Source' and 'Target' columns are required for network analysis.")

    # Create a graph from the financial data
    G = nx.from_pandas_edgelist(data, 'Source', 'Target', create_using=nx.Graph())

    # Apply network metrics and identify suspicious nodes or edges

    # Compute the degree centrality for each node
    degree_centrality = nx.degree_centrality(G)
    degree_centrality_series = pd.Series(degree_centrality)

    # Identify the nodes with high degree centrality (above the 95th percentile)
    high_degree_nodes = degree_centrality_series[degree_centrality_series > degree_centrality_series.quantile(0.95)]
    high_degree_nodes = list(high_degree_nodes.index)

    # Compute the betweenness centrality for each edge
    betweenness_centrality = nx.edge_betweenness_centrality(G)
    betweenness_centrality_series = pd.Series(betweenness_centrality)

    # Identify the edges with high betweenness centrality (above the 95th percentile)
    high_betweenness_edges = betweenness_centrality_series[
        betweenness_centrality_series > betweenness_centrality_series.quantile(0.95)
    ]
    high_betweenness_edges = list(high_betweenness_edges.index)

    # Detect circular transaction patterns using cycle detection
    circular_transactions = []

    # Find all simple cycles in the graph
    all_cycles = nx.simple_cycles(G)

    # Iterate over cycles and find those with more than 2 nodes
    for cycle in all_cycles:
        if len(cycle) > 2:
            circular_transactions.append(cycle)

    return high_degree_nodes, high_betweenness_edges, circular_transactions

# Additional Step 1: Data Linking and Graph Creation
def create_transaction_graph(data):
    # Create a directed graph to represent financial transactions
    G = nx.DiGraph()

    # Add nodes (parties involved) to the graph
    for party in data['Source'].unique():
        G.add_node(party)

    # Add edges (transactions) between parties
    for index, row in data.iterrows():
        G.add_edge(row['Source'], row['Target'], Amount=row['Amount'], transaction_id=row['Transaction_ID'])

    return G

# Additional Step 2: Graph Analysis for Fund Flow Detection
def detect_fund_flow_patterns(graph):
    # Perform graph analysis to identify suspicious fund flow patterns
    # For example, find all simple cycles in the graph

    # Identify frequent transactions between parties
    frequent_transactions = [(Source, Target, data['Amount']) for Source, Target, data in graph.edges(data=True) if data['Amount'] > 50]

    return frequent_transactions

# Additional Step 3: Money Laundering Detection
def detect_money_laundering(graph):
    # Implement money laundering detection algorithms based on graph analysis
    # For example, detect circular transactions or transactions with multiple intermediaries

    # Detect circular transactions (cycles) in the graph
    circular_transactions = [cycle for cycle in nx.simple_cycles(graph) if len(cycle) > 2]

    # Detect transactions with multiple intermediaries
    transactions_with_multiple_intermediaries = [(Source, Target) for Source, Target, data in graph.edges(data=True)
                                                 if graph.out_degree(Source) > 1 and graph.in_degree(Target) > 1]

    return circular_transactions, transactions_with_multiple_intermediaries


# Additional Step 6: Visualize Fund Flow Detection Results
def visualize_fund_flow_detection_results(frequent_transactions):
    # Convert the generator into a list
    frequent_transactions = list(frequent_transactions)

    # Convert the tuple of dictionaries into a list of dictionaries
    frequent_transactions = [{"Source": t[0], "Target": t[1], "Frequency": t[2]} for t in frequent_transactions]

    # Create a subplot for the graph
    fig = make_subplots(rows=1, cols=1, subplot_titles=["Frequent Transactions between Parties"])

    # Bar graph for Frequent Transactions
    party_names = [f'{transaction["Source"]} -> {transaction["Target"]}' for transaction in frequent_transactions]
    frequencies = [transaction["Frequency"] for transaction in frequent_transactions]

    fig.add_trace(go.Bar(
        x=party_names,
        y=frequencies,
        name='Frequent Transactions',
    ), row=1, col=1)

    # Update layout for the frequent transactions subplot
    fig.update_xaxes(title_text="Transaction Parties", row=1, col=1)
    fig.update_yaxes(title_text="Frequency", row=1, col=1)

    # Update layout for the entire figure
    fig.update_layout(title="Frequent Transactions Detection Results", showlegend=False)

    # Show the figure
    return fig


# Additional Step 7: Visualize Circular Transaction Patterns as Circular Graph
def visualize_circular_transactions(circular_transactions):
    # Create a circular graph to visualize the circular transaction patterns
    circular_graph = nx.DiGraph()
    for cycle in circular_transactions:
        for i in range(len(cycle)):
            circular_graph.add_edge(cycle[i], cycle[(i + 1) % len(cycle)])

    pos = nx.circular_layout(circular_graph)

    # Create edge traces
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    # Add edges to the edge trace
    for edge in circular_graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace["x"] += tuple([x0, x1, None])
        edge_trace["y"] += tuple([y0, y1, None])

    # Create node traces
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers+text",
        hoverinfo="text",
        marker=dict(
            showscale=False,
            size=10,
            colorbar=dict(
                thickness=15,
                title="Node Connections",
                xanchor="left",
                titleside="right",
            ),
        ),
    )

    # Add nodes to the node trace
    for node in circular_graph.nodes():
        x, y = pos[node]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])

    # Create hover text for nodes
    for node, adjacencies in enumerate(circular_graph.adjacency()):
        node_info = f"{adjacencies[0]}"
        node_info += f"<br>To: {', '.join(adjacencies[1].keys())}"
        node_trace["text"] += tuple([node_info])

    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace])

    # Set layout properties for the plot
    fig.update_layout(
        showlegend=False,
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
    )

    # Show the figure
    return fig

def generate_summary(text):

    # Tokenize the text
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)

    # Create a frequency table to keep the score of each word
    freq_table = dict()
    for word in words:
        word = word.lower()
        if word in stop_words:
            continue
        if word in freq_table:
            freq_table[word] += 1
        else:
            freq_table[word] = 1

    # Calculate the score of each sentence
    sentences = sent_tokenize(text)
    sentence_value = dict()
    for sentence in sentences:
        for word, freq in freq_table.items():
            if word in sentence.lower():
                if sentence in sentence_value:
                    sentence_value[sentence] += freq
                else:
                    sentence_value[sentence] = freq

    # Calculate the average score for the sentences
    sum_values = 0
    for sentence in sentence_value:
        sum_values += sentence_value[sentence]

    # Getting the average value
    average = int(sum_values / len(sentence_value))

    # Storing sentences into our summary.
    summary = ''
    for sentence in sentences:
        if (sentence in sentence_value) and (sentence_value[sentence] > (1.2 * average)):
            summary += " " + sentence
    print("Summary:", summary)

    return summary

# Additional Step 5: Generate Explanation of the Analysis
def generate_explanation(text):


    # Use Spacy to parse the text and extract keywords
    doc = nlp(text)
    keywords = [token.text for token in doc if not token.is_stop and token.pos_ in ['NOUN', 'VERB', 'ADJ']]

    # Create a simple explanation based on the detected keywords
    explanation = "EXPLANATION:" \
                  "" \
                  "The analysis detected outliers in the financial data and identified suspicious transaction patterns. " \
                  "It used various outlier detection models such as Isolation Forest, One-Class SVM, and Local Outlier Factor. " \
                  "The network analysis was performed to detect fraud and circular transaction patterns. " \
                  "Additionally, the analysis identified frequent transactions between parties."

    # Add detected keywords to the explanation
    if keywords:
        explanation += f" The key aspects of the analysis were related to {', '.join(keywords)}."
    print("Explanation:", explanation)



    return explanation



# Load and preprocess the data
df = pd.read_csv("retrieved/retrieved_transactions.csv")
mean = df["Amount"].mean()
std = df["Amount"].std()
df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

# Functions for fraud detection
def detect_Amount_fraud(row, mean, std):
    if abs(row["Amount"] - mean) > 3 * std:
        return True
    else:
        return False

def detect_time_fraud(row):
    hour = int(row["time"].split(":")[0])
    if hour < 6:
        return True
    else:
        return False

def detect_cash_fraud(row):
    if row["type"] == "cash withdrawal" and row["Amount"] > 10000:
        return True
    else:
        return False

def detect_pattern_fraud(row, df):
    account = row["account"]
    prev_transactions = df[df["account"] == account].sort_values(by="date")

    if len(prev_transactions) > 0:
        prev_transaction = prev_transactions.iloc[-1]
        Amount_diff = abs(row["Amount"] - prev_transaction["Amount"])
        date_diff = (row["date"] - prev_transaction["date"]).days

        if Amount_diff > (0.5 * prev_transaction["Amount"]) or date_diff > 30:
            return True

    return False

def detect_linkage_fraud(row):
    Source = row["Source"]
    Target = row["Target"]
    if Source.startswith("BANK") and Target.startswith("BANK"):
        return True
    else:
        return False

# Apply fraud detection functions to create columns indicating fraud
df["Amount_fraud"] = df.apply(detect_Amount_fraud, axis=1, args=(mean, std))
df["time_fraud"] = df.apply(detect_time_fraud, axis=1)
df["cash_fraud"] = df.apply(detect_cash_fraud, axis=1)
df["pattern_fraud"] = df.apply(detect_pattern_fraud, axis=1, args=(df,))
df["linkage_fraud"] = df.apply(detect_linkage_fraud, axis=1)

# Calculate fraud score
df["fraud_score"] = df[["Amount_fraud", "time_fraud", "cash_fraud", "pattern_fraud", "linkage_fraud"]].sum(axis=1)
fraud_df = df[df["fraud_score"] > 0]


# Define layout for each fraud visualization page
def create_fraud_page(page_id, title, figure):
    return html.Div(id=page_id, children=[
        html.H1(title),
        dcc.Graph(figure=figure)
    ])
# Layout for the fraud score table page
def create_fraud_score_table_page(id, df):
    table = dash_table.DataTable(
        id=id,
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        filter_action="native",  # Enable filtering
        style_table={'height': '100%', 'overflowY': 'auto'},
    )

    return html.Div([
        table
    ])





if __name__ == "__main__":
    file_path = 'financial_data.csv'

    # Step 1: Load the data
    financial_data = load_data(file_path)

    # Step 2: Scale the data (if required)
    financial_data_scaled = scale_data(financial_data)



    # Step 5: Perform network analysis for fraud detection and circular transaction pattern detection
    transaction_graph = create_transaction_graph(financial_data)

    # Additional: Detect fund flow patterns
    frequent_transactions = detect_fund_flow_patterns(transaction_graph)
    fund_flow_fig = visualize_fund_flow_detection_results(frequent_transactions)

    # Additional: Detect money laundering activities
    circular_transactions, transactions_with_multiple_intermediaries = detect_money_laundering(transaction_graph)


    # Additional: Visualize Fund Flow Detection Results
    visualize_fund_flow_detection_results(frequent_transactions)

    print("Circular Transactions:")
    print(circular_transactions)
    print("Transactions With Multiple Intermediaries:")
    print(transactions_with_multiple_intermediaries)
    print("Frequent Transactions:")
    print(frequent_transactions)



    # Generate a summary of the analysis
    analysis_text = "SUMMARY:" \
                    "The analysis detected that the network analysis identified {} circular transactions and {} transactions with multiple intermediaries. The most frequent transactions were between {}." \
                    "" \
                    "" \
                    .format(len(circular_transactions), len(transactions_with_multiple_intermediaries), len(frequent_transactions))
    summary = generate_summary(analysis_text)

    # Generate an explanation of the analysis
    explanation_prompt = "The analysis detected outliers in the financial data and identified suspicious transaction patterns. Can you explain this in simpler terms?"
    explanation = generate_explanation(explanation_prompt)


    # Create a Dash app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)




    # Create a link to download the HTML file
    download_link = html.A(
        id="download-link",
        children=[
            dbc.Button("Download HTML", color="primary", className="mr-1"),
        ],
        href="",  # The href attribute will be updated in the callback
        download="dash_app.html"
    )

    # Create a link to download the screenshot image
    download_image_link = html.A(
        id="download-image-link",
        children=[
            dbc.Button("Download Screenshot", color="primary", className="mr-1"),
        ],
        href="",  # The href attribute will be updated in the callback
        download="webpage_screenshot.png"
    )
    # Define the Dash app's layout with a navigation bar and a content div
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink('Fund Flow Detection', href='/page4', id='link-fundflow')),
                dbc.NavItem(dbc.NavLink('Circular Transactions', href='/page5', id='link-circular')),
                dbc.NavItem(dbc.NavLink('Report', href='/page9', id='report')),
                dbc.NavItem(dbc.NavLink('Fraudulent Transactions', href='/transactions', id='link-transactions')),
                dbc.NavItem(dbc.NavLink('Fraud Score Table', href='/fraud-score-table', id='link-fraud-score-table')),
            ],
            brand='',
            brand_href='/',
            color='primary',
            dark=True,
            className='menu',
            style ={'maxHeight': '700px', 'width': '100%', 'overflow': 'auto'}  # Adjust the height of the navigation bar
        ),
        html.Div(id='page-content', style={'height': '84vh', 'width': '100%', 'overflow': 'auto'}),
        download_link,
        html.Button("Download as Image", id="download-image-button", n_clicks=0, className="btn btn-primary"),
        dcc.Download(id="download-image"),
    ])


    # Callback to handle the image download
    @app.callback(Output("download-image", "data"), [Input("download-image-button", "n_clicks")])
    def download_image(n_clicks):
        if n_clicks:
            try:
                # Take a screenshot of the entire screen
                screenshot = pyautogui.screenshot()

                # Convert the screenshot image to bytes
                with io.BytesIO() as img_buffer:
                    screenshot.save(img_buffer, format="PNG")
                    image_data = img_buffer.getvalue()

                return dcc.send_bytes(image_data, filename="screenshot.png")
            except Exception as e:
                print("Error taking screenshot:", str(e))
        return None


    # Callback to handle the download link
    @app.callback(
        Output("download-link", "href"),
        Input("download-link", "n_clicks"),
        prevent_initial_call=True
    )
    @app.callback(
        Output('fraud-score-table-page', 'data'),
        Input('transaction-id-filter', 'value')
    )
    def update_fraud_table(filter_transaction_id):
        if filter_transaction_id is None:
            return fraud_df.to_dict('records')
        else:
            filtered_data = fraud_df[fraud_df['Transaction_ID'].astype(str) == filter_transaction_id]
            return filtered_data.to_dict('records')



    # Callback to handle navigation between pages based on navbar selection
    @app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
    def display_page(pathname):
        page_content_style = {'height': '80vh', 'width': '100%', 'overflow': 'auto'}  # Adjust as needed

        if pathname == '/page2':
            return

        elif pathname == '/page4':
            return dcc.Graph(figure=fund_flow_fig, style=page_content_style)

        elif pathname == '/page5':
            circular_transactions_figure = visualize_circular_transactions(circular_transactions)
            return dcc.Graph(figure=circular_transactions_figure, style=page_content_style)

        elif pathname == '/page9':
            analysis_text = "SUMMARY: The analysis detected that the network analysis identified {} circular transactions and {} transactions with multiple intermediaries. The most frequent transactions were between {}.".format(

                len(circular_transactions), len(transactions_with_multiple_intermediaries), len(frequent_transactions)
            )

            summary_html = generate_summary(analysis_text)
            explanation_html = generate_explanation(explanation_prompt)

            summary_section = html.Div([
                html.H2("Summary"),
                html.Div(dcc.Markdown(summary_html))
            ], className='summary-section')

            explanation_section = html.Div([
                html.H2("Explanation"),
                html.Div(dcc.Markdown(explanation_html))
            ], className='explanation-section')

            report_section = html.Div([
                summary_section,
                explanation_section
            ], className='report')

            return report_section



        elif pathname == '/distribution':
            fraud_counts = [
                df["Amount_fraud"].sum(),
                df["time_fraud"].sum(),
                df["cash_fraud"].sum(),
                df["pattern_fraud"].sum(),
                df["linkage_fraud"].sum()
            ]
            fraud_labels = ["Amount Fraud", "Time Fraud", "Cash Fraud", "Pattern Fraud", "Linkage Fraud"]
            return dcc.Graph(figure=go.Figure(data=[go.Pie(labels=fraud_labels, values=fraud_counts, hole=0.3)]),
                             style=page_content_style)

        elif pathname == '/transactions':
            return dcc.Graph(figure=px.scatter(fraud_df, x="Amount", y="time", color="fraud_score", size="fraud_score",text="Transaction_ID"),
                             style=page_content_style)


        elif pathname == '/fraud-score-table':

            # Call the function to create the fraud score table page

            fraud_score_table_page = create_fraud_score_table_page('fraud-score-table-page', fraud_df)

            # Apply the style directly to the page content

            fraud_score_table_page = html.Div(

                [fraud_score_table_page],

                style=page_content_style  # Apply the desired style here

            )

            return fraud_score_table_page

        else:
            return dcc.Graph(figure=px.scatter(fraud_df, x="Amount", y="time", color="fraud_score", size="fraud_score"),
                             style=page_content_style)



    app.run_server(debug=True, port=8050, use_reloader=True)  # Run the Dash app on port 8050 without reloader
