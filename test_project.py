from final_project import is_csv, validate_csv, read_csv, clean_csv, deduplicate_csv, write_csv
import pytest
import csv

def test_is_csv():

    assert is_csv("file.csv") == True
    assert is_csv("file.CSV") == True
    assert is_csv("file.txt") == False
    assert is_csv("csv") == False


def test_validate_csv(tmp_path):

    # Valid CSV
    file_path1 = tmp_path / "isFound.csv"
    file_path1.touch()
    assert validate_csv(str(file_path1)) == True


    # Invalid CSV
    file_path2 = tmp_path / "isNotFound.csv"
    assert validate_csv(str(file_path2)) == False

def test_read_csv(tmp_path):

    # Empty CSV
    with pytest.raises(SystemExit):
        file_path1 = tmp_path / "empty.csv"
        file_path1.touch()
        file_path1.write_text("")

        read_csv(file_path1)


    # CSV with empty headers
    with pytest.raises(SystemExit):
        file_path2 = tmp_path / "emptyheader.csv"
        file_path2.touch()
        file_path2.write_text(
            "header1,header2,,header4\n"
            "value1,value2,value3,value4\n"
        )

        read_csv(file_path2)


    # CSV with duplicate headers
    with pytest.raises(SystemExit):
        file_path3 = tmp_path / "duplicateheader.csv"
        file_path3.touch()
        file_path3.write_text(
            "header1,header2,header1,header4\n"
            "value1,value2,value3,value4\n"
        )

        read_csv(file_path3)


    # Valid CSV
    file_path4 = tmp_path / "valid.csv"
    file_path4.touch()
    file_path4.write_text(
        "header1,header2,header3,header4\n"
        "value1,value2,value3,value4\n"
    )

    contents, malformed_rows_count = read_csv(file_path4)

    assert contents == [
        {"header1": "value1", "header2": "value2",
         "header3": "value3", "header4": "value4"
        }
    ]
    assert malformed_rows_count == 0


    # Valid CSV with a missing value
    file_path5 = tmp_path / "missingValue.csv"
    file_path5.touch()
    file_path5.write_text(
        "header1,header2,header3,header4\n"
        "value1,value2,value3,value4\n"
        "value5,value6,,value8"
    )

    contents, malformed_rows_count = read_csv(file_path5)

    assert contents == [
        {"header1": "value1", "header2": "value2",
         "header3": "value3", "header4": "value4"
        }
    ]
    assert malformed_rows_count == 1


    # Valid CSV with an extra columns
    file_path6 = tmp_path / "extraColumn.csv"
    file_path6.touch()
    file_path6.write_text(
        "header1,header2,header3,header4\n"
        "value1,value2,value3,value4\n"
        "value5,value6,value7,value8,?value9?"
    )

    contents, malformed_rows_count = read_csv(file_path6)

    assert contents == [
        {"header1": "value1", "header2": "value2",
         "header3": "value3", "header4": "value4"
        }
    ]
    assert malformed_rows_count == 1


    # Valid CSV with header whitespace
    file_path7 = tmp_path / "headerWhitespace.csv"
    file_path7.touch()
    file_path7.write_text(
        "  header1  ,  header2  ,  header3  ,  header4  \n"
        "value1,value2,value3,value4\n"
    )

    contents, malformed_row_count = read_csv(file_path7)

    assert contents == [
        {"header1": "value1", "header2": "value2",
         "header3": "value3", "header4": "value4"
        }
    ]
    assert malformed_row_count == 0


