from flask import Flask, render_template, jsonify
import requests
from collections import Counter

app = Flask(__name__)

# Fetch the past results as before
def fetch_past_results():
    url = "https://euromillions.api.pedromealha.dev/draws"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = []
        for draw in data:
            date = draw.get('date')
            main_numbers = draw.get('numbers', [])
            stars = draw.get('stars', [])
            results.append((date, main_numbers, stars))
        return results
    else:
        print("Failed to fetch data:", response.status_code)
        return []

def get_highest_lowest_probability_numbers(previous_results):
    all_numbers = [number for result in previous_results for number in result[1]]
    all_stars = [star for result in previous_results for star in result[2]]

    number_counts = Counter(all_numbers)
    star_counts = Counter(all_stars)

    most_common_numbers = [num for num, _ in number_counts.most_common(5)]
    least_common_numbers = [num for num, _ in number_counts.most_common()[:-6:-1]]
    most_common_stars = [star for star, _ in star_counts.most_common(2)]
    least_common_stars = [star for star, _ in star_counts.most_common()[:-3:-1]]

    return most_common_numbers, least_common_numbers, most_common_stars, least_common_stars

def calculate_percentage(counts, total_draws):
    return {num: (count / total_draws) * 100 for num, count in counts.items()}

@app.route('/')
def index():
    previous_results = fetch_past_results()

    if not previous_results:
        return "No results fetched. Please check the API.", 500

    most_common_numbers, least_common_numbers, most_common_stars, least_common_stars = get_highest_lowest_probability_numbers(previous_results)

    number_counts = Counter([number for result in previous_results for number in result[1]])
    star_counts = Counter([star for result in previous_results for star in result[2]])

    total_draws = len(previous_results)
    number_percentages = calculate_percentage(number_counts, total_draws)
    star_percentages = calculate_percentage(star_counts, total_draws)

    return render_template('index.html', 
                           most_common_numbers=most_common_numbers, 
                           least_common_numbers=least_common_numbers,
                           most_common_stars=most_common_stars, 
                           least_common_stars=least_common_stars,
                           number_percentages=number_percentages,
                           star_percentages=star_percentages)

# Define an API endpoint if you want to return JSON
@app.route('/api/results')
def api_results():
    previous_results = fetch_past_results()

    if not previous_results:
        return jsonify({"error": "No results fetched"}), 500

    most_common_numbers, least_common_numbers, most_common_stars, least_common_stars = get_highest_lowest_probability_numbers(previous_results)

    number_counts = Counter([number for result in previous_results for number in result[1]])
    star_counts = Counter([star for result in previous_results for star in result[2]])

    total_draws = len(previous_results)
    number_percentages = calculate_percentage(number_counts, total_draws)
    star_percentages = calculate_percentage(star_counts, total_draws)

    return jsonify({
        "most_common_numbers": most_common_numbers,
        "least_common_numbers": least_common_numbers,
        "most_common_stars": most_common_stars,
        "least_common_stars": least_common_stars,
        "number_percentages": number_percentages,
        "star_percentages": star_percentages
    })

if __name__ == "__main__":
    app.run(debug=True)
