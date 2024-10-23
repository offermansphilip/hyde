import os
import numpy as np
from tqdm import tqdm
from pyserini.search import FaissSearcher, LuceneSearcher
from pyserini.search.faiss import AutoQueryEncoder
from pyserini.search import get_topics, get_qrels

# Import the classes from your provided module for generating and handling prompts
from hyde import OllamaGenerator, Promptor, HyDE, MultiPromptHyDE

# Define paths and variables for models, index paths, and output files
model_name = 'llama3.1'  # The model to be used for generating responses
encoder = 'facebook/contriever'  # Query encoder model
index_path = './src/contriever_msmarco_index/'  # Path to Faiss index for passage retrieval
prebuilt_index = 'msmarco-v1-passage'  # Pre-built Lucene index for MSMARCO passage dataset
run_directory = './runs/'  # Directory to store results of retrieval
multi_prompt_runfile = 'multi_prompt-hyde-dl19-contriever-llama3.1-top1000-8rep-trec'  # File to store MultiPromptHyDE run results
topics_name = 'dl19-passage'  # Name of the evaluation topic set

# Initialize the query encoder for transforming queries into dense vectors
query_encoder = AutoQueryEncoder(encoder_dir=encoder, pooling='mean')

# Create a FaissSearcher for dense vector search over the Faiss index
searcher = FaissSearcher(index_path, query_encoder)

# Load a pre-built Lucene index for corpus-based retrieval
corpus = LuceneSearcher.from_prebuilt_index(prebuilt_index)

# Load the topics (queries) and the corresponding qrels (ground truth relevance judgments)
topics = get_topics(topics_name)
qrels = get_qrels(topics_name)

# Initialize the Ollama-based text generator using the specified model (Llama 3.1)
generator = OllamaGenerator(model_name=model_name)


print("___MULTI_PROMPT_HYDE____")

# Create a Promptor object for generating web search prompts
promptor = Promptor(task='web search')

# Initialize the HyDE model for generating hypotheses and performing retrieval
hyde = HyDE(promptor=promptor, generator=generator, encoder=query_encoder, searcher=searcher)

# Define the output file for storing the MultiPromptHyDE retrieval run results
multi_prompt_runfilepath = os.path.join(run_directory, multi_prompt_runfile)


with open(multi_prompt_runfilepath, 'w') as f:
    for qid in tqdm(topics):
        # Loop trough queries
        if qid in qrels:
            query = topics[qid]['title']  # Extract the query text from the topics

            # Generate hypothesis documents based on the query
            hypothesis_documents = hyde.generate(query)

            # Encode the query and hypothesis documents into dense vectors
            hyde_vector = hyde.encode(query, hypothesis_documents)

            # Perform a search in the Faiss index using the generated HyDE vector
            hits = hyde.search(hyde_vector, k=1000)

            # Write the top retrieved document results to the output file
            for rank, hit in enumerate(hits, start=1):
                f.write(f'{qid} Q0 {hit.docid} {rank} {hit.score} rank\n')

