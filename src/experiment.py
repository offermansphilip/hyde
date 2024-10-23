import os
import json
import csv
from tqdm import tqdm
import argparse
from pyserini.search import FaissSearcher, LuceneSearcher
from pyserini.search.faiss import AutoQueryEncoder
from pyserini.search import get_topics, get_qrels

# Import the classes from your provided module for generating and handling prompts
from hyde import OllamaGenerator, Promptor, HyDE, MultiPromptHyDE

# Import evaluation function
from utils import evaluate_metrics

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run MultiPromptHyDE with specified model, encoder, and dataset.")
    
    # Add arguments for configuration
    parser.add_argument('--model_name', type=str, default='llama3.1', help="Name of the text generation model to be used.")
    parser.add_argument('--encoder', type=str, default='facebook/contriever', help="Name of the query encoder model.")
    parser.add_argument('--index_path', type=str, default='./src/contriever_msmarco_index/', help="Path to the Faiss index.")
    parser.add_argument('--prebuilt_index', type=str, default='msmarco-v1-passage', help="Prebuilt Lucene index for passage retrieval.")
    parser.add_argument('--run_directory', type=str, default='./runs/', help="Directory to store the retrieval results.")
    parser.add_argument('--topics_name', type=str, default='dl19-passage', help="Name of the evaluation topic set.")
    parser.add_argument('--job_number', type=int, default=0, help="Job number.") 
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Initialize the query encoder
    query_encoder = AutoQueryEncoder(encoder_dir=args.encoder, pooling='mean')

    # Create a FaissSearcher for dense vector search over the Faiss index
    searcher = FaissSearcher(args.index_path, query_encoder)

    # Load a pre-built Lucene index for corpus-based retrieval
    corpus = LuceneSearcher.from_prebuilt_index(args.prebuilt_index)

    # Load the topics (queries) and the corresponding qrels (ground truth relevance judgments)
    topics = get_topics(args.topics_name)
    qrels = get_qrels(args.topics_name)

    # Initialize the Ollama-based text generator using the specified model
    generator = OllamaGenerator(model_name=args.model_name)

    print("___SINGLE_PROMPT_HYDE____")

    # Create a Promptor object for generating web search prompts
    promptor = Promptor(task='web search')

    # Initialize the HyDE model for generating hypotheses and performing retrieval
    hyde = HyDE(promptor=promptor, generator=generator, encoder=query_encoder, searcher=searcher)

    # Set filenames
    trec_file = 'single_prompt-hyde-dl19-contriever-llama3.1-top1000-8rep-trec'
    hypothetical_documents_file = 'single_prompt-hyde-dl19-contriever-llama3.1-top1000-8rep-hyd.json'
    output_csv_file = 'single_prompt-hyde-dl19-contriever-llama3.1-top1000-8rep-output.csv'

    # Define the filepaths
    trec_filepath = os.path.join(args.run_directory, trec_file)
    hypothetical_documents_filepath = os.path.join(args.run_directory, hypothetical_documents_file) 
    output_csv_filepath = os.path.join(args.run_directory, output_csv_file)

    # Open the output file for writing retrieval results
    with open(trec_filepath, 'w') as f:
        for qid in tqdm(topics):
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
                
                # Write the query and hypothesis_documents to the JSON file incrementally
                with open(hypothetical_documents_filepath, 'a') as hypthetical_documents:
                    json.dump({
                        'query_id': qid,
                        'query': query,
                        'hypothesis_documents': hypothesis_documents
                    }, hypthetical_documents)
                    hypthetical_documents.write('\n')  # Add a newline after each JSON object for separation

    # Example usage for evaluating metrics
    evaluation_results = evaluate_metrics(trec_filepath)

    # Write the evaluation results to the CSV file
    with open(output_csv_filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
    
        # Write header (optional)
        writer.writerow(['Metric', 'Value'])
    
        # Write the rows (each metric and its value)
        writer.writerows(evaluation_results)


    print("___MULTI_PROMPT_HYDE____")

    # Create a Promptor object for generating web search prompts
    promptor1 = Promptor(task='web search')
    promptor2 = Promptor(task='web search expert')
    promptor3 = Promptor(task='web search novice')
    promptor4 = Promptor(task='web search intermediate')

    # Initialize the HyDE model for generating hypotheses and performing retrieval
    hyde = MultiPromptHyDE(promptor1=promptor1, promptor2=promptor2, promptor3=promptor3, promptor4=promptor4, generator=generator, encoder=query_encoder, searcher=searcher)

    # Set filenames
    trec_file = 'multi_prompt-hyde-dl19-contriever-llama3.1-top1000-8rep-trec'
    hypothetical_documents_file = 'multi_prompt-hyde-dl19-contriever-llama3.1-top1000-8rep-hyd.json'
    output_csv_file = 'multi_prompt-hyde-dl19-contriever-llama3.1-top1000-8rep-output.csv'

    # Define the filepaths
    trec_filepath = os.path.join(args.run_directory, trec_file)
    hypothetical_documents_filepath = os.path.join(args.run_directory, hypothetical_documents_file) 
    output_csv_filepath = os.path.join(args.run_directory, output_csv_file)

    # Open the output file for writing retrieval results
    with open(trec_filepath, 'w') as f:
        for qid in tqdm(topics):
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
                
                # Write the query and hypothesis_documents to the JSON file incrementally
                with open(hypothetical_documents_filepath, 'a') as hypthetical_documents:
                    json.dump({
                        'query_id': qid,
                        'query': query,
                        'hypothesis_documents': hypothesis_documents
                    }, hypthetical_documents)
                    hypthetical_documents.write('\n')  # Add a newline after each JSON object for separation

    # Example usage for evaluating metrics
    evaluation_results = evaluate_metrics(trec_filepath)

    # Write the evaluation results to the CSV file
    with open(output_csv_filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
    
        # Write header (optional)
        writer.writerow(['Metric', 'Value'])
    
        # Write the rows (each metric and its value)
        writer.writerows(evaluation_results)

   

if __name__ == "__main__":
    main()