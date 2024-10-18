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
searcher = FaissSearcher('./src/contriever_msmarco_index/', query_encoder)
corpus = LuceneSearcher.from_prebuilt_index('msmarco-v1-passage')

# Load the topics and qrels (query relevance judgments)
topics = get_topics('dl19-passage')
qrels = get_qrels('dl19-passage')

# Initialize the promptor and generator using Llama3.1
promptor = Promptor(task='web search')  # Adjust the task as needed
second_promptor = Promptor(task='TREC_COVID')   # Adjust the task as needed
generator = OllamaGenerator(model_name='llama3.1')  # Use Llama 3.1 with Ollama

# Initialize the HyDE engine with the promptor, generator, encoder, and searcher
hyde = HyDE(promptor=promptor, second_promptor=second_promptor, generator=generator, encoder=query_encoder, searcher=searcher)

print("___MULTI_PROMPT_HYDE____")
# Perform retrieval and evaluation with generated passages
with open('./runs_playground/multi_prompt-hyde-dl19-contriever-llama3.1-top1000-8rep-trec', 'w') as f, open('./runs_playground/multi_prompt-hyde-dl19-llama3.1-gen.jsonl', 'w') as fgen:
    for qid in tqdm(topics):
        if qid in qrels:
            query = topics[qid]['title']

            # Generate hypotheses documents using HyDE (llama3.1)
            hypothesis_documents = hyde.generate(query)

            # Encode the query and generated documents to form the HyDE vector
            hyde_vector = hyde.encode(query, hypothesis_documents)

            # Search using the HyDE vector
            hits = hyde.search(hyde_vector, k=1000)

            # Write results to file
            rank = 0
            for hit in hits:
                rank += 1
                f.write(f'{qid} Q0 {hit.docid} {rank} {hit.score} rank\n')

# Evaluation commands
os.system('python -m pyserini.eval.trec_eval -c -l 2 -m map dl19-passage ./runs_playground/multi_prompt-hyde-dl19-contriever-gpt3-top1000-8rep-trec')
os.system('python -m pyserini.eval.trec_eval -c -m ndcg_cut.10 dl19-passage ./runs_playground/multi_prompt-hyde-dl19-contriever-gpt3-top1000-8rep-trec')
os.system('python -m pyserini.eval.trec_eval -c -l 2 -m recall.1000 dl19-passage ./runs_playground/multi_prompt-hyde-dl19-contriever-gpt3-top1000-8rep-trec')

# print("____NORMAL_HYDE____")
# # Perform retrieval and evaluation with generated passages
# with open('./runs_playground/hyde-dl19-contriever-llama3.1-top1000-8rep-trec', 'w') as f, open('./runs_playground/hyde-dl19-llama3.1-gen.jsonl', 'w') as fgen:
#     for qid in tqdm(topics):
#         if qid in qrels:
#             query = topics[qid]['title']

#             # Improve query
#             improved_query = hyde.improved_query(query)

#             # Generate hypotheses documents using HyDE (llama3.1)
#             hypothesis_documents = hyde.generate(improved_query)

#             # Encode the query and generated documents to form the HyDE vector
#             hyde_vector = hyde.encode(query, hypothesis_documents)

#             # Search using the HyDE vector
#             hits = hyde.search(hyde_vector, k=1000)

#             # Write results to file
#             rank = 0
#             for hit in hits:
#                 rank += 1
#                 f.write(f'{qid} Q0 {hit.docid} {rank} {hit.score} rank\n')

# # Evaluation commands
# os.system('python -m pyserini.eval.trec_eval -c -l 2 -m map dl19-passage ./runs_playground/hyde-dl19-contriever-gpt3-top1000-8rep-trec')
# os.system('python -m pyserini.eval.trec_eval -c -m ndcg_cut.10 dl19-passage ./runs_playground/hyde-dl19-contriever-gpt3-top1000-8rep-trec')
# os.system('python -m pyserini.eval.trec_eval -c -l 2 -m recall.1000 dl19-passage ./runs_playground/hyde-dl19-contriever-gpt3-top1000-8rep-trec')


