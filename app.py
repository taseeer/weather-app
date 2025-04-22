from flask import Flask, render_template, request
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

API_KEY = "895f5d80cc757efdd9a27323f7b11e7d"  # Replace with your actual OpenWeatherMap API key

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error = None
    if request.method == "POST":
        city = request.form["city"]
        if city:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                timezone_offset = data["timezone"]
                current_time = datetime.utcnow().timestamp() + timezone_offset
                local_time = datetime.fromtimestamp(current_time)
                hour = local_time.hour
                is_day = 6 <= hour < 18
                weather_data = {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": round(data["main"]["temp"]),
                    "feels_like": round(data["main"]["feels_like"]),
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "description": data["weather"][0]["description"].capitalize(),
                    "icon": data["weather"][0]["icon"],
                    "time": local_time.strftime("%I:%M %p"),
                    "is_day": is_day
                }
            else:
                error = "City not found. Please enter a valid city name."
        else:
            error = "Please enter a city name."
    return render_template("index.html", weather_data=weather_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
