import json
from pyserini.search import FaissSearcher, LuceneSearcher
from pyserini.search.faiss import AutoQueryEncoder
from hyde import Promptor, OllamaGenerator, HyDE

# Replace with your API key (OpenAI or Cohere)
KEY = 'REDACTED'

# Adding print statements to track progress
print("Initializing Promptor...")
promptor = Promptor('web search')

print("Initializing OllamaGenerator with model 'llama3.1'...")
generator = OllamaGenerator('llama3.1')

print("Initializing AutoQueryEncoder with 'facebook/contriever' model...")
encoder = AutoQueryEncoder(encoder_dir='facebook/contriever', pooling='mean')

print("Initializing FaissSearcher with 'contriever_msmarco_index/'...")
searcher = FaissSearcher('./src/contriever_msmarco_index/', encoder)

print("Loading LuceneSearcher prebuilt index 'msmarco-v1-passage'...")
corpus = LuceneSearcher.from_prebuilt_index('msmarco-v1-passage')

print("Initializing HyDE with Promptor, Generator, Encoder, and Searcher...")
hyde = HyDE(promptor, generator, encoder, searcher)

print("Initialization complete. Ready to proceed!")

query = 'how long does it take to remove wisdom tooth'

# Generate the prompt only once
prompt = hyde.prompt(query)
print(prompt)

# Generate the hypothesis documents only once
hypothesis_documents = hyde.generate(query)
for i, doc in enumerate(hypothesis_documents):
    print(f'HyDE Generated Document: {i}')
    print(doc.strip())

# Encode the hypothesis documents only once
hyde_vector = hyde.encode(query, hypothesis_documents)
print(hyde_vector.shape)

# Perform the search once with the encoded vector
hits = hyde.search(hyde_vector, k=10)
for i, hit in enumerate(hits):
    print(f'HyDE Retrieved Document: {i}')
    print(hit.docid)
    print(json.loads(corpus.doc(hit.docid).raw())['contents'])

# Perform end-to-end search only once
hits = hyde.e2e_search(query, k=10)
for i, hit in enumerate(hits):
    print(f'HyDE Retrieved Document: {i}')
    print(hit.docid)
    print(json.loads(corpus.doc(hit.docid).raw())['contents'])