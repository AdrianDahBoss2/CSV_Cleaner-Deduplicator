import csv
import sys
import re

def main():

    """
    Orchestrates CSV validation, cleaning, deduplication, and writing.

    Exits the program if:
        - If there is not exactly two user-specified command-line arguments
        - Input or output file is not a CSV
        - Input file cannot be read

    Prints the number of discarded rows, if any.
    """

    if len(sys.argv) > 3:
        sys.exit("Too many arguments")
    elif len(sys.argv) < 3:
        sys.exit("Too few arguments")

    input_file: str = sys.argv[1]
    output_file: str = sys.argv[2]

    if not is_csv(input_file):
        sys.exit(f"File '{input_file}' is not a CSV")
    elif not is_csv(output_file):
        sys.exit(f"File '{output_file}' is not a CSV")

    if not validate_csv(input_file):
        sys.exit(f"File '{input_file}' was not found")

    contents, malformed_rows_count = read_csv(input_file)
    clean_contents, unclean_rows_count = clean_csv(contents)
    deduplicated_rows, duplicate_rows_count = deduplicate_csv(clean_contents)
    write_csv(deduplicated_rows, output_file)

    # Displays how many rows were dropped, not how, to keep simple for longer CSVs
    if malformed_rows_count or unclean_rows_count or duplicate_rows_count:
        print(f"{malformed_rows_count + unclean_rows_count + duplicate_rows_count} discarded row(s)")


def is_csv(file_name: str) -> bool:

    """
    Returns True if the given filename ends in ".csv".

    This does not verify file existence or contents.

    :param file_name: The name of file to check
    :type file_name: str
    :return: True if file_name ends with csv otherwise returns false
    :rtype: bool
    """

    return file_name.lower().endswith(".csv")


def validate_csv(file_name: str) -> bool:

    """
    Returns True if the file exists and can be opened for reading.

    :param file_name: The name of file to attempt to read
    :type file_name: str
    :rtype: bool
    """

    try:
        with open(file_name, 'r', newline="") as f:
            return True

    except FileNotFoundError:
        return False


def read_csv(file: str) -> tuple:

    """
    Reads a CSV file and returns validated and structured row data.

    The first non-empty row is considered as the header row. Headers are:
        - Stripped of whitespace
        - Converted to lowercase
        - Must be non-empty and unique

    Rows are considered malformed and are discarded if they:
        - Have missing fields or extra fields
        - Contain empty values

    :param file: Name of file to read
    :type file: str
    :raise SystemExit:
        - If the file is empty
        - If a header is empty
        - If there is a duplicate header
    :return:
        - A list of dictionaries mapping headers to row values.
        - Count of discarded rows
    :rtype:
        - list
        - int
    """

    contents = []
    headers = []

    try:
        # Scans file and assigns first valid line as headers otherwise the file is empty
        with open(file, 'r', newline="") as f:
            lines = csv.reader(f)
            for row in lines:
                headers = row
                if headers:
                    break
            if headers == []:
                raise ValueError("File is empty")


            # Cleans headers. Exits if header is empty or a duplicate. And displays invalid header location(s) if found
            clean_headers = []
            empty_header_locations = []
            duplicate_headers = []
            duplicate_header_locations = []

            for i, header in enumerate(headers, start=1):
                clean_header = header.strip().lower()
                if clean_header == "":
                    empty_header_locations.append(i)
                elif clean_header in clean_headers:
                    duplicate_header_locations.append(i)
                    duplicate_headers.append(header)
                else:
                    clean_headers.append(clean_header)

            if empty_header_locations:
                raise ValueError(f"Empty header(s) found at position(s) {empty_header_locations}")
            elif duplicate_headers:
                raise ValueError(f"Duplicate header(s) '{duplicate_headers}' found at position(s) {duplicate_header_locations} respectively")


            # Malformed rows are rows with empty values or rows with more than columns than headers
            malformed_contents = []

            for row in lines:
                if not len(row) == len(clean_headers):
                    malformed_contents.append(row)
                elif any(data.strip() == "" for data in row):
                    malformed_contents.append(row)
                else:
                    contents.append(dict(zip(clean_headers, row)))

            return contents, len(malformed_contents)

    except ValueError as error:
        sys.exit(f"Error reading file: {error}")


