from flask_cors import CORS
import openai
import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = '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'
WEATHER_KEY = '24080b462f6beb96eb6bc6ab69de3a88'

def getWeather(location):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": WEATHER_KEY,
        "units": "metric",
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            temperature = data["main"]["temp"]
            weather_description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]

            return json.dumps({
                "location": location,
                "temperature": temperature,
                "description": weather_description,
                "humidity": humidity,
                "information": data,
                "explain": "explain it like a news forcast",
            })
        else:
            return {"error": f"Failed to fetch weather data for {location}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {e}"}


@app.route("/get_weather", methods=["POST"])
def chat():
    user_message = request.json.get("content", "")
    messages = [{"role": "user", "content": user_message}]

    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    response_message = response["choices"][0]["message"]

    if response_message.get("function_call"):
        available_functions = {
            "get_current_weather": getWeather,
        }

        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(
            location=function_args.get("location")
        )

        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )
        return jsonify({"message": second_response["choices"][0]["message"]["content"]})
    return jsonify({"message": response_message["content"]})

if __name__ == '__main__':
    app.run(debug=True)
