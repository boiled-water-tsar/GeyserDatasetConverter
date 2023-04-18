import csv
import math
import time
import os
from decimal import Decimal

import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter


def load_csv(filename: str) -> list:
    with open(filename, newline='') as file:
        reader = csv.reader(file, delimiter=",", quotechar='"')
        return list(reader)


def parse_csv_input(loaded_csv: list[list[str]]) -> dict[str, list[list[int | float]] | list[list[str]]]:
    _parsed = []
    _errors = []

    for entry in loaded_csv[1:]:

        if all(not s or s.isspace() for s in entry):
            continue

        parsed_entry = []

        try:
            parsed_decimal = Decimal(entry[1])
            if math.isnan(parsed_decimal):
                _errors.append(entry)
                continue

            parsed_entry.append(int(entry[0]))
            parsed_entry.append(parsed_decimal)
            parsed_entry.append(int(entry[2]))

            _parsed.append(parsed_entry)

        except ValueError:
            _errors.append(entry)
            continue

    return {"parsed": _parsed, "errors": _errors}


def serialize_avro(filename: str, schema_name: str, items: dict[str, list[list[int | float]] | list[list[str]]]) -> None:
    schema = avro.schema.parse(open(schema_name).read())
    writer = DataFileWriter(open(filename, "wb"), DatumWriter(), schema)

    for entry in items["parsed"]:
        writer.append({"index": entry[0],
                       "eruption_length_mins": entry[1],
                       "eruption_wait_mins": entry[2],
                       "error": False})

    for entry in items["errors"]:
        writer.append({"index": entry[0],
                       "eruption_length_mins": entry[1],
                       "eruption_wait_mins": entry[2],
                       "error": True})

    writer.close()


def read_avro(filename: str):
    reader = DataFileReader(open(filename, "rb"), DatumReader())
    reader_result = list(reader)
    reader.close()
    return reader_result


def end_message():
    print("\n* Thank you for using the AVRO Geyser Data Experience! *")


if __name__ == "__main__":
    width = 50
    welcome_message = "Welcome to the AVRO Geyser Data Experience!"
    centered = ' '.join(welcome_message).center(width, ' ')
    print("* " * (len(welcome_message) + 3))
    print(f"*  {centered}  *")
    print("* " * (len(welcome_message) + 3))
    print("*")
    print("*")

    while True:
        csv_filepath = input("* Enter the name or location of your unfaithful dataset. Default: unfaithful.csv *\n") or "unfaithful.csv"
        if os.path.isfile(csv_filepath):
            break
        print(f"* Path {csv_filepath} is invalid")
    time.sleep(0.1)

    while True:
        schema_filepath = input("* Enter the name or location of your schema file. Default: unfaithful.avsc *\n") or "unfaithful.avsc"
        if os.path.isfile(schema_filepath):
            break
        print(f"* Path {schema_filepath} is invalid")
    time.sleep(0.1)

    out_filepath = input("* Enter the name or location of your desired output file. Default: unfaithful.avro *\n") or "unfaithful.avro"

    loaded = load_csv(csv_filepath)
    parsed = parse_csv_input(loaded)

    serialize_avro(out_filepath, schema_filepath, parsed)

    while True:
        print_file = input("* Do you wish to print the [F]irst five, [A]ll or [N]o entries of the generated file? Default: [A]ll\n") or "A"
        print_file = print_file.lower()

        if print_file == "f":
            for item in read_avro(out_filepath)[:5]:
                print(item)
            end_message()
            break
        elif print_file == "a":
            for item in read_avro(out_filepath):
                print(item)
            end_message()
            break
        elif print_file == "n":
            end_message()
            break
        else:
            print("* Entered value is not valid for print options.")
