from googleapiclient.discovery import build
import pandas as pd
import csv
from pytube import extract
import os

api_key = os.environ.get("YOUTUBE_API_KEY")



number = 0
comm=[]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMENT_CSV_PATH = os.path.join(BASE_DIR, "comment.csv")

def video_comments(url):
  comm = []
  
  video_id = extract.video_id(url)

  comment_count = 0

  youtube = build('youtube', 'v3', developerKey=api_key)

  video_response = youtube.commentThreads().list(
  part = 'snippet,replies',
  videoId = video_id
  ).execute()

  while video_response:
    for item in video_response['items']:
    
      comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
      arr=[comment]
      comm.append(arr)

      comment_count += 1

    if 'nextPageToken' in video_response:
      video_response = youtube.commentThreads().list(
          part = 'snippet,replies',
          videoId = video_id,
          pageToken = video_response['nextPageToken']
        ).execute()
    else:
        break
  with open(COMMENT_CSV_PATH, 'w',encoding="utf-8", newline='') as filee:
    writer = csv.writer(filee)
    writer.writerow(["Comments"])
    writer.writerows(comm)
  filee.close();
