
# Databricks Resource Deletion App

This Streamlit app provides a user-friendly interface to delete Databricks resources, including catalogs, jobs, notebooks, and serving endpoints, using the Databricks SDK. It supports secure authentication, handles special cases like AI Brick-associated endpoints and foundation models, and includes safety features to prevent accidental deletions.
## Features

- Input Fields: Enter Databricks workspace URL and personal access token.

- Resource Selection: Choose to delete all catalogs, jobs, notebooks, or serving endpoints via a multiselect dropdown.

- Advanced Options:

- Disable foundation model endpoints (e.g., databricks-claude-3-7-sonnet) by setting rate limits to 0.

- Experimental option to flag AI Brick-associated endpoints for manual deletion.

- Safety: Requires a confirmation checkbox to prevent accidental deletions.

- Error Handling: Displays detailed success and error messages for each deletion attempt.

- UI: Polished interface with a sidebar for configuration and clear status feedback.


## Prerequisites

- Python: Version 3.8 or higher.

- Databricks Workspace: A valid Databricks workspace URL and personal access token with MANAGE permissions for catalogs, jobs, notebooks, and serving endpoints.

- Dependencies: Listed in requirements.txt.

## Installation

#### Clone the Repository:

```http
  git clone <repository-url>
  cd <repository-directory>
```

#### Install Dependencies:

```http
  pip install -r requirements.txt
```

#### Contents of requirements.txt:

```http
  streamlit==1.39.0
  databricks-sdk==0.34.0
  requests==2.32.3 
```

#### Optional CLI Setup (if using CLI-based deletion):

```http
  pip install databricks-cli==0.18.0
  databricks configure --token 
```

## Usage
#### Run the App:

```http
  streamlit run app.py
```

## Configure the App:
-  In the sidebar, enter your Databricks Workspace URL (e.g., https://adb-1234567890.cloud.databricks.com).

- Enter your Personal Access Token (generated in Databricks under User Settings).

- Optionally, enable Advanced Options:

- Check "Set rate limits to 0 for foundation models" to disable foundation model endpoints.

- Check "Attempt to delete associated AI Bricks" to flag AI Brick endpoints (note: requires manual deletion via UI).

- Select Resources:

- Choose resources to delete (e.g., All Catalogs, All Jobs) from the multiselect dropdown.

- Confirm Deletion:

- Check the "I confirm I want to delete the selected resources (IRREVERSIBLE!)" checkbox.

- Click Delete Selected Resources to start the deletion process.

- Review Status:

- Success and error messages appear under "Deletion Status".


- For AI Brick-associated endpoints (e.g., ka-43d8c535-endpoint), manually delete the AI Brick in the Databricks UI and re-run the app.

- For foundation models (e.g., databricks-claude-3-7-sonnet), ensure the "Set rate limits to 0" option is enabled to disable them.

## Notes

- Safety: Always test in a non-production workspace to avoid accidental data loss. Back up critical data (e.g., catalog metadata, notebooks) before deletion.

- Permissions: The token or service principal must have MANAGE permissions for catalogs, jobs, notebooks, and serving endpoints.

- AI Bricks: Deletion is not supported programmatically. Use the Databricks UI for these endpoints.

- Foundation Models: These cannot be deleted; use the "Set rate limits to 0" option to disable them.

- Deployment: Host on a server (e.g., AWS EC2, Azure App Service) for team access. Use a service principal for secure automation.


## Contributing
- Report issues or suggest features by creating a GitHub issue.

- To add custom filters (e.g., delete only specific catalogs), modify the respective deletion functions in app.py.
## License

[MIT License.  See LICENSE for details.](https://choosealicense.com/licenses/mit/)


## Authors

- [@Ayush Singh Rawat](https://github.com/AyushSinghRawat-hub)
