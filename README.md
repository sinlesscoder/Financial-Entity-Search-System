<center>

## Financial Entity Search System

 Ali Ahmed
 October 16, 2023

</center>


---

> Create an entity search system which can match an input entity with closely related entities using a metric of my choice.

<center>

### End-to-End Solution

</center>

#### Web Application 

For this assignment, I've written my solution using the Python programming language. Leveraging a web-application library called [Streamlit](https://streamlit.io), the application I developed asks an end user for input regarding with an entity and the number of top matches desired, then clicking the `Search` button to show the entered number of top matches as a table. In order to give the user simulated control over the resulting matches, I added another input feature which acts as a way of manually setting a threshold for the key metric to alter results.

Below is a screenshot of the interface.

![](https://p131.p1.n0.cdn.getcloudapp.com/items/mXuvr7nl/6b88112a-e6aa-40c0-82ed-74795b2255c1.jpg?v=e93923d0e16c68e8417df939e75455c7)

#### Dataset

As the assignment proposed, I made use of the default dataset related to stock tickers. Out of the columns that were available, I had the opportunity to choose between the following columns for entity search:

<table>
<tr>
<th> Column Name
</tr>

<tr>
<td> Ticker </td>
</tr>

<tr>
<td>Title</td>
</tr>

</table>


From the options above, I chose `Title` as it gave me the exact name of the organization which the ticker represents. The example shown in the assignment instructions also indicated company titles which also was factored in my decision to go with this column. In order to retrieve the dataset's contents as a DataFrame, I made use of the `requests` module to get a `JSON` response which I later applied the `json_normalize` method in `pandas` to transform the dataset into a tabular one. The exact logic I applied can be found in this code below:

```python
from requests import get

# Response from HTTP GET Request
    
    ## Performing a HTTP GET request on URL below
    response = get("https://www.sec.gov/files/company_tickers.json")

    ## Converting the response into an in-memory JSON response
    response = response.json()

    ## Casting the values of the object's dictionary representation
    ## as a Python list
    results = list(response.values())

    # Creating a DataFrame in pandas after normalizing the list of objects
    result_df = json_normalize(results)

    # Get all titles as a list
    titles = result_df['title'].unique().tolist()
```

<center>

### Search Algorithm

</center>

To conduct entity search, I implemented the metric called [Levenshtein's Distance](https://en.wikipedia.org/wiki/Levenshtein_distance). The metric's design allows it to score the match by how much the entities have a change in a letter(s) of one string to match one another. Leveraging the library called [Fuzzy-Wuzzy](https://pypi.org/project/fuzzywuzzy/), I scored the match between the user's input and each title in the dataset.

Using this library, I wanted to create a function that takes a user input and the amount of top matching titles. The function would then take that user input and compare it to every title in the list, and give a score in similarity between the two. Then I would append all of the matches into one list, and turn it into a `Pandas DataFrame`, which becomes the end user's output. 


Levenshtein's distance is great to find keyword searches that is similar or not exactly similar. Its mechanism quantifies the minimum number of single-character edits (insertions, deletions, or substitutions) required to transform one word into another. Some example of phrases expected to be resolved include: 

1. Typos (e.g. aple, apple)
2. Similar words (e.g. apple, applied)
3. Not exactly similar words (e.g. Montreal, America)


<center>

### Implementation Details

Below, I write about the Python functions I wrote to assist in implementing the entity matching with the above search algorithm.

#### Fuzzy Matching Function

The `fuzzy_matching` function takes two key inputs: the user's query and the number of top matching titles to retrieve. Its operation involves the following steps:

1. **Comparison with Titles**: The function compares the user's input with each title in the dataset and assigns a similarity score to each pair.

2. **List of Matches**: The function then accumulates all the matching titles into a list.

3. **Conversion to Pandas DataFrame**: Finally, the function converts this list of matches into a Pandas DataFrame, which serves as the output of the process.

```python
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
```

#### Repetitive Tracker Function

Within the `fuzzy_matching` process, another important function called `repetitive_tracker` comes into play. This function requires two inputs: a list of all unique titles from the dataset and an integer value. Its operation involves the following steps:

1. **Word Extraction**: The function extracts all words that appear in all titles and compiles them into a new list. For example, a title like "Bank of America" is broken down into individual words: "Bank," "of," and "America."

2. **Word Counting**: The function then counts the occurrences of each word in the new list. The output is a list of words that appeared the same number of times as the input integer provided by the user or more. This list is named `rep_word`.

```python
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
```

#### Preprocess Text Function

The `Preprocess_text` function is also utilized within the `fuzzy_matching` process. This function requires two inputs: a title from the dataset and the `rep_word` list. Its operation involves the following steps:

1. **List to String**: The function converts the list produced by `repetitive_tracker` into a single string.

2. **Filtering**: The function filters the title to remove any words that are present in the `rep_word` list.

3. **Fuzzy-Wuzzy Matching**: After filtering, the function conducts the fuzzy-wuzzy matching with the filtered title and the user's entity search input to determine the similarity score.

By implementing these functions, the backend efficiently performs entity matching, taking into account word similarity and the removal of frequently occurring words to provide meaningful search results.

```python
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
```

### Evaluation and Testing

</center>

Since Levenshtein's distance provides a numerical value to score how similar two entities are, it was important to try out several thresholds before setting up the keyword matching as a ranking design. For this dataset, I've identified thresholds for this dataset via simulation of expected cases on several threshholds to see where the cases begin to fail.

To make the end user as a tester, I've included a third input in the Streamlit application that allows the selection of the threshold for result tuning on entity searches which leverages the `partial_ratio()` method in the `fuzzywuzzy` Python module. This module will return a 100% match if one entity is present as a sub-entity in another word or phrase.

#### Example of Partial Ratio Matching

1. `berkshire` -> `berkshire hathaway` : `100%`
2. `apple` -> `alphabet` : `~85%`

#### Expected Behavior

##### Advantages

- **Typo Resolution:** Aple -> Apple
- **Similar Company Names:** Ameica -> Trans American Aquaculture, Inc

##### Disadvantages

- Levenshtein's distance only factors into account the similarity of the entities based on the orthography of the keywords that are being compared. Since the dataset used only consists of stock titles, there's not much context-specific information that can be leveraged for getting a more informed search. For example, `Apple Inc` and `Alphabet Inc` are actually very similar titles for stocks since they're both considered as the category of big tech with similar consumer verticals.

### Local Deployment and Project Setup

#### Running the Entity Search Application

1. **Run the Streamlit Application**: Open your terminal or command prompt and execute the `streamlit_app.py` script. You can do this by pasting the following command and replacing the file path with the actual path to the `streamlit_app.py` script on your system:

```bash
streamlit run c:/Users/example/Documents/Example/streamlit_app.py
```

#### Accessing the Local Browser

Once you run the script, it will automatically open a local web browser with the entity search interface.

#### Entering Search Criteria

In the entity search interface, you can enter your search criteria:

- **Entity Search Term**: Input the entity or keyword you want to search for.
- **Amount of Top Matches**: Specify the number of top matching entities you want to retrieve as a result.
- **Remove Frequent Words**: Optionally, you can set a threshold for removing frequently occurring words in the titles. For example, entering "30" will filter the titles to remove any words that were repeated 30 or more times. A recommended range for this value is between 30 and 100, depending on your specific data.

#### Initiating the Search

After you've entered your search term and other criteria, click the "Search" button in the interface to initiate the search.

#### Viewing the Results

The system will display a DataFrame containing the matching titles and their corresponding scores from the fuzzy-wuzzy matching algorithm. This allows you to see the top matching entities along with their matching percentages, helping you identify the most relevant results.

By following these steps, you can easily search for entities, control the number of results, and customize the filtering of titles based on word frequency using the provided interface.

```python
import streamlit as st
from fuzzymatching import fuzzy_matching

# Centered Title
st.markdown("<h1 style='text-align:center'> Entity Search </h1>", unsafe_allow_html=True)

col_1, col_2, col_3 = st.columns(3, gap='medium')

# Search term
with col_1:
  entity = st.text_input("Type in the search entity: ")

# Amount of result
with col_2:
  number = st.number_input("Enter the number of matches:", min_value=0)

# Capture the repeated words over the amount entered
with col_3:
  acc = st.number_input("Enter a Levenshtein threshold value:", min_value=0)

# Click to receive the matches
if st.button("Search"):


![](https://p131.p1.n0.cdn.getcloudapp.com/items/jku6Pyq8/7feff1d8-726d-4839-bf6a-f3636d7b9249.jpg?v=12678b65c0af6fdf1a2cd3a4d465047b)
