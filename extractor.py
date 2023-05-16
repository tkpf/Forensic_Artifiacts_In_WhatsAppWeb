

import os
import shutil
import argparse
from helpers import *

out_dir = './output/'
in_dir = './input/'


def copy_files_to_working_directory(src_path, des_path = in_dir):
    '''
    Move metadata .ldb files to specified location and change file extension to allow reading it with python reader object

    src_path:   Path where indexeddb data is stored (e.g. .ldb metadata files)
    des_pah:    Path where the metadata files are stored as textfiles
    ''' 
    # check if folder exists, otherwise create
    if not os.path.isdir(des_path):
        os.mkdir(des_path)
        
    for filename in os.listdir(src_path):
        if filename.endswith('.ldb'):  # change the extension to txt file for further processing
            new_filename = os.path.splitext(filename)[0] + '.txt'
            old_path = os.path.join(src_path, filename)
            new_path = os.path.join(des_path, new_filename)
            shutil.copyfile(old_path, new_path)
            print(f"Copied file {filename} and converted to textfile.")



if __name__ == "__main__":
    # Ausführung des files via python Extractor.py -c copypath -p 1101 -s sortColumn -en NoName NoName2 

    # Create the argument parser
    parser = argparse.ArgumentParser(description='Argument Parser for Extractor')

    # Add the command-line arguments
    parser.add_argument('-p', dest='metadata_filepath', help='metadata file path')
    parser.add_argument('-s', dest='col_to_sort', help='column to sort')
    parser.add_argument('-exn', dest='excluded_names', nargs='+', help='excluded names')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the parsed arguments
    metadata_filepath = args.metadata_filepath
    if args.col_to_sort:
        col_to_sort = args.col_to_sort
    else:
        col_to_sort = 'occ'
    excluded_names = '|'.join(args.excluded_names) if args.excluded_names else ''
    
    ### Argument Parsing finished
    ### make directory, specify patterns

    # check if output folder exists, otherwise create
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    # check if metadata path is specified, if delete old input file
    if metadata_filepath:
        # delete existing output_files
        if not os.path.isdir(in_dir):
                os.mkdir(in_dir)
        else:
            for f in os.listdir(in_dir):
                if not f.endswith(".txt"):
                    continue
                os.remove(os.path.join(in_dir, f))
        copy_files_to_working_directory(metadata_filepath, in_dir)


    no_names = r'Status|Error|Event|Single|Direct|Time|Sent|Update|Obaque|Record|Paused|Dialog|Select|Offset|Sender|Parent|Height|Hverified|Lverified|Connec'
    # Append the excluded_names to 'no_names'
    if excluded_names:
        no_names = no_names + '|' + excluded_names
        print(f"Following strings are not considered as names:\n{no_names}")

    patterns = {
        "name_double_plus" : r'[A-Z][a-z]{2,10}(\x20[A-Z][a-z]{2,10})+',
        "name_single" : r'(?<=[\x01\x14])(?!' + no_names + r')[[A-Z][a-z]{3,10}',
        "number_simple" : r'[0-9]{9,15}', # decrease false positives further by making length dependent on country code e.g. russian numbers are short
        "number_and_name_linked" : r'\x02.{0,100}@(?:s\.whatsapp\.net|c\.us).{0,100}\x02'
    }

    # header to write to file, to allow further processing after pattern extraction
    patterns_header = {
        "name_double_plus" : 'name',
        "name_single" : 'name',
        "number_simple" : 'number',
        "number_and_name_linked" : 'filtered_output_to_link_numbers_and_names'
    }


    # create empty files and write header for further processing
    for pattern in patterns:
        output_file = os.path.join(out_dir, pattern + ".csv")
        write_header_extracted_patterns(output_file, header = patterns_header[pattern])

    ### Preparement finished
    ### Extract patterns

    metadata_files = os.listdir(in_dir)

    for filename in metadata_files:
        if filename.endswith('.txt'):
            input_file = os.path.join(in_dir, filename)
            for pattern in patterns:
                output_file = os.path.join(out_dir, pattern + ".csv")
                extract_patterns(input_file, output_file, patterns[pattern])


    print(f'Pattern extraction complete! Output from {len(patterns)} patterns of {len(metadata_files)} files.')

    ### Extracted patterns
    ### Further evaluate extracted files with the help of helpers.py

    
    evaluated_csv_file = sort_csv_file(add_number_occurences(add_country_codes_to_numbers(extract_linked_number_and_names(extract_non_linked_numbers=True, delete_input_file_afterwards=False))), col_to_sort=col_to_sort)
    occ_in_number_file = sort_csv_file(add_number_occurences(add_country_codes_to_numbers(input_file="output/number_simple.csv", delete_input_file_afterwards=False)), col_to_sort=col_to_sort)

