import csv
import os
import re
# remove metadata from the top
#add - To iterate through all ini files in the folder 
ini_directory_path = r'Q:\src\Hack\SrpEncryptionConfig'
csv_file_path = r'data_sink.csv'

#The below csv is generated using the script of blame.py
commit_metadata_csv = 'SrpEncryptionConfig_commit_metadata\meta.csv' # relative path of the commit meta file


import csv

# Function to read a CSV file and convert it to a dictionary
def csv_to_dict(file_path):
    data_dict = {}
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            key = row[0]
            value = row[1:]
            data_dict[key] = value
    return data_dict

# Example usage
commit_metadata_dict = csv_to_dict(commit_metadata_csv)

# Should get live regions from kusto or some other source
valid_regions = [
    'eastusslv', 'centralindia', 'uksouth', 'westus2', 'japaneast',
    'centraluseuap', 'westcentralus', 'eastus2euap', 'eastus2(stage)', 
    'eastusstg', 'southcentralusstg', 'francecentral', 'eastasia', 
    'ukwest', 'newzealandnorth', 'southafricawest', 'italynorth', 
    'germanywestcentral', 'norwaywest', 'uaenorth', 'koreacentral', 
    'taiwannorth', 'francesouth', 'jioindiacentral', 'norwayeast', 
    'qatarcentral', 'germanynorth', 'brazilsoutheast', 'southafricanorth', 
    'swedensouth', 'westindia', 'swedencentral', 'taiwannorthwest', 
    'spaincentral', 'switzerlandnorth', 'jioindiawest', 'uaecentral', 
    'israelcentral', 'australiacentral', 'malaysiasouth', 'switzerlandwest', 
    'koreasouth', 'brazilsouth', 'southindia', 'polandcentral', 
    'canadacentral', 'eastus', 'australiaeast', 'eastus2', 
    'northcentralus', 'japanwest', 'westeurope', 'australiasoutheast', 
    'centralus', 'northeurope', 'southeastasia', 'westus3', 
    'mexicocentral', 'australiacentral2', 'canadaeast', 'southcentralus', 
    'westus'
]

# identify sections in .ini file and add a new column for it
# check with pratik to get history and commit of each dc
# add a new column to detect if the dc value is changed (show the latest commit leading to change)

data = []

import os

