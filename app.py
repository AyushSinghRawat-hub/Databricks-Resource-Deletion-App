import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointStateConfigUpdate
from typing import List
import json

# Streamlit app configuration
st.set_page_config(page_title="Databricks Resource Deletion", layout="wide")
st.title("Databricks Resource Deletion App")

# Sidebar for configuration
with st.sidebar:
    st.header("Databricks Configuration")
    workspace_url = st.text_input("Databricks Workspace URL", placeholder="https://<workspace-id>.cloud.databricks.com")
    token = st.text_input("Databricks Personal Access Token", type="password")
    st.header("Advanced Options")
    disable_foundation_models = st.checkbox("Set rate limits to 0 for foundation models (disables instead of deletes)", False)
    delete_ai_bricks = st.checkbox("Attempt to delete associated AI Bricks (experimental)", False)

# Main content
st.write("Enter your Databricks workspace details and select resources to delete.")
st.subheader("Select Resources to Delete")
delete_options = st.multiselect(
    "Choose resources to delete",
    options=["All Catalogs", "All Jobs", "All Notebooks", "All Serving Endpoints"],
    help="Select one or more resource types to delete. Use with caution!"
)

# Confirmation checkbox
confirm_deletion = st.checkbox("I confirm I want to delete the selected resources (IRREVERSIBLE!)")

# Initialize session state for status messages
if "status_messages" not in st.session_state:
    st.session_state.status_messages = []

def delete_catalogs(client: WorkspaceClient) -> List[str]:
    """Delete all non-protected catalogs using the Databricks SDK."""
    messages = []
    try:
        catalogs = client.catalogs.list()
        for catalog in catalogs:
            catalog_name = catalog.name
            if catalog_name not in ["hive_metastore"]:  # Skip protected catalogs
                try:
                    client.catalogs.delete(name=catalog_name, force=True)  # force=True for CASCADE
                    messages.append(f"Deleted catalog: {catalog_name}")
                except Exception as e:
                    messages.append(f"Failed to delete catalog: {catalog_name}. Error: {str(e)}")
    except Exception as e:
        messages.append(f"Error listing catalogs: {str(e)}")
    return messages

def delete_jobs(client: WorkspaceClient) -> List[str]:
    """Delete all jobs."""
    messages = []
    try:
        jobs = client.jobs.list()
        for job in jobs:
            try:
                client.jobs.delete(job_id=job.job_id)
                messages.append(f"Deleted job with ID: {job.job_id}")
            except Exception as e:
                messages.append(f"Failed to delete job with ID: {job.job_id}. Error: {str(e)}")
    except Exception as e:
        messages.append(f"Error listing jobs: {str(e)}")
    return messages

def delete_notebooks(client: WorkspaceClient) -> List[str]:
    """Delete all notebooks in the workspace."""
    messages = []
    try:
        notebooks = client.workspace.list(path="/", recursive=True)
        for item in notebooks:
            if item.object_type == "NOTEBOOK":
                try:
                    client.workspace.delete(path=item.path)
                    messages.append(f"Deleted notebook: {item.path}")
                except Exception as e:
                    messages.append(f"Failed to delete notebook: {item.path}. Error: {str(e)}")
    except Exception as e:
        messages.append(f"Error listing notebooks: {str(e)}")
    return messages

def delete_serving_endpoints(client: WorkspaceClient, disable_foundation: bool, delete_bricks: bool) -> List[str]:
    """Delete or disable serving endpoints, handling AI Bricks and foundation models."""
    messages = []
    try:
        endpoints = client.serving_endpoints.list()
        for endpoint in endpoints:
            # Handle dictionary-based endpoint data
            endpoint_name = endpoint.get('name') if isinstance(endpoint, dict) else endpoint.name
            try:
                if "databricks-" in endpoint_name and disable_foundation:
                    # Handle foundation models by setting rate limits to 0
                    client.serving_endpoints.update_config(
                        name=endpoint_name,
                        traffic_config={"routes": [{"served_model_name": endpoint_name, "traffic_percentage": 0}]}
                    )
                    messages.append(f"Disabled foundation model endpoint: {endpoint_name} (rate limits set to 0)")
                else:
                    # Attempt to delete the endpoint
                    client.serving_endpoints.delete(name=endpoint_name)
                    messages.append(f"Deleted serving endpoint: {endpoint_name}")
            except Exception as e:
                error_msg = str(e)
                if "Please delete the AI Brick" in error_msg and delete_bricks:
                    messages.append(f"AI Brick deletion for {endpoint_name} not supported in SDK. Please delete manually via UI.")
                else:
                    messages.append(f"Failed to delete serving endpoint: {endpoint_name}. Error: {error_msg}")
    except Exception as e:
        messages.append(f"Error listing serving endpoints: {str(e)}")
    return messages

# Delete button
if st.button("Delete Selected Resources", disabled=not (workspace_url and token and delete_options and confirm_deletion)):
    if not (workspace_url.startswith("https://") and token):
        st.error("Please provide a valid workspace URL and token.")
    else:
        try:
            # Initialize Databricks client
            client = WorkspaceClient(host=workspace_url, token=token)
            st.session_state.status_messages = []

            # Execute deletions based on user selection
            if "All Catalogs" in delete_options:
                st.session_state.status_messages.extend(delete_catalogs(client))
            if "All Jobs" in delete_options:
                st.session_state.status_messages.extend(delete_jobs(client))
            if "All Notebooks" in delete_options:
                st.session_state.status_messages.extend(delete_notebooks(client))
            if "All Serving Endpoints" in delete_options:
                st.session_state.status_messages.extend(
                    delete_serving_endpoints(client, disable_foundation_models, delete_ai_bricks)
                )

        except Exception as e:
            st.session_state.status_messages.append(f"Connection error: {str(e)}")

# Display status messages
if st.session_state.status_messages:
    st.subheader("Deletion Status")
    for msg in st.session_state.status_messages:
        if "Deleted" in msg or "Disabled" in msg:
            st.success(msg)
        else:
            st.error(msg)

# Warning and guidance
st.warning("⚠️ Deletion is irreversible. Ensure you have backups and proper permissions. For AI Brick-associated endpoints, delete the AI Brick via the Databricks UI. For foundation models, enable the 'Set rate limits to 0' option to disable instead of delete.")