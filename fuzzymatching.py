from pandas import json_normalize
from requests import get
from fuzzywuzzy import fuzz
import pandas as pd
import re

# Gets a list of words that was repeated above a threshold
def repetitive_tracker(statement, counter):
    """
    Input: List of unique titles and an integer
    Output: List of words that was repeated above a threshold (counter)
    """
    # Initialize a dictionary to store word counts
    word_counts = {}

    # Define a regular expression pattern to match words (words are considered to be sequences of letters and numbers)
    word_pattern = re.compile(r'\w+')
    # Loop through the list of strings
    for text in statement:
        # Find all words in the text using the regular expression pattern
        words = word_pattern.findall(text)
        # Loop through the words and update word counts
        for word in words:
            word = word.lower()  # Convert to lowercase for case-insensitive counting
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

    filtered_word_counts = {word: count for word, count in word_counts.items() if count > counter}

    # Sort the word counts in descending order by count
    sorted_word_counts = dict(sorted(filtered_word_counts.items(), key=lambda item: item[1]))

    repetitive_words = []
    # Display the word counts
    for word, count in sorted_word_counts.items():
        # print(f"'{word}': {count} times")
        repetitive_words.append(word)

    return repetitive_words
    
# Function to preprocess text by removing specific words
def preprocess_text(text, words_to_exclude):
    """
    Input: A title from the loop and the list of words to filter out from the looping titles
    Output: Filtered title
    """

    # Turn the list into a single string
    words_string = ' '.join(words_to_exclude)
    
    # Define a regular expression pattern to match words (words are considered to be sequences of letters and numbers)
    word_pattern = re.compile(r'\w+')
    
    # Find all words in the text using the regular expression pattern
    words = word_pattern.findall(text)
    
    # Filter out words to exclude
    filtered_words = [word.lower() for word in words if word.lower() not in words_string]
    
    # Join the filtered words to create a processed text
    processed_text = ' '.join(filtered_words)
    
    return processed_text

def fuzzy_matching(user_input:str, accuracy: int):
    """
    Input: User's Entity Input
    Output: A DataFrame with the top matches
    """

    # Response from HTTP GET Request
    response = get("https://www.sec.gov/files/company_tickers.json")

    # Convert the response into JSON to make it easier to use
    response = response.json()

    # Turn the json into a list
    results = list(response.values())
    
    # Turn the list into a Pandas DataFrame
    result_df = json_normalize(results)

    # Get all titles as a list
    titles = result_df['title'].unique().tolist()

    # Capture all the word that appears as many times as the accuracy or more.
    rep_word = repetitive_tracker(titles, accuracy)

    # Setup empty list
    match_list = []

    # Loop through the list of title
    for i in titles:
        # Filter out any word in the title that is in rep_word
        fix = preprocess_text(i, rep_word)
        
        # Get the title and how much they match 
        ent_ratios = [i, fuzz.partial_ratio(user_input, fix)]

        # Combining all results into match_list
        match_list.append(ent_ratios)

    columns = ['Title', 'Matching%']

# Create a DataFrame from the match_list
    df = pd.DataFrame(match_list, columns=columns).sort_values(by='Matching%', ascending=False)

    return df
