import wikipedia
import pandas as pd
import time
import sqlite3
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import warnings
#Suppress warnings to make the program output cleaner
warnings.catch_warnings()
warnings.simplefilter("ignore")

def fetch_and_process_article():

    #Takes a random Wikipedia article, processes the text, count words and returns a counter object with word counts.
    wikipedia.set_lang("en")
    try:
        random_article = wikipedia.random()
        random_article = wikipedia.page(random_article)
        text = random_article.content
    except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
        return None
    
    #Remove punctuation and digits, then split into words
    text = re.sub(r'[^\w\s]', ' ', text)
    text = text.lower()
    words = text.split()
    
    #Remove single character words
    words = [word for word in words if len(word) > 1]
    
    #Count word frequencies
    word_counts = Counter(words)
    
    return word_counts

#Uses multiple threads to count words for the total
def process_articles_in_batches(batch_size, total_runs):

    """
    Processes Wikipedia articles in batches using multiple threads and summonize words.
    
    Args:
        batch_size: Number of articles to process in each batch
        total_runs: Total number of articles to process.
    """
    aggregated_counts = Counter()
    with ThreadPoolExecutor() as executor:
        for i in range(0, total_runs, batch_size):
            futures = [executor.submit(fetch_and_process_article) for _ in range(min(batch_size, total_runs - i))]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    aggregated_counts.update(result)
    return aggregated_counts

start = time.time()

#To make the process faster but use more memory increase the batch size
total_runs = 10_000
batch_size = 100
#Executes the multithreading function
final_counts = process_articles_in_batches(batch_size, total_runs)

#Convert to DataFrame
final_result = pd.DataFrame(final_counts.items(), columns=['word', 'frequency'])

#Calculate percentage of each word
total_words = final_result['frequency'].sum()
final_result['frequency in %'] = round(final_result['frequency'] / total_words * 100, 6)
final_result = final_result.append({'word': '_total', 'frequency': total_words, 'frequency in %': 100}, ignore_index=True)

#Save to CSV
final_result['frequency'] = final_result['frequency'].astype(int)
final_result = final_result.sort_values(by="frequency", ascending=False)
final_result.to_csv('word_frequency.csv', index=False)

#Save to SQLite database
conn = sqlite3.connect('word_frequency.db')
final_result.to_sql('word_frequency', conn, if_exists='replace', index=False)
conn.close()

end = time.time()
print(f"Finished! {end-start}s")