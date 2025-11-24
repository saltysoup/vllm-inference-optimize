# This script parses local vllm server logs to calculate the average draft acceptance rate and mean acceptance length to identify optimal k value for speculative decoding config tuning

import re
import concurrent.futures
import sys # Import sys for handling potential file errors
import argparse # Import argparse for command-line arguments

def extract_metrics(filename):
    """Extracts 'Mean acceptance length' and 'Avg Draft acceptance rate' from a log file.
    
    Args:
        filename (str): The name of the log file (e.g., 'serve.txt').
    
    Returns:
        tuple: (filename, total_count, average_length, average_rate)
               Returns (filename, 0, 0, 0) on file not found or no matches.
    """

    total_count = 0
    total_length = 0
    total_rate = 0.0

    try:
        with open(filename, 'r') as file:
            for line in file:
                # Improved regex pattern to handle different log formats and capture the needed values.
                match = re.search(r"Mean acceptance length:\s*(\d+\.\d+).*?Avg Draft acceptance rate:\s*(\d+\.\d+)%", line)

                if match:
                    total_count += 1
                    length = float(match.group(1))
                    rate = float(match.group(2)) / 100.0  # Convert percentage to decimal

                    total_length += length
                    total_rate += rate
    
    except FileNotFoundError:
        print(f"Error: File not found '{filename}'", file=sys.stderr)
        return filename, 0, 0, 0
    except Exception as e:
        print(f"Error processing file '{filename}': {e}", file=sys.stderr)
        return filename, 0, 0, 0

    if total_count == 0:
        # Return filename so we know which file had no data
        return filename, 0, 0, 0
    else:
        average_length = total_length / total_count
        average_rate = total_rate / total_count
        # Return filename for clarity in results
        return filename, total_count, average_length, average_rate

def main():
    """
    Main function to process files in parallel and aggregate results.
    """
    # --- Set up command-line argument parsing ---
    parser = argparse.ArgumentParser(
        description="Extracts metrics from log files in parallel."
    )
    parser.add_argument(
        "--files",
        type=str,
        required=True,
        help="A comma-separated list of log file names (e.g., 'serve.txt,serve2.txt')"
    )
    
    args = parser.parse_args()
    
    # Split the comma-separated string into a list of files
    files_to_process = [file.strip() for file in args.files.split(',') if file.strip()]
    
    if not files_to_process:
        print("Error: No valid files provided. Please use the --files argument with comma-separated names.", file=sys.stderr)
        sys.exit(1)

    combined_count = 0
    total_weighted_length = 0
    total_weighted_rate = 0

    print(f"Starting parallel processing for {len(files_to_process)} files...")

    # Use ProcessPoolExecutor to run tasks on multiple CPU cores
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # map applies the extract_metrics function to each item in files_to_process
        # The results will be returned in the order the files were submitted
        results = list(executor.map(extract_metrics, files_to_process))

    print("\n--- Individual File Results ---")
    # results is a list of tuples: [(filename, count, length, rate), ...]
    for filename, count, length, rate in results:
        if count > 0:
            print(f"[{filename}] Found {count} entries. Avg Length: {length:.2f}, Avg Rate: {rate*100:.2f}%")
        else:
            print(f"[{filename}] No data found or file error.")
        
        # Aggregate results for combined average
        combined_count += count
        total_weighted_length += length * count
        total_weighted_rate += rate * count

    # Calculate the final combined results
    if combined_count > 0:
        combined_length = total_weighted_length / combined_count
        combined_rate = total_weighted_rate / combined_count
    else:
        combined_length = 0
        combined_rate = 0

    print("\n--- Combined Results ---")
    print(f"Total count from all files: {combined_count}")
    print(f"Overall Average Mean acceptance length: {combined_length:.2f}")
    print(f"Overall Average Avg Draft acceptance rate: {combined_rate*100:.2f}%")

# --- Guard for multiprocessing ---
# This is essential for ProcessPoolExecutor to work correctly on
# platforms like Windows.
if __name__ == "__main__":
    main()