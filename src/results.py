import os
import pandas as pd
import argparse

def compare_and_average_metrics(input_directory, output_directory, output_csv='combined_avg_metrics.csv', comparison_csv='comparison_metrics.csv'):
    # Initialize counters for each metric
    metrics_count = {
        'map': {'single_higher': 0, 'multi_higher': 0},
        'ndcg_cut.10': {'single_higher': 0, 'multi_higher': 0},
        'recall.1000': {'single_higher': 0, 'multi_higher': 0}
    }
    
    # Dictionary to store CSV data for averaging
    csv_data = {}

    # Create output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Go through the directories and compare the metrics
    for subdir, dirs, files in os.walk(input_directory):
        # Identify single_prompt and multi_prompt CSV files
        single_prompt_file = None
        multi_prompt_file = None
        for file in files:
            if 'single_prompt' in file and file.endswith('.csv'):
                single_prompt_file = os.path.join(subdir, file)
            elif 'multi_prompt' in file and file.endswith('.csv'):
                multi_prompt_file = os.path.join(subdir, file)

            # Add files to the csv_data dictionary for averaging
            file_key = file.replace(".csv", "")  # Remove the extension to form a key
            file_path = os.path.join(subdir, file)
            if file.endswith('.csv'):
                if file_key not in csv_data:
                    csv_data[file_key] = []
                csv_df = pd.read_csv(file_path)
                csv_data[file_key].append(csv_df)

        # Check if both files were found
        if not single_prompt_file or not multi_prompt_file:
            print(f"Run not finished in directory: {subdir}")
            continue

        # If both files are found, proceed with comparison
        if single_prompt_file and multi_prompt_file:
            # Read both CSV files
            single_prompt_df = pd.read_csv(single_prompt_file)
            multi_prompt_df = pd.read_csv(multi_prompt_file)

            # Compare the metrics
            for metric in metrics_count.keys():
                single_value = single_prompt_df[single_prompt_df['Metric'] == metric]['Value'].values[0]
                multi_value = multi_prompt_df[multi_prompt_df['Metric'] == metric]['Value'].values[0]
                if single_value > multi_value:
                    metrics_count[metric]['single_higher'] += 1
                elif multi_value > single_value:
                    metrics_count[metric]['multi_higher'] += 1

    # After comparison, average the results of the CSV files and write them to output CSV
    combined_dfs = []
    for file_key, dataframes in csv_data.items():
        # Concatenate all dataframes and calculate mean of numerical columns
        combined_df = pd.concat(dataframes).groupby('Metric').mean().reset_index()
        combined_dfs.append(combined_df)

    # Concatenate all averaged DataFrames into one and save as CSV in the results directory
    final_combined_df = pd.concat(combined_dfs).groupby('Metric').mean().reset_index()
    output_file_path = os.path.join(output_directory, output_csv)
    final_combined_df.to_csv(output_file_path, index=False)

    print(f"Comparison and averaged CSV created: {output_file_path}")
    
    # Save comparison results into a CSV
    comparison_results = []
    for metric, comparison in metrics_count.items():
        comparison_results.append({
            'Metric': metric,
            'Single Prompt Higher': comparison['single_higher'],
            'Multi Prompt Higher': comparison['multi_higher']
        })
    comparison_df = pd.DataFrame(comparison_results)
    comparison_output_file = os.path.join(output_directory, comparison_csv)
    comparison_df.to_csv(comparison_output_file, index=False)
    
    print(f"Comparison metrics CSV created: {comparison_output_file}")
    return metrics_count

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Compare and average metrics from CSV files.')
    parser.add_argument('-d', '--directory', required=True, help='Input directory containing the CSV files.')
    parser.add_argument('-r', '--result_dir', required=True, help='Output directory to store the result CSV files.')

    args = parser.parse_args()

    # Execute the function with the provided directories
    result = compare_and_average_metrics(args.directory, args.result_dir)
    print(result)