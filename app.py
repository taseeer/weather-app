from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

API_KEY = "895f5d80cc757efdd9a27323f7b11e7d"  # Replace with your actual OpenWeatherMap API key

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    error = None
    if request.method == "POST":
        city = request.form["city"]
        if city:
            # Current weather URL
            current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            # 5-day forecast URL
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
            
            current_response = requests.get(current_url)
            forecast_response = requests.get(forecast_url)
            
            if current_response.status_code == 200 and forecast_response.status_code == 200:
                # Process current weather data
                current_data = current_response.json()
                timezone_offset = current_data["timezone"]
                current_time = datetime.utcnow().timestamp() + timezone_offset
                local_time = datetime.fromtimestamp(current_time)
                hour = local_time.hour
                is_day = 6 <= hour < 18
                
                weather_data = {
                    "city": current_data["name"],
                    "country": current_data["sys"]["country"],
                    "temperature": round(current_data["main"]["temp"]),
                    "feels_like": round(current_data["main"]["feels_like"]),
                    "humidity": current_data["main"]["humidity"],
                    "wind_speed": current_data["wind"]["speed"],
                    "description": current_data["weather"][0]["description"].capitalize(),
                    "icon": current_data["weather"][0]["icon"],
                    "time": local_time.strftime("%I:%M %p"),
                    "is_day": is_day
                }
                
                # Process forecast data
                forecast_data = []
                forecast_json = forecast_response.json()
                timezone_offset = forecast_json["city"]["timezone"]
                
                # Group forecasts by day (8 forecasts per day, 3-hour intervals)
                daily_forecasts = {}
                for item in forecast_json["list"]:
                    dt = datetime.fromtimestamp(item["dt"] + timezone_offset)
                    date_key = dt.date()
                    if date_key not in daily_forecasts:
                        daily_forecasts[date_key] = {
                            "date": dt.strftime("%A, %b %d"),
                            "day_name": dt.strftime("%A"),
                            "temp_min": round(item["main"]["temp_min"]),
                            "temp_max": round(item["main"]["temp_max"]),
                            "icon": item["weather"][0]["icon"],
                            "description": item["weather"][0]["description"].capitalize()
                        }
                    else:
                        if item["main"]["temp_min"] < daily_forecasts[date_key]["temp_min"]:
                            daily_forecasts[date_key]["temp_min"] = round(item["main"]["temp_min"])
                        if item["main"]["temp_max"] > daily_forecasts[date_key]["temp_max"]:
                            daily_forecasts[date_key]["temp_max"] = round(item["main"]["temp_max"])
                
                # Convert to list and take next 5 days (excluding today if you want)
                forecast_data = list(daily_forecasts.values())[:5]
                
            else:
                error = "City not found. Please enter a valid city name."
        else:
            error = "Please enter a city name."
    return render_template("index.html", weather_data=weather_data, forecast_data=forecast_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)