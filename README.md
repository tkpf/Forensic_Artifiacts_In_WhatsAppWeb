# Metadata Extractor for WhatsApp Web .ldb files
This repository contains functions to extract artifacts from WhatsApp Web Metadata (Tested using Chrome Browser Version 113.0.5672.93 (64-Bit)).  
Artifacts include:
- Name and Surname of a person
- Numbers
- Group Names
- Further plain text such as sent attachment names or group descriptions

The script can be started from command line by:
```python extractor.py <args>```

In the default execution the python script will extract
- single names (written to name_single.csv)
- names containing at least two consecutive names (e.g. first name and surname) (written to name_double_plus.csv)
- numbers containing 9-15 chiffres (e.g. telephonenumbers) (written number_simple.csv)
- numbers and names which can be linked together in a next step (pre-filtered result written to number_and_name_linked.csv)

In a consecutive step it will add country codes, count occurences of numbers and sort the csv file according to the number of occurences.  
In the case of post-computing of file 'number_and_name_linked.csv' it will also check if the the contact name is coming from the local address book or it represents the WhatsApp name given by the numbers owner.
This will create the files:
- number_simple_with_country_code_and_occurences_sorted_by_occ.csv
- number_and_contacts_with_country_code_and_occurences_sorted_by_occ.csv

## Arguments to adjust script behavior
There are 3 arguments which can be provided:
1. -c some/filepath/
2. -s my_sort_col
3. -exn NoName1 NoName2 

By default it is expected that the WhatsApp Web Metadata files are already copied into a directory names './input' in the working directory. If '-c' argument is provided, the script will copy the .ldb files located in the provided filepath into a directory names 'input' in the current working directory.  
Regularly, Whatsapp Web Metadata files using Chrome are located in filepath ```C:\\User\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\IndexedDB\\https_web.whatsapp.com_0.indexeddb.leveldb```

The '-s' argument specifies with respect to what column the final csv file should be sorted. This can be:
- name
- number
- in_contacts
- country_code
- occ

Default is 'occ'.

The argument '-exn' can be used to exclude additonal strings from the 'name_single.csv' file. When single names are extracted from the metadata files very generic patterns must be used (e.g. one capital letter, followed by at least 2 small letters). This leads to a high false positive rate. As the same false positives appear multiple times, the specification of some false positive strings can reduce the false positive rate dramatically. As a starting point the following strings are excluded by default:  
```Status|Error|Event|Single|Direct|Time|Sent|Update|Obaque|Record|Paused|Dialog|Select|Offset|Sender|Parent|Height|Hverified|Lverified|Connec```

Note that post specifying new excluding names after a first inspection will harm the integrity of the test data and, strictly speaking, the new false positive rate cannot be seen as true false positive rate. Nonetheless, for a forensic examiner this post specification will come in handy as it reduces names to look out for drastically.

The script does not claim to extract all possible metadata, but can be seen as good starting point with a majority of interesting insights.

## Script stats.py
stats.py evaluates and visualizes the extracted artifact data with respect to the number occurences and country code occurences. The script visualizes the results in bar plots.