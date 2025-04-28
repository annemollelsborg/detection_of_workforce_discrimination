import os
import time
import pandas as pd
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Load the CSV file containing job titles and descriptions
df = pd.read_csv('job_descriptions.csv')
documents = df.to_dict('records')

# Set OpenAI API key (ensure it's valid)
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Use the **smallest model** (cheaper & uses fewer tokens)
EMBEDDING_MODEL = "text-embedding-3-small"

# Add retry logic to **avoid rate limit errors**
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def get_embedding(text, model=EMBEDDING_MODEL):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding  # Return the embedding vector

# **Batch requests** to avoid too many API calls
batch_size = 3
embeddings = {'title': [], 'description': []}

for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    titles = [d['title'].replace("\n", " ") for d in batch]
    descriptions = [d['description'].replace("\n", " ") for d in batch]

    try:
        response_titles = client.embeddings.create(input=titles, model=EMBEDDING_MODEL)
        response_descriptions = client.embeddings.create(input=descriptions, model=EMBEDDING_MODEL)

        for title_emb, desc_emb in zip(response_titles.data, response_descriptions.data):
            embeddings['title'].append(title_emb.embedding)
            embeddings['description'].append(desc_emb.embedding)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)

df_embeddings = pd.DataFrame(embeddings)
df_embeddings.to_csv('embedded_job_descriptions.csv', index=False)

print("Embedding of titles and descriptions into two columns completed successfully.")
