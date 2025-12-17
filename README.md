# CSV Cleaner & Deduplicator
#### Video Demo: https://youtu.be/GKy8TS287eM
#### Description:

A command-line Python program that validates, cleans, normalizes, deduplicates, and rewrites CSV files.

This program reads an user-specified CSV file, validates that its structure follows specific rules (outlined below), cleans and normalizes row data, removes duplicate rows, and writes the result to a new user-specified CSV file.

Malformed rows are discarded during processing. The program reports how many rows were discarded.

## Usage

python final_project.py input.csv output.csv

- Exactly two user-specified arguments are required
- Both input and output files must have a '.csv' extension (case-insensitive)
- The input file must exist and be readable

## Input CSV Format:

The input CSV must contain a header row with the following four columns:

- id
- name
- age
- birthdate

Header rules:
- Headers are case-insensitive
- Headers must be unique
- Headers cannot be empty

Row rules:
- All fields must be present
- No field may be empty
- Rows with missing or extra fields are discarded

## Data Visualization & Normalization:

Each row is validated and normalized according to the following rules:

### ID:
- Must be a positive integer
- Normalized to a zero-padded three-digit string (e.g. 1 -> 001)

### Age:
- Must be an integer between 1 and 120 (Inclusive)

### Name:
- Must contain exactly a first and last name
- Middle names are not allowed
- Normalized to the format: "Last, First"

### Birthdate:
- Must be in MM/DD/YYYY or MM-DD-YYYY format
- Year must be 1900 or later
- Normalized to ISO format: YYYY-MM-DD

## Deduplication:

After cleaning, duplicate rows are discarded.

Two rows are considered duplicates if the name, age, and birthdate fields match exactly after normalization. The first occurrence of a row is preserved and numbers are reassigned new IDs.

## Output:

The output CSV contains:
- Cleaned and normalized rows
- No duplicate rows
- The same header fields as the input, written in lowercase

If no valid rows remain after cleaning and deduplication, the program exits with an error

## Error Handling:

The program exits with an error if:
- Incorrect number of command-line arguments is provided
- Input or output file is not a CSV
- Input file cannot be read
- The input CSV is empty
- Headers are missing, empty, or duplicated
- No rows remain after cleaning and deduplication

## Testing:

Tests are written using pytest and cover:
- CSV validation
- File handling errors
- Data cleaning and normalization
- Deduplication logic
- Output file writing

Tests use pytest's tmp_path to create temporary files.
