import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the .ini file
config.read('example.ini')

# Accessing data
section = 'SectionName'
option = 'OptionName'
value = config.get(section, option)
print(f'The value of {option} in {section} is {value}')