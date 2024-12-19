# import re
# import csv
# import os
#
#
# def parse_entry(entry_content):
#     # Remove outer braces and replace newlines with spaces
#     entry_content = entry_content.strip('{}').replace('\n', ' ')
#
#     # Initialize dictionaries
#     kv_dict = {}
#
#     # Split content into outer and inner parts
#     if '[' in entry_content and ']' in entry_content:
#         outer_content, inner_content = entry_content.split('[', 1)
#         inner_content = inner_content.rsplit(']', 1)[0]
#     else:
#         outer_content = entry_content
#         inner_content = ''
#
#     # Parse outer key-value pairs
#     outer_kv_pairs = re.findall(r'(\w+)=("[^"]*"|[^,\s]+)', outer_content)
#     # Parse inner key-value pairs
#     inner_kv_pairs = re.findall(r'(\w+(?:\[\w+\])?)=("[^"]*"|[^,\s]+)', inner_content)
#
#     # Combine all key-value pairs into one dictionary
#     for key, value in outer_kv_pairs + inner_kv_pairs:
#         kv_dict[key] = value.strip('"')
#
#     return kv_dict
#
#
# def process_log_file(log_file, csv_file):
#     entries = []
#     with open(log_file, 'r') as f:
#         lines = f.readlines()
#
#     idx = 0
#     while idx < len(lines):
#         line = lines[idx].strip()
#         if line.startswith('SESSION_INFO_NTF:'):
#             # Start collecting entry lines
#             entry_lines = []
#             # Remove the 'SESSION_INFO_NTF: ' prefix
#             entry_line = line[len('SESSION_INFO_NTF: '):]
#             entry_lines.append(entry_line)
#             # Check if the entry ends on this line
#             if '}' not in line:
#                 idx += 1
#                 while idx < len(lines):
#                     entry_line = lines[idx].strip()
#                     entry_lines.append(entry_line)
#                     if '}' in entry_line:
#                         break
#                     idx += 1
#             # Combine entry lines into one string
#             entry_content = ' '.join(entry_lines)
#             # Parse the entry content
#             kv_dict = parse_entry(entry_content)
#             entries.append(kv_dict)
#         idx += 1
#
#     # Get all unique keys for CSV headers
#     all_keys = set()
#     for entry in entries:
#         all_keys.update(entry.keys())
#     all_keys = sorted(all_keys)
#
#     # Write to CSV file
#     with open(csv_file, 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=all_keys)
#         writer.writeheader()
#         for entry in entries:
#             writer.writerow(entry)
#
#     print(f"Data from {log_file} has been extracted to {csv_file}")
#
#
# def main():
#     log_dir = './logs'  # Directory containing log files
#     output_dir = './output'  # Directory to save CSV files
#
#     # Ensure output directory exists
#     os.makedirs(output_dir, exist_ok=True)
#
#     # Process all log files in the directory
#     for log_file in os.listdir(log_dir):
#         if log_file.endswith('.log'):
#             log_path = os.path.join(log_dir, log_file)
#             csv_file_name = os.path.splitext(log_file)[0] + '.csv'
#             csv_path = os.path.join(output_dir, csv_file_name)
#             process_log_file(log_path, csv_path)
#
#
# if __name__ == "__main__":
#     main()
#
# import os
# import sqlite3
# import pandas as pd
#
#
# def create_table_from_csv(csv_file, conn):
#     """Create a table and insert data from a CSV file into an SQLite database."""
#     # Extract table name from the CSV file name
#     table_name = os.path.splitext(os.path.basename(csv_file))[0]
#
#     # Read CSV into a DataFrame
#     df = pd.read_csv(csv_file)
#
#     # Write the DataFrame to the SQLite database
#     df.to_sql(table_name, conn, if_exists='replace', index=False)
#
#     print(f"Table '{table_name}' created successfully.")
#
#
# def process_csv_files(csv_dir, db_file):
#     """Process all CSV files in a directory and create corresponding tables in a database."""
#     # Connect to the SQLite database (or create it if it doesn't exist)
#     conn = sqlite3.connect(db_file)
#
#     # Process each CSV file in the directory
#     for csv_file in os.listdir(csv_dir):
#         if csv_file.endswith('.csv'):
#             csv_path = os.path.join(csv_dir, csv_file)
#             create_table_from_csv(csv_path, conn)
#
#     # Close the database connection
#     conn.close()
#     print(f"All tables created in database '{db_file}'.")
#
#
# if __name__ == "__main__":
#     csv_directory = './my_flask_app/output'  # Directory containing CSV files
#     database_file = './logs_data.db'  # SQLite database file name
#
#     process_csv_files(csv_directory, database_file)


import os
import re
import json
import csv
import sqlite3
import pandas as pd

