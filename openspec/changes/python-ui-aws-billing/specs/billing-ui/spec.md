## ADDED Requirements

### Requirement: Date Range Selection
The system SHALL provide a user interface to select a start date and an end date for the billing report.

#### Scenario: User selects a valid date range
- **WHEN** the user selects "2024-01-01" as start date and "2024-01-31" as end date
- **THEN** the system SHALL validate the range and store it for the report generation.

### Requirement: Trigger Billing Process
The system SHALL provide a button to trigger the execution of all billing scripts (`run_961.sh`, `run_leb.sh`, `run_ksa.sh`) for the selected date range.

#### Scenario: User triggers the report generation
- **WHEN** the user clicks the "Run Reports" button after selecting dates
- **THEN** the system SHALL execute the billing scripts sequentially and display the progress/logs in the UI.

### Requirement: Display Output Files
The system SHALL list the generated Excel files in the UI after the process completes.

#### Scenario: Reports are generated successfully
- **WHEN** the billing process finishes
- **THEN** the system SHALL display a list of links or buttons to open/download the generated `.xlsx` files from the `excel_output/` directory.
