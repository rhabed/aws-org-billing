## ADDED Requirements

### Requirement: Authentication Status Check
The system SHALL check if the user has a valid AWS session before allowing the billing report generation to start.

#### Scenario: User attempts to run reports without valid session
- **WHEN** the user clicks "Run Reports" but is not logged into AWS
- **THEN** the system SHALL display an error message and prompt the user to log in.

### Requirement: Profile Selection
The system SHALL allow the user to select the AWS profile to use for the billing scripts if multiple profiles are supported.

#### Scenario: User selects a specific AWS profile
- **WHEN** the user chooses a profile from a dropdown (e.g., "kloudr-961")
- **THEN** the system SHALL set the `AWS_PROFILE` environment variable accordingly for subsequent commands.
