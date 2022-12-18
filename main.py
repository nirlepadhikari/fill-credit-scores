import pandas as pd
import json
import urllib.request
from dotenv import load_dotenv
import os
import PyPDF2
import io
import requests
import logging


# Loading env variables
load_dotenv()

# Set logging
log = "logs.log"
logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

# Get pdf content from url
def getPDFcontent(url : str):
    """
    Parse the PDF and return the data \n
    Args:
        url: URL to the PDF
    Returns:
        dict: Data from the PDF
    Raises:
        Exception: If the PDF doesn't exist or doesn't contain the data
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
        remote_file = urllib.request.urlopen(req).read()
        remote_file_bytes = io.BytesIO(remote_file)
        pdfdoc_remote = PyPDF2.PdfFileReader(remote_file_bytes)
        if len(pdfdoc_remote.pages) <=1 :
          print("Invalid pdf document")
          return False
        return pdfdoc_remote
    except Exception as e:
      print("Error occured", e)
      return False

# Extract credit scores from pdf content
def extract_scores(url:str):
  reader = getPDFcontent(url)
  if not reader:
    return
  page = reader.pages[0]
  extracted_text = page.extract_text()
  comp_score_text = extracted_text.split('\n')
  veda_score_text = extracted_text.split('VedaScore 1.1 : ')
  comprehensive_score = int(comp_score_text[comp_score_text.index('Comprehensive Score')+1])
  veda_score = veda_score_text[1].split(" ")[0]
  
  return {
      "comprehensive_score": comprehensive_score,
      "veda_score" : veda_score
}

def main():
  print("Testing docker, main started")
  return 0
  # Run a loop to get credit scores and update the system
  df = pd.read_csv('data.csv')
  df.columns = ['id', 'url']
  all_data = json.loads(df.to_json(orient='records'))
  url = os.environ.get("URL")
  for mainData in all_data:
    logging.info(f"For {str(mainData['id'])}")
    try:
      scores = extract_scores(mainData['url'])
      logging.info(f"Scores For {str(mainData['id'])} : {str(scores)}")
      r = requests.post(url, data = json.dumps({
        "api-key" : os.environ.get("API_KEY"),
        "app-id" : mainData['id'],
        "comprehensive-score" : scores['comprehensive_score'],
        "veda-score" : scores['veda_score']
        })).json()
      print(r)
      logging.info(f"Response for {str(mainData['id'])} : {str(r)}")
    except Exception as e:
      logging.critical(f"Couldn't update scores for {mainData['id']} because {str(e)}")

if __name__ == "__main__":
  main()