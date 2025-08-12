from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

class drive_handler:
    def __init__(self):
        pass

    def load(self):
        creds = Credentials.from_service_account_file(
            'credentials/service_account.json',
            scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=creds)
        

    def create_folder(self, folder_name, parent_folder_id=None):
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        folder = self.service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')  # Return the ID of the created folder
    
    def create_file(self, file_name, mime_type, folder_id=None) -> str:
        file_metadata = {
            'name': file_name,
            'mimeType': mime_type
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')
    
handler = drive_handler()