import json
import requests
import datetime
import sys
import openai
import streamlit as st

# Define API keys for OpenWeatherMap and OpenAI
WEATHER_API_KEY = '27ddf1b27291b0ec63e647d4f9a5dfe6'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'

# Function to get the latitude and longitude of a city
def get_latitude_longitude(city):
    url = 'http://api.openweathermap.org/geo/1.0/direct'
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'limit': 1
    }
    try:
        # Make request to OpenWeatherMap API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception if status code is not 200
        data = response.json()
        return data[0]['lat'], data[0]['lon']
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("Error:", err)
        sys.exit(1)

# Function to get the weather data of a location using the latitude and longitude of the city generated from get_latitude_longitude function
def get_weather(lat, lon):
    url = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {
        'lat': lat,
        'lon': lon,
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    try:
        # Make request to OpenWeatherMap API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception if status code is not 200
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("Error:", err)
        sys.exit(1)

# Function to generate a creative description of the weather using GPT-3.5-turbo
def generate_description(forecast_data):
    openai.api_key = OPENAI_API_KEY

    # Create a string that describes the weather data
    weather_data_string = f"The weather for the time is as follows: {forecast_data}"

    # Use the GPT-3.5-turbo model to generate a description
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are supposed to generate a cool description of this weather forecast data:"},
                {"role": "user", "content": forecast_data}
            ]
        )
    # handling all the exceptions
    except (openai.error.APIError,
            openai.error.Timeout,
            openai.error.RateLimitError,
            openai.error.APIConnectionError,
            openai.error.InvalidRequestError,
            openai.error.AuthenticationError,
            openai.error.ServiceUnavailableError) as err:
        print(f"Error occurred while generating description: {err}")
        return None

    return response

# Main function to fetch and print weather data for a given city
def main(city):
    # Get latitude and longitude for the city
    lat, lon = get_latitude_longitude(city)

    # Get weather data for the city
    data = get_weather(lat, lon)

    data_to_write = []

    for item in data['list']:
        date = datetime.datetime.fromtimestamp(item['dt'])
        date = date + datetime.timedelta(hours=5, minutes=30)
        if date.hour == 8 or date.hour == 17:
            final_date = date.strftime('%A, %B %d, %Y %I:%M:%S')

            forecast_data = f"Temperature: {item['main']['temp']}, Feels Like: {item['main']['feels_like']}, Pressure: {item['main']['pressure']}, Humidity: {item['main']['humidity']}, Weather: {item['weather'][0]['main']}, Description: {item['weather'][0]['description']}"

            # create a forecast_data_dictionary:
            forecast_data_dictionary = {'Temperature': item['main']['temp'], 'Feels Like': item['main']['feels_like'],
                                        'Pressure': item['main']['pressure'], 'Humidity': item['main']['humidity'],
                                        'Weather': item['weather'][0]['main'],
                                        'Description': item['weather'][0]['description']}
            gpt_description = generate_description(forecast_data)
            if gpt_description is not None:
                gpt_response = gpt_description['choices'][0]['message']['content']
            else:
                gpt_response = "I am not able to generate a description for this weather forecast data."

            st.write(f"{final_date}:")
            st.write(forecast_data)
            st.write(f"gpt-3.5-turbo says: {gpt_response}\n")

            # extract day, date, and time
            day = date.strftime('%A')
            date_only = date.strftime('%B %d, %Y')
            time = date.strftime('%I:%M:%S')

            # add the data to the list
            data_to_write.append(
                {'date': date_only, 'day': day, 'time': time,
                 'forecast_data': forecast_data_dictionary,
                 'gpt-3.5-turbo says': gpt_response}
            )

    # write the entire list to the JSON file
    with open('data.json', 'w') as f:
        json.dump(data_to_write, f, indent=4)

# Run the Streamlit Web Application
if __name__ == "__main__":
    st.title('Weather Whisperer')
    # text box to input the simulated command
    city = st.text_input("Command Line Simulator (usage: python main.py <city name>)")
    if city:
        # print the data in the web application
        if len(city.split(' ')) < 3:
            st.write("usage: python main.py <city name>")
        elif city.split(' ')[0] != 'python' or city.split(' ')[1] != 'main.py':
            st.write("usage: python main.py <city name>")
        main(city.split(' ')[2].strip())
