import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

user_agent = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

# First
first_numbers = []
first_names = []
first_release_dates = []
first_meta_scores = []
first_recommendations = []

first_total_pages = 200
for index, page in enumerate(range(0, first_total_pages), 1):
    url = f'https://www.metacritic.com/browse/game/all/all/all-time/popular/?releaseYearMin=1910&releaseYearMax=2023&page={page}'
    response = requests.get(url, headers=user_agent)
    soup = BeautifulSoup(response.text, 'lxml')

    # name and number
    h3_tags = soup.find_all('h3', class_='c-finderProductCard_titleHeading')
    for tag in h3_tags:
        span_tags = tag.find_all('span')
        if len(span_tags) > 1:
            number = span_tags[0].get_text().replace('.', '')
            name = span_tags[1].get_text().replace(',', '')
            first_numbers.append(number)
            first_names.append(name)

    # release_date
    release_divs = soup.find_all('div', class_='c-finderProductCard_meta')
    for div in release_divs:
        span_tags = div.find_all('span', class_='u-text-uppercase')
        release_date = ''
        for span in span_tags:
            if 'Metascore' not in span.get_text(strip=True):
                release_date = span.get_text(strip=True)
                date_object = datetime.strptime(release_date, '%b %d, %Y')
                formatted_date = date_object.strftime('%Y-%m-%d')
                first_release_dates.append(formatted_date)

    # meta_score and recommendation
    metascore_elements = soup.find_all('div', class_='c-siteReviewScore')
    for element in metascore_elements:
        span = element.find('span')
        if span is not None:
            first_meta_scores.append(span.text.strip())
        else:
            first_meta_scores.append('')

        # Recommendation
        if 'c-siteReviewScore_green' in element['class']:
            first_recommendations.append('A score')
        elif 'c-siteReviewScore_yellow' in element['class']:
            first_recommendations.append('B score')
        elif 'c-siteReviewScore_red' in element['class']:
            first_recommendations.append('C score')

with open('games_data_first.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Number", "Name", "Release Date",
                    "Meta Score", "Recommendation"])
    for data in zip(first_numbers, first_names, first_release_dates, first_meta_scores, first_recommendations):
        writer.writerow(data)

# Second
second_numbers = []
second_names = []
second_release_dates = []
second_meta_scores = []
second_recommendations = []

second_total_pages = 343

for index, page in enumerate(range(201, 544), 201):
    url = f'https://www.metacritic.com/browse/game/all/all/all-time/popular/?releaseYearMin=1910&releaseYearMax=2023&page={page}'
    response = requests.get(url, headers=user_agent)
    soup = BeautifulSoup(response.text, 'lxml')

    # name and number
    h3_tags = soup.find_all('h3', class_='c-finderProductCard_titleHeading')
    for tag in h3_tags:
        span_tags = tag.find_all('span')
        if len(span_tags) > 1:
            number = span_tags[0].get_text().replace('.', '')
            name = span_tags[1].get_text().replace(',', '')
            second_numbers.append(number)
            second_names.append(name)

    # release_date
    release_divs = soup.find_all('div', class_='c-finderProductCard_meta')
    for div in release_divs:
        span_tags = div.find_all('span', class_='u-text-uppercase')
        release_date = ''
        for span in span_tags:
            if 'Metascore' not in span.get_text(strip=True):
                release_date = span.get_text(strip=True)
                date_object = datetime.strptime(release_date, '%b %d, %Y')
                formatted_date = date_object.strftime('%Y-%m-%d')
                second_release_dates.append(formatted_date)

    # meta_score and recommendation
    metascore_elements = soup.find_all('div', class_='c-siteReviewScore')
    for element in metascore_elements:
        span = element.find('span')
        if span is not None:
            second_meta_scores.append(span.text.strip())
        else:
            second_meta_scores.append('')

        # Recommendation
        if 'c-siteReviewScore_green' in element['class']:
            second_recommendations.append('A score')
        elif 'c-siteReviewScore_yellow' in element['class']:
            second_recommendations.append('B score')
        elif 'c-siteReviewScore_red' in element['class']:
            second_recommendations.append('C score')

with open('games_data_second.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Number", "Name", "Release Date",
                    "Meta Score", "Recommendation"])
    for data in zip(second_numbers, second_names, second_release_dates, second_meta_scores, second_recommendations):
        writer.writerow(data)
