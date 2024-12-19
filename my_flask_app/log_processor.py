import csv
import json
import os
import re
import sqlite3
from typing import Dict, List, Optional, Union

import pandas as pd


def parse_session_info_entry(entry_content: str) -> Dict[str, str]:
    """Parses a SESSION_INFO_NTF style entry that may contain nested structures.

    :param str entry_content: Content of the SESSION_INFO_NTF log entry.
    :returns: A dictionary containing key-value pairs extracted from the log entry.
    :rtype: Dict[str, str]
    """
    entry_content = entry_content.strip("{}").replace("\n", " ")
    kv_dict: Dict[str, str] = {}
    if "[" in entry_content and "]" in entry_content:
        outer_content, inner_content = entry_content.split("[", 1)
        inner_content = inner_content.rsplit("]", 1)[0]
    else:
        outer_content = entry_content
        inner_content = ""

    outer_kv_pairs = re.findall(r'(\w+)=("[^"]*"|[^,\s]+)', outer_content)
    inner_kv_pairs = re.findall(r'(\w+(?:\[\w+\])?)=("[^"]*"|[^,\s]+)', inner_content)

    for key, value in outer_kv_pairs + inner_kv_pairs:
        kv_dict[key] = value.strip('"')

    return kv_dict


def parse_json_blocks(line: str) -> Optional[Union[Dict, List]]:
    """Parses JSON log blocks within a line.

    :param str line: A single line from the log file that may contain JSON data.
    :returns: Parsed JSON data as a dictionary or list, or None if parsing fails.
    :rtype: Optional[Union[Dict, List]]
    """
    try:
        clean_line = re.sub(r"^[^{]*", "", line)
        return json.loads(clean_line)
    except json.JSONDecodeError:
        return None


def process_log_file(log_file: str, csv_file: str) -> None:
    """Process a log file to extract SESSION_INFO_NTF and JSON data into a CSV file.

    :param str log_file: Path to the input log file.
    :param str csv_file: Path to the output CSV file.
    :returns: None
    :rtype: None
    """
    entries: List[Dict] = []
    with open(log_file, "r") as f:
        lines = f.readlines()

    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()

        if line.startswith("SESSION_INFO_NTF:"):
            entry_lines: List[str] = []
            entry_line = line[len("SESSION_INFO_NTF: ") :]
            entry_lines.append(entry_line)
            if "}" not in line:
                idx += 1
                while idx < len(lines):
                    entry_line = lines[idx].strip()
                    entry_lines.append(entry_line)
                    if "}" in entry_line:
                        break
                    idx += 1
            entry_content = " ".join(entry_lines)
            kv_dict = parse_session_info_entry(entry_content)
            entries.append(kv_dict)
            idx += 1
            continue

        if "{" in line and "}" in line:
            parsed_json = parse_json_blocks(line)
            if parsed_json:
                if "results" in parsed_json:
                    for result in parsed_json["results"]:
                        flattened_entry = {
                            "Block": parsed_json.get("Block", None),
                            **result,
                        }
                        entries.append(flattened_entry)
                else:
                    entries.append(parsed_json)

        idx += 1

    if entries:
        all_keys = sorted(set().union(*entries))
        with open(csv_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_keys)
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry)


def create_table_from_csv(csv_file: str, conn: sqlite3.Connection) -> None:
    """Create a table and insert data from a CSV file into an SQLite database.

    :param str csv_file: Path to the CSV file to be processed.
    :param sqlite3.Connection conn: SQLite database connection object.
    :returns: None
    :rtype: None
    """
    table_name = os.path.splitext(os.path.basename(csv_file))[0]
    df = pd.read_csv(csv_file)
    if "D_cm" in df.columns:
        df.rename(columns={"D_cm": "distance[cm]"}, inplace=True)
    df.to_sql(table_name, conn, if_exists="replace", index=False)


def process_csv_files(csv_dir: str, db_file: str) -> None:
    """Process all CSV files in the directory and create corresponding tables in the database.

    :param str csv_dir: Path to the directory containing CSV files.
    :param str db_file: Path to the SQLite database file.
    :returns: None
    :rtype: None
    """
    conn = sqlite3.connect(db_file)
    for csv_file in os.listdir(csv_dir):
        if csv_file.endswith(".csv"):
            csv_path = os.path.join(csv_dir, csv_file)
            create_table_from_csv(csv_path, conn)
    conn.close()


def run_log_processing(
    log_dir: str = "./logs",
    output_dir: str = "./output",
    db_file: str = "./logs_data.db",
) -> bool:
    """Run the entire log processing pipeline.

    :param str log_dir: Directory containing log files.
    :param str output_dir: Directory where output CSV files will be saved.
    :param str db_file: Path to the SQLite database file.
    :returns: True if processing is successful.
    :rtype: bool
    """
    os.makedirs(output_dir, exist_ok=True)

    for log_file in os.listdir(log_dir):
        if log_file.endswith(".log"):
            log_path = os.path.join(log_dir, log_file)
            csv_file_name = os.path.splitext(log_file)[0] + ".csv"
            csv_path = os.path.join(output_dir, csv_file_name)
            process_log_file(log_path, csv_path)

    process_csv_files(output_dir, db_file)
    return True
