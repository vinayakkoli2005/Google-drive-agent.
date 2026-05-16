import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SHARED_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt")


def get_drive_service():
    """Authenticate and return the Google Drive API service."""
    try:
        # Prefer JSON string from env var (for Railway/cloud deployments)
        sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if sa_json:
            import json
            sa_info = json.loads(sa_json)
            creds = service_account.Credentials.from_service_account_info(
                sa_info, scopes=SCOPES)
        else:
            # Fall back to file on disk (for local development)
            sa_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")
            if not os.path.exists(sa_file):
                logger.warning(f"Service account file '{sa_file}' not found.")
                return None
            creds = service_account.Credentials.from_service_account_file(
                sa_file, scopes=SCOPES)

        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        logger.error(f"Error building Drive service: {e}")
        return None


def _get_all_folder_ids(service, root_folder_id: str) -> list[str]:
    """Recursively collect all subfolder IDs under root_folder_id."""
    all_ids = [root_folder_id]
    queue = [root_folder_id]

    while queue:
        parent_id = queue.pop()
        try:
            resp = service.files().list(
                q=f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
                fields="files(id)",
                pageSize=100,
            ).execute()
            for f in resp.get("files", []):
                all_ids.append(f["id"])
                queue.append(f["id"])
        except Exception as e:
            logger.warning(f"Could not list subfolders of {parent_id}: {e}")

    return all_ids


def search_drive_files(query: str) -> list[dict]:
    """
    Search files in the Google Drive folder (including subfolders) using the q parameter.
    Always excludes trashed files. Paginates to return up to 50 results.
    """
    service = get_drive_service()
    if not service:
        return [{"error": "Google Drive Service Account not configured. Please add service_account.json."}]

    try:
        folder_ids = _get_all_folder_ids(service, SHARED_FOLDER_ID)
        parents_clause = " or ".join(f"'{fid}' in parents" for fid in folder_ids)
        folder_query = f"({parents_clause}) and trashed = false"

        if query:
            final_query = f"({query}) and {folder_query}"
        else:
            final_query = folder_query

        items = []
        page_token = None

        while len(items) < 50:
            resp = service.files().list(
                q=final_query,
                pageSize=min(50 - len(items), 50),
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink, webContentLink)",
                spaces='drive',
                pageToken=page_token,
            ).execute()

            items.extend(resp.get('files', []))
            page_token = resp.get('nextPageToken')
            if not page_token:
                break

        return items

    except Exception as e:
        logger.error(f"Error searching Drive: {e}")
        return [{"error": str(e)}]
