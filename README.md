Thank you for reviewing my project. This project was made as a final project for CS50x on Edx.org

# WikiDictionaryResearch
#### Video Demo:  https://youtu.be/0CWOLI26ayE
#### Description:

## I came to this project by coming across the following statement:
## "It’s been said that the top 1,000 most frequent words in a language make up over 80% of the speech."

## This project contains following files
- extraction.py
- WikiDictionaryResearch.ipynb
- list_of_articles.txt
- word_frequency.csv
- word_frequency.db

## extraction.py

### This is the main part of this project this python script is used to create allmost all other files.
### It extracts 15,000 Wikipedia articles and calculates the frequency of all english words inside its pages

### For this file the following python libraries are used:
- wikipedia
  used to extract the contents of all 15.000 Wikipedia pages
  
- pandas
  to evalute the words and save them to the csv and database file

- sqlite3
  to store the list into a db file
  
- re
  to remove punctuation of the wikipedia articles
  
- collections
  to count the frequency of the words efficiently
  
- concurrent
  to make the extraction faster with multithreading
  
- enchant
  to check if a word is a actual english words

- warings
  removes the warning messages which filled up the entire terminal window

### This file contains three following functions

- process_articles_in_batches
    Uses the concurrent librarie to execute the 'fetch_and_process_article'
    function in multiple threads and in multiple batches to avoid not having enough ram
    and making the programm faster in generall by using multiple threads instead of evaluating
    the article one and another.
    At last it gives back an dictionary which will be used to transform it into a pandas dataframe

    Args:
      batch_size:
        how big should the batches be to evalute
      total_runs:
        how many wikipedia articles should be proccesed

- fetch_and_process_article
    executed by 'process_articles_in_batches'
    it gets a random english wikipedia articles save the headline to the list_of_articles.txt file
    then fetches it content and at last removes punctuation and counts the words before giving them back in a dictionary

- is_english_word
    takes a word as input and returns true if it is a word in the english dictionary else it returns false

### These are the following variables in the main function in this file:

- list_of_articles
  a filestream to the list_of_articles.txt file
  
- total_runs
  used by the proces_article_in_batches function as input for the amount of articles extracted
  increasing this would mean there getting more articles extracted
  
- batch_size
  used by the proces_article_in_batches function as input for the size of the batches
  increasing this would change how many articles getting processed during a single batch
  and would also increase the amount of ram is needed
  
  
- final_counts
  is a dictionary of words returned by the process_article_in_batches function
  which gets converted into a pandas dataframe and saved into the final_result variable
  
- final_result
  is a pandas dataframe which gets changes sometimes but it always contains the current result and is
  saved into a csv and database file at the end

  ####columns: 'word', 'frequency', 'frequency_in_percent'

  - word
    the english word
  - frequency
    how many times the words has occured in the fetched wikipedia articles
  - frequency_in_percent
    how much percentage does the word cover in the fetched wikipedia articels
  
- total_words
  the sum of all english words of the entire fetched wikipedia articles
  this variable gets used to calculate the frequency_in_percent column in final_result
  and also is used to create the _total row for the csv file
  
- conn
  database connection to the sqlite3 word_frequency.db file
  
- start
  the milliseconds the extraction process has started
  
- end
  the milliseconds the extraction process has finished

## WikiDictionaryResearch.ipynb

### This ipython notebook should show off the results of extraction.py by answering the question

### For this file the following python libraries are used:

- matplotlib
  used to create the piechart out of a pandas dataframe
  
- sqlite3
  used to load the list from word_frequency.db
  and saves it into a pandas dataframe
  
- pandas
  to convert the sqlite3 database data into a dataframe and to use it with the piechart

## list_of_articles.txt

### This files is generated by the extraction.py and the only mission of it
### is to keep track which Article got used during the webscraping part.
#### These are all random articles i do not own or edited any of these.

## word_frequency.csv

### This file is for myself to see if the extractor makes it job correctly easier and also for lookup
### any word i'm currios of how it performed

## word_frequency.db

### This file is used by the WikiDictionaryResearch.ipynb notebook to fetch the data and create its
### piechats with it
