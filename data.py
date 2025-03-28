import requests
import re
from datetime import datetime, timezone
import csv
import os
import time
import numpy as np
import threading
import logging
import pytz
from pysolar.solar import get_altitude
from rtlsdr import RtlSdr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Define the longitude and latitude values
longitudes = list(range(-178, 179, 4))
latitudes = list(range(89, -90, -2))

# Define the city coordinates
cities = {
    "Kabul": (34.5553, 69.2075),
    "Tirana": (41.3275, 19.8187),
    "Algiers": (36.7372, 3.0869),
    "Andorra la Vella": (42.5078, 1.5211),
    "Luanda": (-8.8383, 13.2344),
    "Buenos Aires": (-34.6037, -58.3816),
    "Yerevan": (40.1792, 44.4991),
    "Canberra": (-35.2809, 149.1300),
    "Vienna": (48.2082, 16.3738),
    "Baku": (40.4093, 49.8671),
    "Nassau": (25.0343, -77.3963),
    "Manama": (26.2235, 50.5876),
    "Dhaka": (23.8103, 90.4125),
    "Bridgetown": (13.1132, -59.5988),
    "Minsk": (53.9045, 27.5615),
    "Brussels": (50.8503, 4.3517),
    "Belmopan": (17.2510, -88.7590),
    "Porto-Novo": (6.4969, 2.6289),
    "Thimphu": (27.4712, 89.6339),
    "La Paz": (-16.5000, -68.1500),
    "Sarajevo": (43.8563, 18.4131),
    "Gaborone": (-24.6282, 25.9231),
    "Brasília": (-15.8267, -47.9218),
    "Sofia": (42.6977, 23.3219),
    "Ouagadougou": (12.3714, -1.5197),
    "Gitega": (-3.4271, 29.9246),
    "Praia": (14.9331, -23.5133),
    "Phnom Penh": (11.5564, 104.9282),
    "Yaoundé": (3.8480, 11.5021),
    "Ottawa": (45.4215, -75.6972),
    "Beijing": (39.9042, 116.4074),
    "Bogotá": (4.7110, -74.0721),
    "Moroni": (-11.7172, 43.2473),
    "Kinshasa": (-4.4419, 15.2663),
    "Brazzaville": (-4.2634, 15.2429),
    "San José": (9.9281, -84.0907),
    "Zagreb": (45.8150, 15.9819),
    "Havana": (23.1136, -82.3666),
    "Nicosia": (35.1856, 33.3823),
    "Prague": (50.0755, 14.4378),
    "Copenhagen": (55.6761, 12.5683),
    "Djibouti": (11.5721, 43.1456),
    "Roseau": (15.3092, -61.3790),
    "Santo Domingo": (18.4861, -69.9312),
    "Quito": (-0.1807, -78.4678),
    "Cairo": (30.0444, 31.2357),
    "San Salvador": (13.6929, -89.2182),
    "Malabo": (3.7500, 8.7833),
    "Asmara": (15.3229, 38.9251),
    "Tallinn": (59.4370, 24.7535),
    "Addis Ababa": (9.03, 38.74),
    "Suva": (-18.1416, 178.4419),
    "Helsinki": (60.1695, 24.9354),
    "Paris": (48.8566, 2.3522),
    "Libreville": (0.4162, 9.4673),
    "Banjul": (13.4549, -16.5790),
    "Tbilisi": (41.7151, 44.8271),
    "Berlin": (52.5200, 13.4050),
    "Accra": (5.6037, -0.1870),
    "Athens": (37.9838, 23.7275),
    "Guatemala City": (14.6349, -90.5069),
    "Conakry": (9.6412, -13.5784),
    "Bissau": (11.8817, -15.6170),
    "Georgetown": (6.8013, -58.1551),
    "Port-au-Prince": (18.5944, -72.3074),
    "Tegucigalpa": (14.0723, -87.1921),
    "Budapest": (47.4979, 19.0402),
    "Reykjavik": (64.1466, -21.9426),
    "New Delhi": (28.6139, 77.2090),
    "Jakarta": (-6.2088, 106.8456),
    "Tehran": (35.6892, 51.3890),
    "Baghdad": (33.3152, 44.3661),
    "Dublin": (53.3498, -6.2603),
    "Jerusalem": (31.7683, 35.2137),
    "Rome": (41.9028, 12.4964),
    "Tokyo": (35.6895, 139.6917),
    "Amman": (31.9454, 35.9284),
    "Nur-Sultan": (51.1694, 71.4491),
    "Nairobi": (-1.2864, 36.8172),
    "Tarawa": (1.4518, 173.0354),
    "Pristina": (42.6629, 21.1655),
    "Kuwait City": (29.3759, 47.9774),
    "Bishkek": (42.8746, 74.5698),
    "Vientiane": (17.9757, 102.6309),
    "Riga": (56.9496, 24.1052),
    "Beirut": (33.8938, 35.5018),
    "Maseru": (-29.3151, 27.4869),
    "Monrovia": (6.3156, -10.8074),
    "Tripoli": (32.8872, 13.1913),
    "Vilnius": (54.6872, 25.2797),
    "Luxembourg": (49.6117, 6.1319),
    "Antananarivo": (-18.8792, 47.5079),
    "Lilongwe": (-13.9626, 33.7741),
    "Kuala Lumpur": (3.1390, 101.6869),
    "Male": (4.1755, 73.5093),
    "Bamako": (12.6392, -8.0029),
    "Valletta": (35.8997, 14.5147),
    "Majuro": (7.1164, 171.1850),
    "Nouakchott": (18.0735, -15.9582),
    "Port Louis": (-20.1609, 57.5012),
    "Mexico City": (19.4326, -99.1332),
    "Palikir": (6.9248, 158.1610),
    "Chisinau": (47.0105, 28.8638),
    "Monaco": (43.7384, 7.4246),
    "Ulaanbaatar": (47.8864, 106.9057),
    "Podgorica": (42.4413, 19.2636),
    "Rabat": (34.0209, -6.8416),
    "Casablanca": (33.5731, -7.5898),
    "Tangier": (35.7595, -5.8340),
    "Fes": (34.0331, -4.9998),
    "Marrakech": (31.6295, -7.9811),
    "Laayoune": (27.1253, -13.1625),
    "Maputo": (-25.9653, 32.5892),
    "Naypyidaw": (19.7633, 96.0785),
    "Windhoek": (-22.5609, 17.0658),
    "Yaren": (-0.5467, 166.9211),
    "Kathmandu": (27.7172, 85.3240),
    "Amsterdam": (52.3676, 4.9041),
    "Wellington": (-41.2865, 174.7762),
    "Managua": (12.1150, -86.2362),
    "Niamey": (13.5116, 2.1254),
    "Abuja": (9.0765, 7.3986),
    "Pyongyang": (39.0392, 125.7625),
    "Skopje": (41.9973, 21.4280),
    "Oslo": (59.9139, 10.7522),
    "Muscat": (23.5880, 58.3829),
    "Islamabad": (33.6844, 73.0479),
    "Ngerulmud": (7.5005, 134.6243),
    "Panama City": (8.9824, -79.5199),
    "Port Moresby": (-9.4438, 147.1803),
    "Asunción": (-25.2637, -57.5759),
    "Lima": (-12.0464, -77.0428),
    "Manila": (14.5995, 120.9842),
    "Warsaw": (52.2297, 21.0122),
    "Lisbon": (38.7169, -9.1399),
    "Doha": (25.2760, 51.2280),
    "Bucharest": (44.4268, 26.1025),
    "Moscow": (55.7558, 37.6173),
    "Kigali": (-1.9706, 30.1044),
    "Basseterre": (17.3026, -62.7177),
    "Castries": (13.9094, -60.9789),
    "Kingstown": (13.1600, -61.2248),
    "Apia": (-13.8333, -171.7667),
    "San Marino": (43.9333, 12.4500),
    "São Tomé": (0.3365, 6.7273),
    "Riyadh": (24.7136, 46.6753),
    "Dakar": (14.6928, -17.4467),
    "Belgrade": (44.7866, 20.4489),
    "Victoria": (-4.6167, 55.4500),
    "Freetown": (8.4844, -13.2344),
    "Singapore": (1.3521, 103.8198),
    "Bratislava": (48.1486, 17.1077),
    "Ljubljana": (46.0569, 14.5058),
    "Honiara": (-9.4286, 159.9492),
    "Mogadishu": (2.0469, 45.3182),
    "Pretoria": (-25.7479, 28.2293),
    "Seoul": (37.5665, 126.9780),
    "Juba": (4.8594, 31.5713),
    "Madrid": (40.4168, -3.7038),
    "Colombo": (6.9271, 79.8612),
    "Khartoum": (15.5007, 32.5599),
    "Paramaribo": (5.8520, -55.2038),
    "Stockholm": (59.3293, 18.0686),
    "Bern": (46.9481, 7.4474),
    "Damascus": (33.5138, 36.2765),
    "Taipei": (25.0330, 121.5654),
    "Dushanbe": (38.5598, 68.7870),
    "Dodoma": (-6.1630, 35.7516),
    "Bangkok": (13.7563, 100.5018),
    "Lomé": (6.1725, 1.2314),
    "Nukuʻalofa": (-21.1394, -175.2040),
    "Port of Spain": (10.6549, -61.5019),
    "Tunis": (36.8065, 10.1815),
    "Ankara": (39.9334, 32.8597),
    "Ashgabat": (37.9601, 58.3261),
    "Funafuti": (-8.5211, 179.1942),
    "Kampala": (0.3476, 32.5825),
    "Kyiv": (50.4501, 30.5234),
    "Abu Dhabi": (24.4539, 54.3773),
    "London": (51.5074, -0.1278),
    "Washington, D.C.": (38.9072, -77.0369),
    "Montevideo": (-34.9011, -56.1645),
    "Tashkent": (41.2995, 69.2401),
    "Port Vila": (-17.7333, 168.3273),
    "Vatican City": (41.9029, 12.4534),
    "Caracas": (10.4806, -66.9036),
    "Hanoi": (21.0285, 105.8542),
    "Sana'a": (15.3694, 44.1910),
    "Lusaka": (-15.3875, 28.3228),
    "Harare": (-17.8252, 31.0335),
    "Toronto": (43.6510, -79.3470),
    "Montreal": (45.5017, -73.5673),
    "Vancouver": (49.2827, -123.1207),
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Boston": (42.3601, -71.0589),
    "Miami": (25.7617, -80.1918)
}