def parse_session_info_entry(entry_content):
    """Parses a SESSION_INFO_NTF style entry that may contain nested structures."""
    # Remove outer braces and replace newlines with spaces
    entry_content = entry_content.strip('{}').replace('\n', ' ')

    kv_dict = {}

    # Split content into outer and inner parts if brackets exist
    if '[' in entry_content and ']' in entry_content:
        outer_content, inner_content = entry_content.split('[', 1)
        inner_content = inner_content.rsplit(']', 1)[0]
    else:
        outer_content = entry_content
        inner_content = ''

    # Parse outer key-value pairs
    outer_kv_pairs = re.findall(r'(\w+)=("[^"]*"|[^,\s]+)', outer_content)
    # Parse inner key-value pairs
    inner_kv_pairs = re.findall(r'(\w+(?:\[\w+\])?)=("[^"]*"|[^,\s]+)', inner_content)

    # Combine all key-value pairs into one dictionary
    for key, value in outer_kv_pairs + inner_kv_pairs:
        kv_dict[key] = value.strip('"')

    return kv_dict


def parse_json_blocks(line):
    """Parses JSON log blocks within a line."""
    try:
        # Attempt to isolate the JSON part of the line by removing any prefix up to the first '{'
        clean_line = re.sub(r'^[^{]*', '', line)
        return json.loads(clean_line)
    except json.JSONDecodeError:
        return None


def process_log_file(log_file, csv_file):
    """Process a log file to extract SESSION_INFO_NTF and JSON data into a CSV file."""
    entries = []
    with open(log_file, 'r') as f:
        lines = f.readlines()

    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()

        # Check for SESSION_INFO_NTF (multiline capable)
        if line.startswith('SESSION_INFO_NTF:'):
            # Start collecting entry lines
            entry_lines = []
            # Remove the 'SESSION_INFO_NTF: ' prefix
            entry_line = line[len('SESSION_INFO_NTF: '):]
            entry_lines.append(entry_line)
            # If the entry does not end on this line, continue reading until we find '}'
            if '}' not in line:
                idx += 1
                while idx < len(lines):
                    entry_line = lines[idx].strip()
                    entry_lines.append(entry_line)
                    if '}' in entry_line:
                        break
                    idx += 1
            # Combine entry lines into one string
            entry_content = ' '.join(entry_lines)
            # Parse the SESSION_INFO_NTF entry
            kv_dict = parse_session_info_entry(entry_content)
            entries.append(kv_dict)
            idx += 1
            continue

        # Check for JSON blocks in the line
        if '{' in line and '}' in line:
            parsed_json = parse_json_blocks(line)
            if parsed_json:
                # If 'results' key exists, flatten the results array
                if 'results' in parsed_json:
                    for result in parsed_json['results']:
                        flattened_entry = {'Block': parsed_json.get('Block', None), **result}
                        entries.append(flattened_entry)
                else:
                    entries.append(parsed_json)

        idx += 1

    # Write entries to CSV if any
    if entries:
        # Determine all keys for CSV headers
        all_keys = set().union(*entries)
        all_keys = sorted(all_keys)

        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_keys)
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry)

        print(f"Data from {log_file} has been extracted to {csv_file}")


def create_table_from_csv(csv_file, conn):
    """Create a table and insert data from a CSV file into an SQLite database."""
    # Extract table name from the CSV file name
    table_name = os.path.splitext(os.path.basename(csv_file))[0]

    # Read CSV into a DataFrame
    df = pd.read_csv(csv_file)

    # Rename D_cm to distance[cm] if exists
    if 'D_cm' in df.columns:
        df.rename(columns={'D_cm': 'distance[cm]'}, inplace=True)

    # Write the DataFrame to the SQLite database
    df.to_sql(table_name, conn, if_exists='replace', index=False)

    print(f"Table '{table_name}' created successfully.")


def process_csv_files(csv_dir, db_file):
    """Process all CSV files in the directory and create corresponding tables in the database."""
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file)

    # Process each CSV file in the directory
    for csv_file in os.listdir(csv_dir):
        if csv_file.endswith('.csv'):
            csv_path = os.path.join(csv_dir, csv_file)
            create_table_from_csv(csv_path, conn)

    # Close the database connection
    conn.close()
    print(f"All tables created in database '{db_file}'.")


def main():
    log_dir = './logs'    # Directory containing log files
    output_dir = './output'  # Directory to save CSV files
    db_file = './logs_data.db'  # SQLite database file name

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process all log files in the directory
    for log_file in os.listdir(log_dir):
        if log_file.endswith('.log'):
            log_path = os.path.join(log_dir, log_file)
            csv_file_name = os.path.splitext(log_file)[0] + '.csv'
            csv_path = os.path.join(output_dir, csv_file_name)
            process_log_file(log_path, csv_path)

    # After all CSVs are generated, process them into the SQLite database
    process_csv_files(output_dir, db_file)


if __name__ == "__main__":
    main()