def test_clean_csv(tmp_path):

    # CSV with single digit IDs
    contents = [
        {"id": "1", "name": "Morgan, Alex", "age": "29", "birthdate": "03/14/1996"},
        {"id": "002", "name": "Patel, Jamie", "age": "41", "birthdate": "11/02/1984"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"}
    ]
    assert malformed_row_count == 0


    # CSV with letters in IDs
    contents = [
        {"id": "a001", "name": "Morgan, Alex", "age": "29", "birthdate": "03/14/1996"},
        {"id": "002a", "name": "Patel, Jamie", "age": "41", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 2

    # CSV with names formatted as "First Last"
    contents = [
        {"id": "001", "name": "Alex Morgan", "age": "29", "birthdate": "03/14/1996"},
        {"id": "002", "name": "Jamie Patel", "age": "41", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}

    ]
    assert malformed_row_count == 0

    # CSV with names formatted as "Last, First"
    contents = [
        {"id": "001", "name": "Morgan, Alex", "age": "29", "birthdate": "03/14/1996"},
        {"id": "002", "name": "Patel, Jamie", "age": "41", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Chris Nguyen", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 0

    # CSV with middle names in name
    contents = [
        {"id": "001", "name": "Alex J. Morgan", "age": "29", "birthdate": "03/14/1996"},
        {"id": "002", "name": "Patel, Jamie D. ", "age": "41", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 2

    # CSV with whitespace in names
    contents = [
        {"id": "001", "name": "  Alex   Morgan  ", "age": "29", "birthdate": "03/14/1996"},
        {"id": "002", "name": "  Patel,   Jamie  ", "age": "41", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 0

    # CSV with irregular capitalization in names
    contents = [
        {"id": "001", "name": "AlEX mOrGaN", "age": "29", "birthdate": "03/14/1996"},
        {"id": "002", "name": "pATeL, jAMie", "age": "41", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 0

    # CSV with letters in age
    contents = [
        {"id": "001", "name": "  Alex   Morgan  ", "age": "a29", "birthdate": "03/14/1996"},
        {"id": "002", "name": "  Patel,   Jamie  ", "age": "a41", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 2

    # CSV with ages over 120 and below 1
    contents = [
        {"id": "001", "name": "  Alex   Morgan  ", "age": "121", "birthdate": "03/14/1996"},
        {"id": "002", "name": "  Patel,   Jamie  ", "age": "0", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 2

    # CSV with negative ages
    contents = [
        {"id": "001", "name": "  Alex   Morgan  ", "age": "-29", "birthdate": "03/14/1996"},
        {"id": "002", "name": "  Patel,   Jamie  ", "age": "-41", "birthdate": "11/02/1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 2

    # CSV with invalid birthdate format "YYYY/MM/DD"
    contents = [
        {"id": "001", "name": "  Alex   Morgan  ", "age": "29", "birthdate": "1996/03/14"},
        {"id": "002", "name": "  Patel,   Jamie  ", "age": "41", "birthdate": "1984/02/11"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 2

    # CSV with birthdates with neither hyphens (-) or slahes (/)
    contents = [
        {"id": "001", "name": "  Alex   Morgan  ", "age": "29", "birthdate": "03.14.1996"},
        {"id": "002", "name": "  Patel,   Jamie  ", "age": "41", "birthdate": "11_02_1984"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 2

    # CSV with birthdates before 1900
    contents = [
        {"id": "001", "name": "  Alex   Morgan  ", "age": "29", "birthdate": "03/14/1899"},
        {"id": "002", "name": "  Patel,   Jamie  ", "age": "41", "birthdate": "11/02/1000"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "07/19/2003"}
    ]

    clean_contents, malformed_row_count = clean_csv(contents)

    assert clean_contents == [
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]
    assert malformed_row_count == 2


def test_deduplicate_csv():

    # CSV with one duplicate
    clean_contents = [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"},
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"}
    ]
    deduplicated_contents, duplicate_row_count = deduplicate_csv(clean_contents)

    assert deduplicated_contents == [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"},
    ]
    assert duplicate_row_count == 1

    # CSV with multiple duplicates
    clean_contents = [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"},
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"},
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "004", "name": "Garcia, Elena", "age": 35, "birthdate": "1989-06-01"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
    ]

    deduplicated_contents, duplicate_row_count = deduplicate_csv(clean_contents)

    assert deduplicated_contents == [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"},
        {"id": "004", "name": "Garcia, Elena", "age": 35, "birthdate": "1989-06-01"},
    ]
    assert duplicate_row_count == 4


def test_write_csv(tmp_path):

    # Valid CSV
    file_path1 = tmp_path / "VALID.csv"

    deduplicated_contents = [
        {"id": "001", "name": "Morgan, Alex", "age": 29, "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": 41, "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": 22, "birthdate": "2003-07-19"}
    ]

    write_csv(deduplicated_contents, file_path1)

    assert file_path1.exists()

    with open(file_path1, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows == [
        {"id": "001", "name": "Morgan, Alex", "age": "29", "birthdate": "1996-03-14"},
        {"id": "002", "name": "Patel, Jamie", "age": "41", "birthdate": "1984-11-02"},
        {"id": "003", "name": "Nguyen, Chris", "age": "22", "birthdate": "2003-07-19"}
    ]

    # CSV with no rows left
    file_path2 = tmp_path / "noRowsLeft.csv"

    deduplicated_contents = []

    with pytest.raises(SystemExit):
        write_csv(deduplicated_contents, file_path2)

    assert not file_path2.exists()

    # CSV with only headers left
    file_path3 = tmp_path / "onylHeadersLeft.csv"

    deduplicated_contents = []

    with pytest.raises(SystemExit):
        write_csv(deduplicated_contents, file_path3)

    assert not file_path3.exists()
