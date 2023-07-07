from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
import json
import os
from requests_html import HTMLSession


class QuotesScraper:
    def __init__(self):
        load_dotenv()
        self.input_url = os.getenv('INPUT_URL')
        self.input_host = os.getenv('PROXY')
        self.output_file = os.getenv('OUTPUT_FILE')
        self.session = HTMLSession()

    def scrape_page(self, url):
        print(url)

        # Send a GET request to the specified URL using the session
        response = self.session.get(url)

        # Extract the JSON data from the response using BeautifulSoup
        return json.loads(
            bs(response.text, 'lxml').find_all('script')[1].text.split('for (var i in data)')[0].split(
                'var data =')[-1].strip().rstrip(';'))

    def scrape_quotes(self):
        url = self.input_url
        base_url = self.input_url[0:26]
        all_quotes = []
        while True:
            # Scrape the quotes from the current page
            all_quotes.extend(self.scrape_page(url))

            # Check if there is a next page
            next_page_element = bs(self.session.get(url).text, 'lxml').find('li', {'class': 'next'})
            if not next_page_element:
                break

            # Get the link of the next page and update the URL
            next_page_link = base_url + next_page_element.find('a').get('href')
            url = next_page_link

        return all_quotes

    def extract_content(self, quotes):
        extracted_quotes = []
        for quote in quotes:
            # Extract the required fields from each quote
            extracted_quote = {
                "text": quote.get('text')[1:-2],
                "by": quote.get('author').get('name'),
                "tags": quote.get('tags')
            }
            extracted_quotes.append(extracted_quote)

        return extracted_quotes

    def write_quotes_to_file(self, quotes):
        extracted_quotes = self.extract_content(quotes)
        with open(self.output_file, mode='w', encoding='utf-8') as f:
            for quote in extracted_quotes:
                # Convert each quote to JSON format and write to the file
                json_data = json.dumps(quote, ensure_ascii=False)
                json_data = json_data.replace('{', '{\n').replace('"by"', '\n"by"').replace('"tags"', '\n"tags"').replace('}', '\n}')
                f.write(json_data)
                f.write('\n')

    def run(self):
        # Scrape the quotes and write them to the file
        quotes = self.scrape_quotes()
        self.write_quotes_to_file(quotes)


if __name__ == "__main__":
    # Create an instance of the QuotesScraper class and run the scraping process
    scraper = QuotesScraper()
    scraper.run()
