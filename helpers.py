'''
Helper functions to extract useful information (e.g. contact names and numbers) from .ldb database file created by WhatsAppWeb

Helper functions include:
    - extract_patterns():                   Extract given patterns from a specified file.
    - extract_linked_numbers_and_names():   Link numbers and names given a pre-filtered textfile of the original database files.
    - add_country_codes_to_numbers():       Adds country codes to a given csv file as new column.
    - add_number_occurences():              Counts dublicates of number entries and append the information into a new column of the given csv file.
    - sort_csv_file():                      Sorts the given csv file with respect to the specified column.

'''


import re
import csv
import os


out_dir = './output/'


def write_header_extracted_patterns(output_file, header=None):
    with open(output_file, 'w', encoding='ISO-8859-1') as output_f:
        # Write the header to the file
        output_f.write(header + "\n")

def extract_patterns(input_file, output_file, pattern, replace00 = True):
    '''
    Function to extract a given pattern from the input_file.
    '''
    with open(input_file, 'r', encoding='ISO-8859-1') as input_f:
        with open(output_file, 'a', encoding='ISO-8859-1') as output_f:
            # iterate over findings and write them to output_file
            for line in input_f:
                # delete 0x00 bytes from file 
                if replace00:
                    line = line.replace('\x00', '')
                itermatch = re.finditer(pattern, line)
                eof = False
                while not eof:
                    curmatch = ""
                    try:
                        curmatch = next(itermatch)
                        output_f.write(curmatch.group(0) + '\n')
                    except:
                        eof = True

