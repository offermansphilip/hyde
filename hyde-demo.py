import json
from pyserini.search import FaissSearcher, LuceneSearcher
from pyserini.search.faiss import AutoQueryEncoder

from hyde import Promptor, OpenAIGenerator, CohereGenerator, HyDE

KEY = '<api key>' # replace with your API key, it can be OpenAI api key or Cohere api key
promptor = Promptor('web search')
generator = OpenAIGenerator('text-davinci-003', KEY)
encoder = AutoQueryEncoder(encoder_dir='facebook/contriever', pooling='mean')
searcher = FaissSearcher('contriever_msmarco_index/', encoder)
corpus = LuceneSearcher.from_prebuilt_index('msmarco-v1-passage')

hyde = HyDE(promptor, generator, encoder, searcher)

print("done")