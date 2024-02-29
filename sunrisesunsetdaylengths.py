import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_day_length(lat, lng, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    data = []

    for single_date in date_range:
        formatted_date = single_date.strftime("%Y-%m-%d")
        response = requests.get(
            f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={formatted_date}&formatted=0"
        )
        if response.status_code == 200 and response.json()['status'] == 'OK':
            result = response.json()['results']
            data.append({
                'Date': formatted_date,
                'Sunrise': datetime.fromisoformat(result['sunrise']).strftime('%Y-%m-%d %H:%M:%S'),
                'Sunset': datetime.fromisoformat(result['sunset']).strftime('%Y-%m-%d %H:%M:%S'),
                'Solar Noon': datetime.fromisoformat(result['solar_noon']).strftime('%Y-%m-%d %H:%M:%S'),
                'Day Length': result['day_length']
            })
        else:
            print(f"Failed to fetch data for {formatted_date}")

    return pd.DataFrame(data)

# Your specific location and date range
lat = 18.321056
lng = -65.819722
start_date = '1991-09-01'
end_date = '2010-01-31'

# Fetching the data
day_length_data = fetch_day_length(lat, lng, start_date, end_date)

# Display the first few rows of the table
print(day_length_data.head())

# Optionally, save the data to a CSV file
day_length_data.to_csv('day_length_data_El_Verde_1991-2010.csv', index=False)
