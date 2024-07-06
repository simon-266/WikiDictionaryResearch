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

#open file for saving the entire list of articles which got used
list_of_articles = open("ressources/list_of_articles.txt", 'a')

def fetch_and_process_article():

    #Takes a random Wikipedia article, processes the text, count words and returns a counter object with word counts.
    wikipedia.set_lang("en")
    try:
        random_article = wikipedia.random()
        article = wikipedia.page(random_article)
        text = article.content
        list_of_articles.write(random_article + "\n")
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

    #used Ai for understanding some concepts of Multithreading
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
total_runs = 15_000
batch_size = 5000
#Executes the multithreading function
final_counts = process_articles_in_batches(batch_size, total_runs)


#Convert to DataFrame
final_result = pd.DataFrame(final_counts.items(), columns=['word', 'frequency'])

import enchant
d = enchant.Dict("en_US")
def is_english_word(word):
    return d.check(word)

#Filtering non english words
final_result = final_result[final_result['word'].apply(is_english_word)]

#Calculate percentage of each word
total_words = final_result['frequency'].sum()
final_result['frequency_in_percent'] = round(final_result['frequency'] / total_words * 100, 6)

#Save to SQLite database
conn = sqlite3.connect('ressources/word_frequency.db')
final_result.to_sql('word_frequency', conn, if_exists='replace', index=False)
conn.close()

#adding a row with the total values
final_result = final_result.append({'word': '_total', 'frequency': total_words, 'frequency_in_percent': final_result['frequency_in_percent'].sum()}, ignore_index=True)

#Save to CSV
final_result['frequency'] = final_result['frequency'].astype(int)
final_result = final_result.sort_values(by="frequency", ascending=False)
final_result.to_csv('ressources/word_frequency.csv', index=False)

list_of_articles.close()
end = time.time()

print(f"Finished! {end-start}s")

#Time elapsed:  1104.005 seconds = ~18.4mins
