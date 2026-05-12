import os
import re
from collections import Counter
import pandas as pd
from flask import Flask, render_template, request, flash, url_for, redirect
from get_comments import *
from preprocess import *
from get_amazon import get_amazon_reviews  # Moved to the top!
import json

app = Flask(__name__)
# Needed for `flash()`; required even on error paths.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMENT_CSV_PATH = os.path.join(BASE_DIR, "comment.csv")

# ==========================================
# UPDATED, FORGIVING VALIDATION CHECKS
# ==========================================
def is_valid_youtube_link(link):
    # If the input is completely empty
    if not link:
        return False
        
    # .strip() removes any accidental invisible spaces from copy-pasting
    link = link.strip() 
    
    # Simple, highly forgiving check for any YouTube or Shorts link
    return "youtube.com" in link or "youtu.be" in link

def is_valid_amazon_link(link):
    if not link:
        return False
    link = link.strip()
    return "amazon." in link and ("/dp/" in link or "/product/" in link)

def extract_top_themes(text_series, num_themes=5):
    """Helper function to extract common words, ignoring basic stop words."""
    stopwords = {'the', 'is', 'in', 'and', 'to', 'a', 'of', 'for', 'it', 'this', 'that', 'on', 'with', 'as', 'i', 'my', 'was', 'but', 'are', 'not'}
    words = []
    # Drop empty comments
    for text in text_series.dropna():
        # Keep only words with 4 or more letters to find meaningful themes
        clean_words = re.findall(r'\b[a-zA-Z]{4,}\b', str(text).lower())
        words.extend([w for w in clean_words if w not in stopwords])
    
    # Return the most common words
    return [word for word, count in Counter(words).most_common(num_themes)]

@app.route('/', methods=['GET'])
def hello_world():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def sany():
    link = request.form.get('link')
    option_type = request.form.get('option') 
    
    # ==========================================
    # 1. YOUTUBE LOGIC
    # ==========================================
    if option_type == 'yt':
        print(f"1. Route triggered! The exact link received is: '{link}'")
        
        if not is_valid_youtube_link(link):
            print("ERROR: Link validation failed.")
            flash('Entered url was not valid. Please enter a valid YouTube link.')
            return render_template('index.html')
        
        print("2. Link valid. Fetching comments from YouTube API...")
        video_comments(link)
        
        print("3. Comments fetched. Running ML Preprocessing...")
        process_link()
        
        print("4. ML completed. Crunching pandas data...")
        df = pd.read_csv(COMMENT_CSV_PATH)
        
        p_comm = len(df[df['sentiment'] == 1])
        n_comm = len(df[df['sentiment'] == 0])
        
        pos_comments_list = df[df['sentiment'] == 1]['text'].head(3).tolist()
        neg_comments_list = df[df['sentiment'] == 0]['text'].head(3).tolist()
        
        pos_themes = extract_top_themes(df[df['sentiment'] == 1]['text'])
        neg_themes = extract_top_themes(df[df['sentiment'] == 0]['text'])
        
        data = {
            'Positive comments': p_comm,
            'Negative comments': n_comm,
            'Top Positive': pos_comments_list,
            'Top Negative': neg_comments_list,
            'Positive Themes': pos_themes,
            'Negative Themes': neg_themes
        }
        print("5. Rendering output template...")
        return render_template('output.html', data=data)
        
    # ==========================================
    # 2. AMAZON LOGIC
    # ==========================================
    elif option_type == 'amazon':
        if not is_valid_amazon_link(link):
            flash('Entered url was not valid. Please enter an Amazon product link.')
            return render_template('index.html')
            
        print("Fetching Amazon reviews...")
        get_amazon_reviews(link)
        print("Running ML Preprocessing on Amazon data...")
        process_link() # Reuses the exact same ML model!
        
        df = pd.read_csv(COMMENT_CSV_PATH)
        
        p_comm = len(df[df['sentiment'] == 1])
        n_comm = len(df[df['sentiment'] == 0])
        
        pos_comments_list = df[df['sentiment'] == 1]['text'].head(3).tolist()
        neg_comments_list = df[df['sentiment'] == 0]['text'].head(3).tolist()
        
        pos_themes = extract_top_themes(df[df['sentiment'] == 1]['text'])
        neg_themes = extract_top_themes(df[df['sentiment'] == 0]['text'])
        
        data = {
            'Positive comments': p_comm,
            'Negative comments': n_comm,
            'Top Positive': pos_comments_list,
            'Top Negative': neg_comments_list,
            'Positive Themes': pos_themes,
            'Negative Themes': neg_themes
        }
        return render_template('output.html', data=data)
        
    # ==========================================
    # 3. DIRECT TEXT LOGIC
    # ==========================================
    else:
        pred = p_text(link)
        try:
            prob = float(pred[0][0])
        except Exception:
            prob = float(pred)

        result = "Positive" if prob > 0.5 else "Negative"
        return render_template('sen_out.html', sentence=link, result=result)

if __name__ == "__main__":
    app.run(port=3000, debug=True)