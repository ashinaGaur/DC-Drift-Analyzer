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
- **Data Storage**: Leverages an existing Kusto table for active configuration snapshots.
- **Visualization**: Uses Power BI to visualize the data for better analysis and reporting.