def convert_utc_to_local(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M UTC")
    utc_time = utc_time.replace(tzinfo=timezone.utc)
    local_tz = pytz.timezone('America/New_York')  # This covers both EDT and EST
    local_time = utc_time.astimezone(local_tz)
    return local_time.strftime("%Y-%m-%d %H:%M")  # Removed %Z to exclude timezone info


################# XRAY #################


import requests
import json
from datetime import datetime, timedelta

def fetch_xray_data():
    url = 'https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json'
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = json.loads(response.text)
    except requests.RequestException as e:
        logging.error(f"NOAA XRAY - Error fetching X-ray data: {e}")
        return None

    # Filter for primary GOES-16 data and 0.1-0.8nm range
    filtered_data = [entry for entry in data if entry['satellite'] == 16 and entry['energy'] == '0.1-0.8nm']

    # Sort by time_tag
    filtered_data.sort(key=lambda x: x['time_tag'])

    return filtered_data

def log_xray_data(filtered_data):
    filename = 'NOAA_XRAY.csv'

    # Read existing data if file exists
    existing_data = set()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            existing_data = set(row[0] for row in reader)

    new_data = []
    for entry in filtered_data:
        utc_time = datetime.strptime(entry['time_tag'], "%Y-%m-%dT%H:%M:%SZ")
        local_time = convert_utc_to_local(utc_time.strftime("%Y-%m-%d %H:%M UTC"))
        
        if local_time not in existing_data:
            flux = entry['flux']
            classification, normalized_value = classify_xray_flux(flux)
            new_data.append([local_time, classification, normalized_value])

    # Append new data to file
    if new_data:
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not existing_data:  # If file was just created, write header
                writer.writerow(['Timestamp', 'Flare_Class', 'Normalized_Value'])
            writer.writerows(new_data)
        logging.info(f"NOAA XRAY - Added {len(new_data)} new X-ray data entries")
    else:
        logging.info("NOAA XRAY - No new X-ray data to add")

def classify_xray_flux(flux):
    if flux < 1e-7:
        class_letter = 'A'
        class_number = flux * 1e8
    elif flux < 1e-6:
        class_letter = 'B'
        class_number = flux * 1e7
    elif flux < 1e-5:
        class_letter = 'C'
        class_number = flux * 1e6
    elif flux < 1e-4:
        class_letter = 'M'
        class_number = flux * 1e5
    else:
        class_letter = 'X'
        class_number = flux * 1e4

    # Cap at 9.9 for A, B, C, M classes, but not for X class
    if class_letter != 'X':
        class_number = min(class_number, 9.9)

    classification = f"{class_letter}{class_number:.1f}"
    
    # Normalize with C1.0 = 10, keeping maximum precision
    normalized_value = flux * 1e7

    return classification, normalized_value

def run_xray_data_collection(sleep_duration):
    while True:
        xray_data = fetch_xray_data()
        logging.info("NOAA XRAY - NEW XRAY DATA FETCHED")

        if xray_data is not None:
            log_xray_data(xray_data)
            logging.info("NOAA XRAY - XRAY DATA UPDATED")
        time.sleep(sleep_duration)

################# DRAP #################

# Function to fetch DRAP data from NOAA
def fetch_drap_data():
    try:
        url = 'https://services.swpc.noaa.gov/text/drap_global_frequencies.txt'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.RequestException as e:
        logging.error(f"NOAA DRAP - Error fetching DRAP data: {e}")
        return None

# Function to extract timestamp and build the 2D data array from DRAP data
def parse_drap_data(lines):
    # Extract timestamp from the 3rd line
    timestamp_line = lines[2].strip()
    utc_timestamp = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC', timestamp_line).group(0)
    local_timestamp = convert_utc_to_local(utc_timestamp)
    
    # Skip lines until we find the first data line after the dashes line
    data_start_line_pattern = re.compile(r'-{20,}')
    data_start_index = None
    
    for i, line in enumerate(lines):
        if data_start_line_pattern.match(line.strip()):
            data_start_index = i + 1
            break
    
    # Extract data
    data = []
    for line in lines[data_start_index:]:
        if "|" in line:
            latitude, values = line.strip().split('|')
            latitude = int(latitude.strip())
            if latitude in latitudes:
                values = list(map(float, values.split()))
                data.append((latitude, values))
    
    # Ensure all latitudes are covered
    data_dict = {lat: [None]*len(longitudes) for lat in latitudes}
    for lat, values in data:
        data_dict[lat] = values
    
    # Convert to sorted list of tuples
    sorted_data = sorted(data_dict.items(), key=lambda x: x[0], reverse=True)
    
    return local_timestamp, sorted_data


# Function to get DRAP data for a specific city
def fetch_drap_city(city, coords, sorted_data):
    lat_index = min(range(len(latitudes)), key=lambda i: abs(latitudes[i] - coords[0]))
    lon_index = min(range(len(longitudes)), key=lambda i: abs(longitudes[i] - coords[1]))
    drap_value = sorted_data[lat_index][1][lon_index]
    return drap_value

# Function to save DRAP data to CSV
def log_drap_data(city, timestamp, drap_value):
    filename = f"NOAA_DRAP_{city}.csv"
    file_exists = os.path.isfile(filename)
    
    try:
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["Timestamp", "DRAP_Value"])
            writer.writerow([timestamp, drap_value])
    except IOError as e:
        logging.error(f"NOAA DRAP - Error writing to file {filename}: {e}")
    else:
        logging.info(f"NOAA DRAP - Value in {city} at {timestamp} is {drap_value}")

