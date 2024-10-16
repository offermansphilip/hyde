import os
import numpy as np
from tqdm import tqdm
from pyserini.search import FaissSearcher, LuceneSearcher
from pyserini.search.faiss import AutoQueryEncoder
from pyserini.search import get_topics, get_qrels

# Import the classes from your provided module
from hyde import OllamaGenerator, Promptor, HyDE

# Initialize the query encoder and searcher
query_encoder = AutoQueryEncoder(encoder_dir='facebook/contriever', pooling='mean')
searcher = FaissSearcher('contriever_msmarco_index/', query_encoder)
corpus = LuceneSearcher.from_prebuilt_index('msmarco-v1-passage')

# Load the topics and qrels (query relevance judgments)
topics = get_topics('dl19-passage')
qrels = get_qrels('dl19-passage')

# Initialize the promptor and generator using Llama3.1
promptor = Promptor(task='web search')  # Adjust the task as needed
generator = OllamaGenerator(model_name='llama3.1')  # Use Llama 3.1 with Ollama

# Initialize the HyDE engine with the promptor, generator, encoder, and searcher
hyde = HyDE(promptor=promptor, generator=generator, encoder=query_encoder, searcher=searcher)

# Perform retrieval and evaluation with generated passages
for qid in tqdm(topics):
    if qid in qrels:
        query = topics[qid]['title']
        print(f"Query: {query}")
        # Generate hypotheses documents using HyDE (llama3.1)
        hypothesis_documents = hyde.generate(query)
        print(f"Hypothesis Documents: {hypothesis_documents}")

        # Encode the query and generated documents to form the HyDE vector
        hyde_vector = hyde.encode(query, hypothesis_documents)

        # Search using the HyDE vector
        hits = hyde.search(hyde_vector, k=1000)
        for hit in hits:
            print(f"Hit: {hit}")


