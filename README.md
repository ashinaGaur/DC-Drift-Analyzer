# DC-Drift-Analyzer

# Dynamic Config Monitoring Tool

## Features

- **View Statistics**: Get insights into Dynamic Config (DC) values.
- **Drift Detection**:
  - Identify discrepancies between active/live values and configured values.
  - Detect drift in config values across different environments and regions.
- **Change History**: Access config change history (note: this does not include live changes).
- **DC Drifts**: Identify DCs that need attention due to being drifted or stale.
- **Future Enhancements**:
  - Ability to annotate and document expected DC drifts.
  - Automate reporting as part of official builds and publish a comprehensive report.

## Benefits

- **Bird's-Eye View**: Provides developers and managers with an overview of the configuration state.
- **Actionable Insights**: Helps identify DC drifts that require action, such as outdated values that haven't been updated in months.
- **Issue Identification**: Easily view change history to assist in troubleshooting and identifying issues.

## Implementation

- **Python Scripts**: Utilizes Python scripts to check Git history and parse configuration files.
- The parser has been written in python code. The parser fetches information after parsing the .ini file and consolidates the information in an excel sheet like as below.
!informationAfterParsing
This includes the FileName, ConfigurationName, Region, Value of the DC, Commit Id, Commit time and Author of the DC.
- **Data Storage**: Leverages an existing Kusto table for active configuration snapshots.
- The information fetched from the Parser is compared with the Active Configuration(This is fetched from Kusto) for identification of DC Drifts.

The PowerBI dashboard provides a detailed overview of DC-related information, featuring:

- **Configuration Files**: Comprehensive details of all config files.
- **Regions**: Information on various regions.
- **DC Values**: DC values for each region.
- **Graphical Representation**: Visual charts and graphs for better understanding.
- **DC Count**: Total count of DCs across regions.
- **DC Drifts**: Comparison of DC values in config files with the actual active configuration of DC values in Kusto.

- **Visualization**: Uses Power BI to visualize the data for better analysis and reporting.
