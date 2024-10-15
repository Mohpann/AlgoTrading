'''
NEWS GETTER

Get the top 5 headlines for a specific company

For example get 5 headlines for NVDA
Use the Dow Jones API:
https://developer.dowjones.com/site/docs/newswires_apis/dow_jones_top_stories_api/index.gsp#overview-1

Output should be a container or strings (dictionary or array, whichever)
This output will later be fed to the sentiment analysis program

TO DO: Implement basic functionality for getting the top 5 headlines about DJT (Trump Media)
- Hint use requests library to send GET request to API endpoint url
'''
#before carrying out work, make sure to -> pip install requests python-dotenv
#its taking too long to create a dow jones developers account + security reasons so also make sure to replace DOW_JONES_API_KEY with actual api key

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_top_headlines(company_symbol, num_headlines=5):
    # Dow Jones API endpoint
    url = "https://api.dowjones.com/v1/stories/top"

    # API key should be stored in an environment variable for security
    api_key = os.getenv("DOW_JONES_API_KEY") #<-insert real api key here in DOW_JONES_API_KEY

    # Parameters for the API request
    params = {
        "query": company_symbol,
        "limit": num_headlines
    }

    # Headers for the API request
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # Send GET request to the API
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the JSON response
        data = response.json()

        # Extract headlines
        headlines = [story['headline'] for story in data['stories']]

        return headlines

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
if __name__ == "__main__":
    company_symbol = "DJT"  # Trump Media symbol, could also consider creating input func so that its more flexible
    headlines = get_top_headlines(company_symbol)
    
    print(f"Top 5 headlines for {company_symbol}:")
    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline}")
