Databricks Resource Deletion App
This Streamlit app provides a user-friendly interface to delete Databricks resources, including catalogs, jobs, notebooks, and serving endpoints, using the Databricks SDK. It supports secure authentication, handles special cases like AI Brick-associated endpoints and foundation models, and includes safety features to prevent accidental deletions.
Features

Input Fields: Enter Databricks workspace URL and personal access token.
Resource Selection: Choose to delete all catalogs, jobs, notebooks, or serving endpoints via a multiselect dropdown.
Advanced Options:
Disable foundation model endpoints (e.g., databricks-claude-3-7-sonnet) by setting rate limits to 0.
Experimental option to flag AI Brick-associated endpoints for manual deletion.


Safety: Requires a confirmation checkbox to prevent accidental deletions.
Error Handling: Displays detailed success and error messages for each deletion attempt.
UI: Polished interface with a sidebar for configuration and clear status feedback.

Prerequisites

Python: Version 3.8 or higher.
Databricks Workspace: A valid Databricks workspace URL and personal access token with MANAGE permissions for catalogs, jobs, notebooks, and serving endpoints.
Dependencies: Listed in requirements.txt.

Installation

Clone the Repository:git clone <repository-url>
cd <repository-directory>


Install Dependencies:pip install -r requirements.txt

Contents of requirements.txt:streamlit==1.39.0
databricks-sdk==0.34.0
requests==2.32.3


Optional CLI Setup (if using CLI-based deletion):pip install databricks-cli==0.18.0
databricks configure --token


Enter your workspace URL and token when prompted.



Usage

Run the App:streamlit run app.py


The app opens in your browser at http://localhost:8501.


Configure the App:
In the sidebar, enter your Databricks Workspace URL (e.g., https://adb-1234567890.cloud.databricks.com).
Enter your Personal Access Token (generated in Databricks under User Settings).
Optionally, enable Advanced Options:
Check "Set rate limits to 0 for foundation models" to disable foundation model endpoints.
Check "Attempt to delete associated AI Bricks" to flag AI Brick endpoints (note: requires manual deletion via UI).




Select Resources:
Choose resources to delete (e.g., All Catalogs, All Jobs) from the multiselect dropdown.


Confirm Deletion:
Check the "I confirm I want to delete the selected resources (IRREVERSIBLE!)" checkbox.
Click Delete Selected Resources to start the deletion process.


Review Status:
Success and error messages appear under "Deletion Status".
For AI Brick-associated endpoints (e.g., ka-43d8c535-endpoint), manually delete the AI Brick in the Databricks UI and re-run the app.
For foundation models (e.g., databricks-claude-3-7-sonnet), ensure the "Set rate limits to 0" option is enabled to disable them.



Troubleshooting

Error: 'WorkspaceClient' object has no attribute 'host':
Fixed in the latest app version by using client.catalogs for catalog deletion.


Error: 'dict' object has no attribute 'as_dict':
Fixed by handling dictionary-based endpoint data in the delete_serving_endpoints function.


AI Brick Endpoints (e.g., ka-43d8c535-endpoint):
The SDK does not support AI Brick deletion. Manually delete AI Bricks in the Databricks UI:
Navigate to Machine Learning > AI Bricks in the Databricks workspace.
Locate and delete the AI Brick associated with the endpoint.
Re-run the app to delete the endpoint.




Foundation Models (e.g., databricks-claude-3-7-sonnet):
These cannot be deleted. Enable the "Set rate limits to 0" option to disable them, or manually set rate limits to 0 in the Databricks UI under Serving > Endpoints.


Authentication Issues:
Ensure the token has MANAGE permissions for the selected resources.
Use a service principal for production automation to avoid user-specific issues.


CLI Errors:
If using the CLI-based version, ensure databricks-cli is installed and configured (databricks configure --token).
Check for CLI version compatibility (pip install databricks-cli --upgrade).



CLI-Based Alternative
To use the Databricks CLI instead of the SDK, replace the deletion functions in app.py with CLI equivalents. Example for serving endpoints:
import subprocess
import json

def delete_serving_endpoints_cli(disable_foundation: bool, delete_bricks: bool) -> List[str]:
    messages = []
    try:
        result = subprocess.run(
            ["databricks", "serving-endpoints", "list", "--output", "JSON"],
            capture_output=True, text=True, check=True
        )
        endpoints = json.loads(result.stdout).get("endpoints", [])
        for endpoint in endpoints:
            endpoint_name = endpoint["name"]
            try:
                if "databricks-" in endpoint_name and disable_foundation:
                    subprocess.run(
                        ["databricks", "serving-endpoints", "update-config", endpoint_name, "--json", json.dumps({
                            "traffic_config": {"routes": [{"served_model_name": endpoint_name, "traffic_percentage": 0}]}
                        })],
                        check=True
                    )
                    messages.append(f"Disabled foundation model endpoint: {endpoint_name} (rate limits set to 0)")
                else:
                    subprocess.run(
                        ["databricks", "serving-endpoints", "delete", endpoint_name],
                        check=True
                    )
                    messages.append(f"Deleted serving endpoint: {endpoint_name}")
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr
                if "Please delete the AI Brick" in error_msg and delete_bricks:
                    messages.append(f"AI Brick deletion for {endpoint_name} not supported in CLI. Please delete manually via UI.")
                else:
                    messages.append(f"Failed to delete serving endpoint: {endpoint_name}. Error: {error_msg}")
    except subprocess.CalledProcessError as e:
        messages.append(f"Error listing serving endpoints: {e.stderr}")
    except Exception as e:
        messages.append(f"Error listing serving endpoints: {str(e)}")
    return messages


Update requirements.txt to include databricks-cli==0.18.0.
Configure the CLI with databricks configure --token.

Notes

Safety: Always test in a non-production workspace to avoid accidental data loss. Back up critical data (e.g., catalog metadata, notebooks) before deletion.
Permissions: The token or service principal must have MANAGE permissions for catalogs, jobs, notebooks, and serving endpoints.
AI Bricks: Deletion is not supported programmatically. Use the Databricks UI for these endpoints.
Foundation Models: These cannot be deleted; use the "Set rate limits to 0" option to disable them.
Deployment: Host on a server (e.g., AWS EC2, Azure App Service) for team access. Use a service principal for secure automation.

Contributing

Report issues or suggest features by creating a GitHub issue.
To add custom filters (e.g., delete only specific catalogs), modify the respective deletion functions in app.py.

License
MIT License. See LICENSE for details.