default_dc_value = None
pattern = r"^([\w]+)[ ]*=[ ]*([\w:.-]+)$"
# Map -> {key: DC name, value: {62 regions:value}}
for root, dirs, files in os.walk(ini_directory_path):
    for filename in files:
        if filename.endswith('.ini'):
            ini_file_path = os.path.join(root, filename)
            commit_id = ""
            commit_meta = []
            try:
                commit_id = root.split("\\")[-1].split("-")[-1]
                commit_meta = commit_metadata_dict.get(commit_id)
            except IndexError as ex:
                print(ex)
                exit(1)
            except KeyError as ex:
                print(ex)
                exit(1)

            # commit_meta = commit_metadata_csv
            default_dc_value = None
            if filename.endswith(".ini"):
                filename = filename[:-4]
            map = {}
            priorityMap = {} 
            dc_curr_file=set()
            with open(ini_file_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    if line.strip(): 
                        if not line or line.startswith(';') or line.startswith('[') or line.startswith('_meta.type'):
                            continue  
                        
                        #checking for default value
                        isDefaultValuePresent=re.search(pattern,line)
                        if(isDefaultValuePresent):
                            default_dc_value= isDefaultValuePresent.group(2)
                        key, value = line.split('=', 1) # key here will contain dc name, could contain region and environment 
                    
                        value = value.strip()
                        parts = key.split('&')
                        
                        environment = None
                        region = None

                        for part in parts:
                            if part.startswith('Region:'):
                                region = part.split(':')[1]
                            elif part.startswith('Environment:'):
                                environment = part.split(':')[1]
                            else:
                                print("Unknown modifier: " + part)
                        
                        print(region,environment)
                        config_name = parts[0].strip()
                        #Add current configuration to file
                        if config_name not in map:
                            map[config_name]={}
                            priorityMap[config_name]={}
                            # add all regions with empty values
                            # for valid_region in valid_regions:
                            #     if valid_region not in map[config_name]:
                            #         map[config_name][valid_region] = {}
                        # dc_curr_file.add(config_name)
                    
                        if region is None and environment is not "PublicAzure" and not isDefaultValuePresent: # no region, environment is not PublicAzure, and no default value found
                            continue
                        elif isDefaultValuePresent:                           # default value is found, if default_dc is not None, populate all regions with this value
                            for valid_region in valid_regions:
                                if valid_region not in map[config_name]:
                                    map[config_name][valid_region]=default_dc_value
                                    priorityMap[config_name][valid_region]=3
                        elif region is None and environment=="PublicAzure":      # region is not found but environment is found-> populate all regions in PublicAzure with this value
                            for valid_region in valid_regions:
                                if valid_region not in map[config_name]:       # This check is added to only populate it if the an explicit value has not been fetched by a region
                                    map[config_name][valid_region]=value
                                else:
                                    if priorityMap[config_name][valid_region]==3:
                                        map[config_name][valid_region]=value
                        else:
                            map[config_name][region]=value # This will cover the case where if region is present it will not be ignored (overwrite the default value)
                            priorityMap[config_name][region]=1
                print(map)
                for config_name, regions in map.items():
                    for region, value in regions.items():
                        data.append([filename, config_name, region, value, commit_id, commit_meta[0], commit_meta[1]])
    for name in dirs:
        print("in the dir: ", name, " ", os.path.join(root, name))


# default_dc_value = None
# pattern = r"^([\w]+)[ ]*=[ ]*([\w:.-]+)$"
# # Map -> {key: DC name, value: {62 regions:value}}
# for filename in os.listdir(ini_directory_path):
#     if filename.endswith('.ini'):
#         ini_file_path = os.path.join(ini_directory_path, filename)
#         commit_id = ""

#         print(ini_directory_path)
#         exit(0)

#         default_dc_value = None
#         if filename.endswith(".ini"):
#             filename = filename[:-4]
#         map = {}
#         priorityMap = {} 
#         dc_curr_file=set()
#         with open(ini_file_path, 'r', encoding='utf-8-sig') as f:
#             for line in f:
#                 if line.strip(): 
#                     if not line or line.startswith(';') or line.startswith('[') or line.startswith('_meta.type'):
#                         continue  
                    
#                     #checking for default value
#                     isDefaultValuePresent=re.search(pattern,line)
#                     if(isDefaultValuePresent):
#                         default_dc_value= isDefaultValuePresent.group(2)
#                     key, value = line.split('=', 1) # key here will contain dc name, could contain region and environment 
                
#                     value = value.strip()
#                     parts = key.split('&')
                    
#                     environment = None
#                     region = None

#                     for part in parts:
#                         if part.startswith('Region:'):
#                             region = part.split(':')[1]
#                         elif part.startswith('Environment:'):
#                             environment = part.split(':')[1]
#                         else:
#                             print("Unknown modifier: " + part)
                    
#                     print(region,environment)
#                     config_name = parts[0]
#                     #Add current configuration to file
#                     if config_name not in map:
#                         map[config_name]={}
#                         priorityMap[config_name]={}
#                         # add all regions with empty values
#                         # for valid_region in valid_regions:
#                         #     if valid_region not in map[config_name]:
#                         #         map[config_name][valid_region] = {}
#                     # dc_curr_file.add(config_name)
                  
#                     if region is None and environment is not "PublicAzure" and not isDefaultValuePresent: # no region, environment is not PublicAzure, and no default value found
#                         continue
#                     elif isDefaultValuePresent:                           # default value is found, if default_dc is not None, populate all regions with this value
#                         for valid_region in valid_regions:
#                             if valid_region not in map[config_name]:
#                                 map[config_name][valid_region]=default_dc_value
#                                 priorityMap[config_name][valid_region]=3
#                     elif region is None and environment=="PublicAzure":      # region is not found but environment is found-> populate all regions in PublicAzure with this value
#                         for valid_region in valid_regions:
#                             if valid_region not in map[config_name]:       # This check is added to only populate it if the an explicit value has not been fetched by a region
#                                 map[config_name][valid_region]=value
#                             else:
#                                 if priorityMap[config_name][valid_region]==3:
#                                     map[config_name][valid_region]=value
#                     else:
#                         map[config_name][region]=value # This will cover the case where if region is present it will not be ignored (overwrite the default value)
#                         priorityMap[config_name][region]=1
#             print(map)
#             for config_name, regions in map.items():
#                 for region, value in regions.items():
#                      data.append([filename, config_name, region, value])

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['FileName','Configuration Name', 'Region', 'Value', 'Commit-Id', 'Commit Time', 'Author'])
    writer.writerows(data)

print(f'Data is written to {csv_file_path}')


