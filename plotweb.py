import pandas as pd
from datetime import datetime
import time
import threading
import http.server
import socketserver
import os
import requests

# Function to convert timestamp
def convert_timestamp(timestamp_str):
    if isinstance(timestamp_str, str):
        try:
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')
    else:
        return None

# Function to run your code
def process_data():
    # Read the CSV files
    radio_data = pd.read_csv('Local_RadioData_Montreal.csv')
    noaa_xray_data = pd.read_csv('NOAA_XRAY.csv')
    noaa_drap_data = pd.read_csv('NOAA_DRAP_Montreal.csv')

    # Convert timestamps to datetime objects
    radio_data['Timestamp'] = radio_data['Timestamp'].apply(convert_timestamp)
    noaa_xray_data['Timestamp'] = noaa_xray_data['Timestamp'].apply(convert_timestamp)
    noaa_drap_data['Timestamp'] = noaa_drap_data['Timestamp'].apply(convert_timestamp)

    # Drop rows with missing timestamps
    radio_data = radio_data.dropna(subset=['Timestamp'])
    noaa_xray_data = noaa_xray_data.dropna(subset=['Timestamp'])
    noaa_drap_data = noaa_drap_data.dropna(subset=['Timestamp'])

    # Sort dataframes by timestamp
    radio_data = radio_data.sort_values('Timestamp')
    noaa_xray_data = noaa_xray_data.sort_values('Timestamp')
    noaa_drap_data = noaa_drap_data.sort_values('Timestamp')

    # Merge radio data with NOAA X-ray data
    merged_data = pd.merge_asof(radio_data, 
                                noaa_xray_data,
                                on='Timestamp',
                                direction='nearest')

    # Merge the result with NOAA DRAP data
    merged_data = pd.merge_asof(merged_data,
                                noaa_drap_data,
                                on='Timestamp',
                                direction='nearest')

    # Drop rows with any NaNs
    merged_data = merged_data.dropna()

    # Save the merged data to a new CSV file
    merged_data.to_csv('trainingdata.csv', index=False)

    print("Data has been merged and saved to trainingdata.csv")

# Function to start the webserver
def start_webserver():
    PORT = 7777
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        print(f"Visit the plot at: http://{get_ip_address()}:{PORT}/plot.html")
        print(f"Accessible via the internet at: http://{get_public_ip()}:{PORT}/plot.html")
        httpd.serve_forever()

# Function to get the local IP address
def get_ip_address():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "127.0.0.1"
    finally:
        s.close()
    return ip_address

# Function to get the public IP address
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return "Unable to determine public IP"

# Function to schedule the task
def schedule_task(interval_minutes):
    while True:
        process_data()
        time.sleep(interval_minutes * 60)

# Start the webserver in a separate thread
webserver_thread = threading.Thread(target=start_webserver)
webserver_thread.daemon = True
webserver_thread.start()

# Schedule the task to run every 20 minutes
schedule_task(20)
