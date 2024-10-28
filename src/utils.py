import os
import re

def evaluate_metrics(result_file, topics_name='dl19-passage'):
    """
    Function to evaluate retrieval performance using TREC standards and return the results as a list of tuples.

    Args:
        run_directory (str): Directory containing the run files.
        result_file (str): File containing the results to be evaluated.
        topics_name (str): Name of the evaluation topic set. Default is 'dl19-passage'.

    Returns:
        list: A list of tuples containing the metric name and its corresponding value.
    """
    evaluation_metrics = [
        ('map', result_file),  # Mean Average Precision
        ('ndcg_cut.10', result_file),  # Normalized Discounted Cumulative Gain at 10
        ('recall.1000', result_file)  # Recall at 1000
    ]

    results = []  # List to store tuples (metric_name, value)

    for metric, result_file in evaluation_metrics:
        

        # Run the trec_eval command and capture the output
        command = f'python -m pyserini.eval.trec_eval -c -l 2 -m {metric} {topics_name} {result_file}'
        stream = os.popen(command)
        output = stream.read()

        # Parse the output to extract the value of the metric
        match = re.search(rf'{metric}\s+all\s+([0-9.]+)', output)
        if match:
            value = float(match.group(1))
            results.append((metric, value))  # Append the result as a tuple (metric_name, value)
        else:
            print(f"Error parsing result for {metric}")

    return results


def replace_spaces_with_underscores(sentence):
    """
    Function that replaces spaces with _
    """
    return sentence.replace(" ", "_")