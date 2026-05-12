import requests
from bs4 import BeautifulSoup
import csv

def get_amazon_reviews(url):
    # Simulate a real browser to prevent Amazon from blocking the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract review texts based on Amazon's standard review CSS classes
    reviews = soup.find_all('span', {'data-hook': 'review-body'})
    
    comm = []
    for review in reviews:
        text = review.get_text(strip=True)
        if text:
            comm.append([text])
            
    # Write to the exact same CSV format so your existing ML pipeline can read it
    with open('./comment.csv', 'w', encoding="utf-8", newline='') as filee:
        writer = csv.writer(filee)
        writer.writerow(["Comments"])
        writer.writerows(comm)