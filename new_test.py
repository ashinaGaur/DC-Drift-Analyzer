import csv
import os
import re
# remove metadata from the top
#add - To iterate through all ini files in the folder 
ini_directory_path = r'Q:\src\Storage-SRP\src\Service\PackageRoot\Config'
csv_file_path = r'new_source_2.csv'

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

data = set()
# x = set()
# x.add(tuple(['a', 'b']))
# x.add(tuple(['b']))
# x.add(tuple([2]))
# x.add(tuple(['a', 'b']))
# print(x)
# exit(0)
default_dc_value = None
pattern = r"^([\w]+)[ ]*=[ ]*([\w:.-]+)$"
# Map -> {key: DC name, value: {62 regions:value}}
for filename in os.listdir(ini_directory_path):
    if filename.endswith('.ini'):
        ini_file_path = os.path.join(ini_directory_path, filename)
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
                    if "LogEncryptedServicesString" in line:
                        print(line) 
                    
                    #checking for default value
                    isDefaultValuePresent=re.search(pattern,line)
                    if(isDefaultValuePresent):
                        default_dc_value= isDefaultValuePresent.group(2)
                    key, value = line.split('=', 1) # key here will contain dc name, could contain region and environment 
                    
                    key = key.strip()
                    value = value.strip()
                    parts = key.split('&')
                    
                    environment = None
                    region = None

                    for part in parts:
                        if part.startswith('Region:'):
                            region = part.split(':')[1]
                        elif part.startswith('Environment:'):
                            environment = part.split(':')[1]
                        # else:
                        #     print("Unknown modifier: " + part)
                    
                    # print(region,environment)
                    config_name = parts[0]
                    #Add current configuration to file
                    if config_name not in map:
                        map[config_name]={}
                        priorityMap[config_name]={}
                        # add all regions with empty values
                        # for valid_region in valid_regions:
                        #     if valid_region not in map[config_name]:
                        #         map[config_name][valid_region] = {}
                    # dc_curr_file.add(config_name)
                  
                    if config_name == "LogEncryptedServicesString":
                        print("for config:", config_name, "=", isDefaultValuePresent, line)
                    if region is None and environment is not "PublicAzure" and not isDefaultValuePresent: # no region, environment is not PublicAzure, and no default value found
                        continue
                    elif isDefaultValuePresent:
                        if config_name == "LogEncryptedServicesString":
                            print("[Default]Valid region:", config_name, map[config_name])                           # default value is found, if default_dc is not None, populate all regions with this value
                        for valid_region in valid_regions:
                            if valid_region not in map[config_name]:
                                map[config_name][valid_region]=default_dc_value
                                priorityMap[config_name][valid_region]=3
                    elif region is None and environment=="PublicAzure":      # region is not found but environment is found-> populate all regions in PublicAzure with this value
                        print("Valid region:", valid_region)
                        for valid_region in valid_regions:
                            if valid_region not in map[config_name]:       # This check is added to only populate it if the an explicit value has not been fetched by a region
                                map[config_name][valid_region]=value
                            else:
                                if priorityMap[config_name][valid_region]==3:
                                    map[config_name][valid_region]=value
                    else:
                        map[config_name][region]=value # This will cover the case where if region is present it will not be ignored (overwrite the default value)
                        priorityMap[config_name][region]=1
            # print(map)
            for config_name, regions in map.items():
                for region, value in regions.items():
                     data.add(tuple([filename, config_name.strip(), region, value]))

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['FileName','Configuration Name', 'Region', 'Value'])
    writer.writerows(data)

print(f'Data is written to {csv_file_path}')


