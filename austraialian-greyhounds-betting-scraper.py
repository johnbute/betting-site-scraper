import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd

def visitpage():
    # URL of the main page containing the links
    url = 'https://www.odds.com.au/greyhounds/'  # Replace with the actual URL

    # Headers to mimic a real browser visit
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    # Make a GET request to the main page
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the main page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the links in the table
        links = soup.find_all('a', {'class': ['event-lists__link', 'disable-pointer-events']})

        # Create a list to store the full URLs
        full_urls = []

        # Loop through each link and construct the full URL
        for link in links:
            href = link.get('href')
            if href:
                full_url = f'https://www.odds.com.au{href}'  # Adjust this based on the actual URL structure
                full_urls.append(full_url)
        return full_urls
    else:
        print('Failed to retrieve the main page')
        return []

def visitrace(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    # Set path to chromedriver as per your configuration
    webdriver_service = Service("C:/Users/johnb/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")  # Change this to your path to chromedriver

    # Choose Chrome Browser
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    
    driver.get(url)
    
    try:
        # Wait until the odds-comparison-table is loaded
        
        # Once the element is loaded, parse the page source with BeautifulSoup
        page_soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract each name from the span with class 'competitor-details'
        competitors = page_soup.find_all('span', class_='competitor-details')
        names = []
        for competitor in competitors:
            name_tag = competitor.find('a')
            if name_tag:
                name = name_tag.contents[-2].strip()
                names.append(name)
        odds_data = []
        # Extract the odds from class 'octd-right__odds-value-cell'
        odds_cells = page_soup.find_all('div', class_='octd-right__main-cell')
        for cell in odds_cells:
            odds_value_cell = cell.find('div', class_='octd-right__odds-value-cell')
            if odds_value_cell:
                odds_value = odds_value_cell.get_text(strip=True)
                if odds_value:
                    odds_data.append(float(odds_value))
                else:
                    odds_data.append('N/A')
            else:
                odds_data.append('N/A')
        
        # Check if the number of names matches the number of odds divided by 11
        if len(names) * 11 != len(odds_data):
            raise ValueError("The number of names and odds do not match correctly.")
        
        # Create an empty DataFrame with the specified columns
        columns = ["Name", "TAB", "sportsbet", "bet365", "BetM", "ladbrples", "betfair (back)", "betfair (lay)", "boombet", "TABtouch", "pointsbet", "neds", "URL"]
        df = pd.DataFrame(columns=columns)
        
        # Populate the DataFrame
        for i in range(len(names)):
            row = [names[i]] + odds_data[i*11:(i+1)*11] + [url]
            df.loc[i] = row
        
        return df
        
    except Exception as e:
        print(f'An error occurred: {e}')
        return pd.DataFrame()
    finally:
        driver.quit()

if __name__ == '__main__':
    race_urls = visitpage()
    
    # Initialize an empty DataFrame to store all race data
    all_races_df = pd.DataFrame()
    
    for race_url in race_urls:
        race_df = visitrace(race_url)
        print(race_df)
        all_races_df = pd.concat([all_races_df, race_df], ignore_index=True)
    
    print(all_races_df)
    
    # Optionally, you can save the combined DataFrame to a CSV file
    all_races_df.to_csv('all_race_odds.csv', index=False)