def clean_csv(contents: list) -> tuple:

    """
    Further validates and normalizes CSV row data.

    === VALIDATION RULES ===
    - IDs cannot not contain letters
    - Age must be an integer between 1 and 120
    - Names must contain exactly first and last names
    - Birthdates must be between 1900 - 2099 and in MM/DD/YYYY or MM-DD-YYYY format

    === NORMALIZATION RULES ===
    - ID's are zero padded to three digits
    - Ages are converted to integers
    - Names are normalized to "Last, First"
    - Birthdates are normalized to ISO format "YYYY-MM-DD"

    Rows violating any rule are discarded

    :param contents: List of dictionaries from read_csv to clean
    :type contents: list
    :return:
        - List of further validated and normalized dictionaries
        - Count of discarded rows
    :rtype:
        - list
        - int
    """

    clean_contents = []
    unclean_rows = []

    for row in contents:
        try:
            clean_id = int(row["id"].strip()) # Checks that IDs have no letters
            clean_id = row["id"].strip().zfill(3) # IDs are strings and are 3 digits long
            clean_age = int(row["age"].strip())
            if clean_age < 1: # Ages zero or below are NOT allowed
                raise ValueError
            elif clean_age > 120: # Ages above 120 years are NOT allowed
                raise ValueError

            # Names with middle names are NOT allowed
            if "," in row["name"]: # Detects names formatted as "Last, First"
                last, first = row["name"].replace(",", "").split()
                clean_name = f"{last}, {first}".title()
            else:
                first, last = row["name"].split()
                clean_name = f"{last}, {first}".title()

            if matches := re.search(r"^(0?[1-9]|1[0-2])[/-](0?[1-9]|[12][0-9]|3[01])[/-](19\d{2}|20\d{2})$", row["birthdate"].strip()):
                #                         ^ Month ^               ^ Day ^                 ^ Year ^
                # Rejects birthdates BEFORE 1900. Accepts birthdates formatted as "MM/DD/YYYY" or "MM-DD-YYYY"
                clean_birthdate = f"{matches[3]}-{matches[1]:02}-{matches[2]:02}" # Formats using ISO: "YYYY/MM/DD"
            else:
                raise ValueError

            clean_contents.append({"id": clean_id, "name": clean_name, "age": clean_age, "birthdate": clean_birthdate})

        except ValueError:
            unclean_rows.append(row)

    return clean_contents, len(unclean_rows)


def deduplicate_csv(clean_contents: list) -> tuple:

    """
    Removes duplicate rows from CSV file.

    Two rows are duplicates if name, age, and birthdate key-value pairs match exactly.
    Original row order is preserved.

    :param clean_contents: List of dictionaries from clean_csv to deduplicate
    :type clean_contents: list
    :return:
        1. A list of deduplicated dictionaries
        2. Count of discarded rows
    :rtype:
        1. list
        2. int
    """

    deduplicated_contents = []
    malformed_rows = []
    seen_people = set()

    for row in clean_contents:
        person_key = (row["name"], row["age"], row["birthdate"])

        if person_key not in seen_people:
            seen_people.add(person_key)
            deduplicated_contents.append(row)
        else:
            malformed_rows.append(person_key)

    for index, row in enumerate(deduplicated_contents, start=1):
        row["id"] = f"{index:03}"

    return deduplicated_contents, len(malformed_rows)


def write_csv(deduplicated_contents: list, output_file: str):

    """
    Writes cleaned and deduplicated CSV data to an user-specified output file.

    :param deduplicated_contents: List of dictionaries from deduplicate_csv to write
    :param output_file: Name of the file to write clean and deduplicated to
    :type deduplicated_contents: list
    :type output_file: str
    :raise SystemExit:
        - ValueError: Error occurred while writing output file
        - IndexError: No rows left to write after clean_csv and deduplicate_csv
    """
    try:
        keys = deduplicated_contents[0].keys()
        headers = []
        for key in keys:
            headers.append(key)

        with open(output_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=headers)

            writer.writeheader()
            for row in deduplicated_contents:
                writer.writerow(row)

    except ValueError:
        sys.exit(f"Error writing to file '{output_file}'")
    except IndexError:
        sys.exit(f"Error writing to file '{output_file}', no rows left after cleaning and deduplicating")


if __name__ == "__main__":
    main()
