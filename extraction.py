import wikipedia
import pandas as pd
import time
import sqlite3
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import warnings
# Suppress warnings to keep the program output clean
warnings.catch_warnings()
warnings.simplefilter("ignore")

# Open file to log all the articles that are processed
list_of_articles = open("ressources/list_of_articles.txt", 'a')

def fetch_and_process_article():
    """
    Fetches a random Wikipedia article, processes the text, and counts word frequencies.
    
    Returns:
        Counter object containing word counts or None if the article cannot be processed.
    """
    wikipedia.set_lang("en")  # Set Wikipedia language to English
    try:
        # Get a random article and its content
        random_article = wikipedia.random()
        article = wikipedia.page(random_article)
        text = article.content
        # Log the article's title
        list_of_articles.write(random_article + "\n")
    except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
        # If the article has issues (e.g., disambiguation or non-existent), skip it
        return None
    
    # Remove punctuation, digits, and convert text to lowercase
    text = re.sub(r'[^\w\s]', ' ', text)
    text = text.lower()
    # Split the text into words
    words = text.split()
    
    # Filter out single-character words (e.g., 'a', 'I')
    words = [word for word in words if len(word) > 1]
    
    # Count word frequencies
    word_counts = Counter(words)
    
    return word_counts

def process_articles_in_batches(batch_size, total_runs):
    """
    Processes Wikipedia articles in batches using multiple threads and aggregates word counts.
    
    Args:
        batch_size: The number of articles to process in each batch.
        total_runs: The total number of articles to process.
    
    Returns:
        A Counter object containing aggregated word counts across all processed articles.
    """
    aggregated_counts = Counter()
    with ThreadPoolExecutor() as executor:
        # Process articles in batches
        for i in range(0, total_runs, batch_size):
            # Submit tasks to the executor for concurrent processing
            futures = [executor.submit(fetch_and_process_article) for _ in range(min(batch_size, total_runs - i))]
            # Collect the results as they complete
            for future in as_completed(futures):
                result = future.result()
                if result:
                    aggregated_counts.update(result)
    return aggregated_counts

start = time.time()

# Define total number of articles to fetch and batch size for processing
total_runs = 15_000
batch_size = 5000  # Increase batch size to speed up processing (requires more memory)
# Execute the multithreaded function to process articles and count words
final_counts = process_articles_in_batches(batch_size, total_runs)

# Convert the word counts to a DataFrame for easier manipulation and analysis
final_result = pd.DataFrame(final_counts.items(), columns=['word', 'frequency'])

import enchant
d = enchant.Dict("en_US")

def is_english_word(word):
    """
    Checks if a word is valid in the English dictionary using the enchant library.
    
    Args:
        word: The word to check.
    
    Returns:
        True if the word is in the English dictionary, False otherwise.
    """
    return d.check(word)

# Filter out non-English words from the DataFrame
final_result = final_result[final_result['word'].apply(is_english_word)]

# Calculate the frequency percentage of each word
total_words = final_result['frequency'].sum()  # Total number of words across all articles
final_result['frequency_in_percent'] = round(final_result['frequency'] / total_words * 100, 6)

# Save the results to an SQLite database for later use
conn = sqlite3.connect('ressources/word_frequency.db')
final_result.to_sql('word_frequency', conn, if_exists='replace', index=False)
conn.close()

# Add a row to the DataFrame that summarizes the total word count and frequency percentage
final_result = final_result.append({'word': '_total', 'frequency': total_words, 'frequency_in_percent': final_result['frequency_in_percent'].sum()}, ignore_index=True)

# Save the results to a CSV file for easy access and review
final_result['frequency'] = final_result['frequency'].astype(int)  # Convert frequencies to integers
final_result = final_result.sort_values(by="frequency", ascending=False)  # Sort words by frequency
final_result.to_csv('ressources/word_frequency.csv', index=False)

# Close the file stream after finishing the article logging
list_of_articles.close()

end = time.time()

# Print the time taken to complete the extraction process
print(f"Finished! {end-start}s")

# Time elapsed: ~18.4 minutes (1104.005 seconds)
