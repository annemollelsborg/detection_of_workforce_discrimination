# --- Install nltk and download stopwords if you haven't already ---
# pip install nltk
import nltk
nltk.download('punkt')
nltk.download('stopwords')

# --- Standard libraries ---
import pandas as pd
import re
from collections import Counter
from nltk.corpus import stopwords

# Load Danish word list from .dic file
danish_words_path = 'Danish.dic'

danish_words = set()

with open(danish_words_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Skip the first line (it usually just says how many words)
for line in lines[1:]:
    word = line.strip().split('/')[0].lower()  # Remove any formatting after '/'
    if word:  # Only add non-empty words
        danish_words.add(word)

print(f"Loaded {len(danish_words)} Danish words.")


# --- Load your dataset ---
df = pd.read_csv('job_descriptions_final.csv', sep=';', quoting=1)

# --- Map your manual field gender labels ---
user_gender_mapping = {0: 'male-dominated', 1: 'female-dominated'}
df['field_gender_user'] = df['Male or female'].map(user_gender_mapping)

# --- Define Danish stopwords ---
danish_stopwords = set(stopwords.words('danish'))

# --- Define custom extra stopwords to clean scraping artifacts ---
custom_stopwords = danish_stopwords.union({
    'indeed', 'dk', 'https', 'com', 're', 'ans', 'from', 'viewjob', 'in', 'the', 
    'st', 'to', 'jk', 'ger', 'hj', 'tter', 'stillingen', 'arbejde', 'job', 'del'
})

# --- Preprocessing function ---
def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-ZæøåÆØÅ]+', ' ', text)  # Keep Danish letters
    tokens = text.split()
    tokens = [word for word in tokens if word in danish_words and word not in custom_stopwords and len(word) > 1]
    return tokens

# --- Apply preprocessing to descriptions ---
df['tokens'] = df['description'].apply(preprocess_text)

# --- Split by male/female dominated ---
male_tokens = df[df['field_gender_user'] == 'male-dominated']['tokens'].sum()
female_tokens = df[df['field_gender_user'] == 'female-dominated']['tokens'].sum()

# --- Count word frequencies ---
male_word_counts = Counter(male_tokens)
female_word_counts = Counter(female_tokens)

# --- Get top N most common words ---
N = 20
top_male_words = male_word_counts.most_common(N)
top_female_words = female_word_counts.most_common(N)

# --- Output the results ---
print("\nTop words in male-dominated industries:")
for word, count in top_male_words:
    print(f"{word}: {count}")

print("\nTop words in female-dominated industries:")
for word, count in top_female_words:
    print(f"{word}: {count}")
