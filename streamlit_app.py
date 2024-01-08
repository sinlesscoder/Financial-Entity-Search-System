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

    df = fuzzy_matching(entity, acc)

    # Resetting the index
    df = df.reset_index().drop('index', axis=1)

    st.info(f"Showing {number} matches for entity: {entity} .")

    st.dataframe(df.head(number), use_container_width=True)

    st.balloons()