def extract_linked_number_and_names(input_file = out_dir + 'number_and_name_linked.csv', output_file = out_dir + 'number_and_contacts.csv', delete_input_file_afterwards = True, extract_non_linked_numbers = False):
    '''
    Function to extract information from pre-filtered file to link numbers and contact names.

    input_file: Filepath to file with pre-extracted lines promising to contain number-name information. File is ideally produced by function extract_patterns with respect to 'number_and_name_linked'-pattern
    '''
    
    # Define the pattern for matching numbers and names
    number_pattern = r"\d{10,16}@(?:s\.whatsapp\.net|c\.us)"
    name_pattern = r"(?<=name..)[A-Z][a-z]+(\s([A-Z][a-z]+)*)?"
    no_contact_pattern = r"pushname" # 'pushname' indicates that the number is not in the chat owners contacts, but the whatsapp name of the number will be displayed.
    # Open the input text file for reading
    with open(input_file, "r", encoding = 'ISO-8859-1') as file:
        # Create a CSV file for writing
        with open(output_file, "w", newline="", encoding = 'ISO-8859-1') as csvfile:
            fieldnames = ["number", "name", "in_contacts"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            hits = 0
            # Process each line in the input text file
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespaces
                if line:  # Skip empty lines
                    # Extract number and name from the line using pattern matching
                    number = re.search(number_pattern, line)
                    name = re.search(name_pattern, line)

                    if number and (name or extract_non_linked_numbers):
                        # Remove the "@s.whatsapp.net" part from the number
                        number = number.group(0).replace("@s.whatsapp.net", "")
                        number = number.replace("@c.us", "")
                        if name:
                            name = name.group(0)
                        # Write the extracted data to the CSV file
                        in_contacts = True
                        if re.search(no_contact_pattern, line) or not name:
                            in_contacts = False
                        writer.writerow({"number": number, "name": name, "in_contacts": in_contacts})
                        hits += 1
            print(f"Wrote new file {output_file} with {hits} lines.")
    # remove pre-extracted pattern file
    if delete_input_file_afterwards: 
        os.remove(input_file)
        print(f"Deleted file: {input_file}.")
    # return filepath such that functions can be nested
    return output_file

def add_country_codes_to_numbers(input_file, output_file=None, delete_input_file_afterwards = True):
    '''
    Function to add country codes to extracted numbers
    '''
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '_with_country_code.csv'
    # read the mapping of country codes to phone number prefixes
    country_codes = {}
    # check if country-code.csv file exists
    if os.path.exists('country-codes.csv'):
        with open('country-codes.csv', encoding = 'ISO-8859-1') as f:
            reader = csv.reader(f)
            for row in reader:
                country_codes[row[1]] = row[0]
        # remove entries with empty keys or values
        country_codes = {k: v for k, v in country_codes.items() if k != '' and v.strip() != ''}
        # add norway manually
        country_codes['47'] = 'NOR'

        # open the original CSV file and add a fourth column with the country code
        with open(input_file, encoding = 'ISO-8859-1') as f, open(output_file, 'w', newline='', encoding = 'ISO-8859-1') as g:
            reader = csv.reader(f)
            writer = csv.writer(g)
            header = next(reader)  # read the header row
            header.append('country_code')  # extend the header row
            writer.writerow(header)  # write the updated header row
            hits = 0
            for row in reader:
                phone_number = row[0]
                country_code = None
                for prefix, code in country_codes.items():
                    if phone_number.startswith(prefix):
                        country_code = code
                        break
                row.append(country_code)
                writer.writerow(row)
                hits += 1
        print(f"Wrote new file {output_file} with {hits} lines!")
        if delete_input_file_afterwards: 
            os.remove(input_file)
            print(f"Deleted file: {input_file}.")

    else:
        print("File country-code.csv file could not be found")
        print("Try downloading it from https://github.com/datasets/country-codes/blob/master/data/country-codes.csv\nAborting...")
    # return filepath such that functions can be nested
    return output_file

def add_number_occurences(input_file, output_file=None, delete_input_file_afterwards=True):
    '''
    Function to remove dublicates, bundle information and count occurences of the same number entry which could give insides into closeness to chat owner.
    '''
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '_and_occurences.csv'
    # Read the CSV file
    with open(input_file, newline='', encoding = 'ISO-8859-1') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    # Sort the data by the "country_code" column
    sorted_data = sorted(data, key=lambda x: int(x['number']))

    # setup unique data list with new 'occurences' field
    unique_data = [sorted_data[0]]
    unique_data[0]['occ'] = 1

    for item in sorted_data:
        if item['number'] != unique_data[-1]['number']:
            # add to unique data list
            unique_data.append(item)
            item['occ'] = 1
        else:
            # add occurences counter
            unique_data[-1]['occ'] += 1
            # check for additional information
            if item.get('name') and item['name']:
                if unique_data[-1]['name'] != item['name'] and not item['name']:
                    print(f"There are two different names, namely {unique_data[-1]['name']} and {item['name']}, registered for one number.")
                else:
                    # replace entry with duplicate entry which holds more information
                    unique_data[-1]['name'] = item['name']
                    unique_data[-1]['in_contacts'] = item['in_contacts']
            
    # write the sorted data back to the CSV file
    with open(output_file, 'w', newline='', encoding = 'ISO-8859-1') as f:
        fieldnames = ["number", "name", "in_contacts", "country_code", "occ"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_data)
        print(f"Wrote new file: {output_file} with {len(unique_data)} lines.")

    # delete input file
    if delete_input_file_afterwards: 
        os.remove(input_file)
        print(f"Deleted file: {input_file}.")
    # return filepath such that functions can be nested
    return output_file

def sort_csv_file(input_file, col_to_sort='occ', output_file=None, delete_input_file_afterwards = True):
    '''
    Sorts a given csv file according to the col to sort.
    If output_file argument is not provided or None, file is saved to <input_file>_sorted.csv
    '''
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + f"_sorted_by_{col_to_sort}.csv"
    # set up lambda function according to 'col_to_sort' due to necessary cast with columns 'occ', 'numbers'
    if col_to_sort == 'occ':
        cast = lambda c:  -int(c)
    elif col_to_sort == 'number':
        cast = lambda c: int(c[:4])
    elif col_to_sort == 'in_contacts':
        cast = lambda c: c
    else: # keep string format with 'Name', 'country_code'
        cast = lambda c: c
        
    # Read the CSV file
    with open(input_file, newline='', encoding = 'ISO-8859-1') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    # Sort the data by the "country_code" column
    sorted_data = sorted(data, key=lambda x: cast(x[col_to_sort]))

    # write the sorted data back to the CSV file
    with open(output_file, 'w', newline='', encoding = 'ISO-8859-1') as f:
        fieldnames = ["number", "name", "in_contacts", "country_code", "occ"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_data)
        print(f"Wrote new file: {output_file} with {len(sorted_data)} lines.")
    
    if delete_input_file_afterwards: 
        os.remove(input_file)
        print(f"Deleted file: {input_file}.")
    # return filepath such that functions can be nested
    return output_file