# Function to run the DRAP data fetching loop
def run_drap_data_collection(city, sleep_duration):
    coords = cities[city]
    previous_timestamp = None
    while True:
        lines = fetch_drap_data()
        if lines is None:
            local_time = datetime.now().astimezone(pytz.timezone('America/New_York'))
            timestamp = local_time.strftime("%Y-%m-%d %H:%M")
        else:
            utc_timestamp = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC', lines[2].strip()).group(0)
            local_timestamp = convert_utc_to_local(utc_timestamp)
            if local_timestamp == previous_timestamp:
                logging.info(f"NOAA DRAP - No new DRAP data for {city}. Skipping this cycle.")
                time.sleep(sleep_duration)
                continue
            timestamp, sorted_data = parse_drap_data(lines)
            drap_value = fetch_drap_city(city, coords, sorted_data)
            previous_timestamp = local_timestamp
        
        log_drap_data(city, timestamp, drap_value)
        time.sleep(sleep_duration)


################# SDR #################

# Function to get sun elevation
def get_sun_elevation(lat, lon):
    date = datetime.now(timezone.utc)
    altitude = get_altitude(lat, lon, date)
    return altitude

# Function to log SDR data to CSV with sun elevation
def log_sdr_data(city, frequencies, duration, sample_rate):
    sdr = RtlSdr()
    sdr.sample_rate = sample_rate
    sdr.gain = 'auto'
    
    filename = f"Local_RadioData_{city}.csv"
    file_exists = os.path.isfile(filename)
    
    # Write the header if the file doesn't exist
    if not file_exists:
        header = ["Local_Timestamp", "City", "Sun_Elevation"]
        for frequency in frequencies:
            header.append(f"Signal_Strength_{frequency}")
            header.append(f"SNR_{frequency}")
        with open(filename, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
    
    return sdr, filename

# Function to perform SDR measurement
def perform_sdr_measurement(sdr, frequency, duration, sample_rate):
    try:
        sdr.center_freq = frequency
        samples = sdr.read_samples(duration * sample_rate)
        signal_strength = np.mean(np.abs(samples))
        noise_floor = np.mean(np.abs(samples - np.mean(samples)))
        snr = signal_strength / noise_floor if noise_floor != 0 else float('inf')
        return signal_strength, snr
    except Exception as e:
        logging.error(f"LOCAL RTLSDR - Error in SDR measurement: {e}")
        return None, None

# Function to run the SDR data collection loop
def run_sdr_data_collection(city, frequencies, duration, sample_rate, sleep_duration):
    sdr, filename = log_sdr_data(city, frequencies, duration, sample_rate)
    coords = cities[city]
    try: 
        while True:
            local_time = datetime.now().astimezone(pytz.timezone('America/New_York'))
            start_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
            row = [start_time, city]

            sun_elevation = get_sun_elevation(coords[0], coords[1])
            row.append(sun_elevation)

            for frequency in frequencies:
                signal_strength, snr = perform_sdr_measurement(sdr, frequency, duration, sample_rate)
                if signal_strength is not None and snr is not None:
                    row.append(signal_strength)
                    row.append(snr)
                    logging.info(f"LOCAL RTLSDR - Freq {frequency} in {city} at {start_time}: Signal Strength = {signal_strength} ; SNR = {snr} ; Sun Elevation = {sun_elevation}")
                else:
                    row.append("N/A")
                    row.append("N/A")
                    print(row)
            with open(filename, "a", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

            time.sleep(sleep_duration)  # Sleep for the specified duration
    finally:
        sdr.close()




################# DATA COLLECTION #################

# Function to start the data collection processes
def start_data_collection(city):
    frequencies = [5000000, 10000000, 15000000, 20000000, 25000000]  # in Hz
    duration = 1  # seconds per frequency
    sample_rate = 2.048e6  # Hz
    sleep_duration_xray = 3600  # = 60 minutes
    sleep_duration_drap = 30  # seconds
    sleep_duration_sdr = 1  # seconds

    # Start XRAY data logging
    threading.Thread(target=run_xray_data_collection, args=(sleep_duration_xray,)).start()  # Run every 60 minutes

    # Start DRAP data fetching
    threading.Thread(target=run_drap_data_collection, args=(city, sleep_duration_drap)).start()

    # Start SDR data logging
    threading.Thread(target=run_sdr_data_collection, args=(city, frequencies, duration, sample_rate, sleep_duration_sdr)).start()
    
    
# Run the main function for each city
if __name__ == "__main__":
    start_data_collection("Montreal")

