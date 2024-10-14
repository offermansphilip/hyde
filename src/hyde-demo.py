import json
from pyserini.search import FaissSearcher, LuceneSearcher
from pyserini.search.faiss import AutoQueryEncoder
from hyde import Promptor, OpenAIGenerator, CohereGenerator, HyDE

# Replace with your API key (OpenAI or Cohere)
KEY = '<api key>'

# Adding print statements to track progress
print("Initializing Promptor...")
promptor = Promptor('web search')

print("Initializing OpenAIGenerator with model 'text-davinci-003'...")
generator = OpenAIGenerator('text-davinci-003', KEY)

print("Initializing AutoQueryEncoder with 'facebook/contriever' model...")
encoder = AutoQueryEncoder(encoder_dir='facebook/contriever', pooling='mean')

print("Initializing FaissSearcher with 'contriever_msmarco_index/'...")
searcher = FaissSearcher('contriever_msmarco_index/', encoder)

print("Loading LuceneSearcher prebuilt index 'msmarco-v1-passage'...")
corpus = LuceneSearcher.from_prebuilt_index('msmarco-v1-passage')

print("Initializing HyDE with Promptor, Generator, Encoder, and Searcher...")
hyde = HyDE(promptor, generator, encoder, searcher)

print("Initialization complete. Ready to proceed!")
