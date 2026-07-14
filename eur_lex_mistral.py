### lib import

#import json
#import pandas as pd
#import requests
#import os 
#from bs4 import BeautifulSoup
#import time
#from mistralai.client import Mistral

# own key
API_KEY = "xxx"
client = Mistral(api_key=API_KEY)

df = pd.read_csv('vysledek.csv')
all_results = [] 
output_filename = 'result_full.csv'

system_rules = """You are acting as: Expert EU Legislative and Financial Analyst.
Task: Read the provided EU legislation text and extract specific economic and legal dimensions for a quantitative dataset.
Work fully independently. Do not speculate. Strictly classify the document based ONLY on the provided text.
If you cannot find the exact information, choose the most logical default based on the context.
CRITICAL: Fill in the "Reasoning" field FIRST before providing the classification values.
You must output EXACTLY and ONLY a valid JSON object. Do not use markdown blocks outside the JSON."""

for index, row in df.iloc[8692:].iterrows():
    celex = row['Celexové číslo']
    date = row['Datum dokumentu'] 
    form = row['Forma']           
    
    print(f"[{index+1}/{len(df)}] CELEX: {celex} ...", end=" ", flush=True)
    
    url = f"https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:{celex}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            legislation_text = soup.get_text(separator=' ', strip=True)[:30000]
            
            prompt_text = """
Output exactly in this JSON format:
{
  "Reasoning": {
    "Value": "[Briefly explain in 1-2 sentences your logic for the classifications. Do this first.]"
  },
  "Primary_Sector": {
    "Value": "[Choose EXACTLY ONE: Energetika, Finance, Stavebnictví, Průmysl, Životní prostředí, Jiné]"
  },
  "Impact_Intensity": {
    "Value": "[Choose EXACTLY ONE from 1-5 (low to high): 1, 2, 3, 4, 5]"
  },
  "Strictness": {
    "Value": "[Choose EXACTLY ONE from 1-5 (low to high): 1, 2, 3, 4, 5]"
  },
  "Time_Horizon": {
    "Value": "[Choose EXACTLY ONE: Okamžitý, Krátkodobý, Střednědobý, Dlouhodobý]"
  },
  "Complexity": {
    "Value": "[Choose EXACTLY ONE from 1-5 (low to high): 1, 2, 3, 4, 5]"
  }
}

Text of the legislation:
""" + legislation_text

            max_attempts = 5
            success = False
            
            for attempt in range(max_attempts):
                try:
                    response_prompt = client.chat.complete(
                        model="mistral-medium-2508", 
                        messages=[
                            {"role": "system", "content": system_rules},
                            {"role": "user", "content": prompt_text}
                        ],
                        response_format={"type": "json_object"}, 
                        temperature=0.0
                    )
                    
                    result_text = response_prompt.choices[0].message.content
                    data = json.loads(result_text)
                    
                    result_row = {
                        'Celex_Number': celex,
                        'Document_Date': date,
                        'Form': form,
                        'Reasoning': data.get('Reasoning', {}).get('Value', 'N/A'),
                        'Primary_Sector': data.get('Primary_Sector', {}).get('Value', 'N/A'),
                        'Impact_Intensity': data.get('Impact_Intensity', {}).get('Value', 'N/A'),
                        'Strictness': data.get('Strictness', {}).get('Value', 'N/A'),
                        'Time_Horizon': data.get('Time_Horizon', {}).get('Value', 'N/A'),
                        'Complexity': data.get('Complexity', {}).get('Value', 'N/A')
                    }
                    
                    all_results.append(result_row)
                    print("done")
                    success = True
                    break 
                    
                except json.JSONDecodeError:
                    pause = (attempt + 1) * 3
                    print(f"JSON error. Retrying in {pause}s... (Attempt {attempt + 1}/{max_attempts})", end=" ", flush=True)
                    time.sleep(pause)
                except Exception as e:
                    pause = (attempt + 1) * 3
                    print(f"API Error ({e}). Retrying in {pause}s... (Attempt {attempt + 1}/{max_attempts})", end=" ", flush=True)
                    time.sleep(pause)
                    
            if not success:
                print(f"Skipped CELEX {celex} after {max_attempts} failed attempts.")

        else:
            print(f"HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"Request Error: {e}")
        
    # ukládáná každých 250 výsledků
    current_count = index + 1
    if current_count % 250 == 0 and all_results:
        print(f"zpracováno: {current_count})")
        df_chunk = pd.DataFrame(all_results)
        
        if not os.path.isfile(output_filename):
            df_chunk.to_csv(output_filename, index=False, sep=';', encoding='utf-8-sig')
        else:
            df_chunk.to_csv(output_filename, mode='a', index=False, sep=';', encoding='utf-8-sig', header=False)
        all_results.clear()

if all_results:
    df_final_chunk = pd.DataFrame(all_results)
    if not os.path.isfile(output_filename):
        df_final_chunk.to_csv(output_filename, index=False, sep=';', encoding='utf-8-sig')
    else:
        df_final_chunk.to_csv(output_filename, mode='a', index=False, sep=';', encoding='utf-8-sig', header=False)
    all_results.clear()

# check
df_result = pd.read_csv(output_filename, sep=';', encoding='utf-8-sig')
print(f"uloženo {len(df_result)}.")
df_result.head()