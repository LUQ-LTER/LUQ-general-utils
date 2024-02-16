
import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import paramiko

# Google Drive setup
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = None

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret_264765493676-b7t1ii0khs385lvue3ntq3n1uvu54nj1.apps.googleusercontent.com.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('drive', 'v3', credentials=creds)
print(creds)
# Replace 'your_folder_id_here' with the actual Google Drive folder ID you want to download
folder_id = '1p8zWKlH5CunlIUKj6zjMyl0HiImx9yKk'
query = f"'{folder_id}' in parents"
print(query)
results = service.files().list(q=query, pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
items = results.get('files', [])


def download_files_in_folder(service, folder_id, folder_name):
    # Query to get folders
    folders_query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    folders = service.files().list(q=folders_query,
                                   spaces='drive',
                                   fields='nextPageToken, files(id, name)').execute().get('files', [])

    # Recursively list and download files from each folder
    for folder in folders:
        print(f"Accessing folder: {folder['name']}")
        download_files_in_folder(service, folder['id'], folder['name'])

    # Query to list files in the current folder (not folders)
    files_query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'"
    files = service.files().list(q=files_query,
                                 spaces='drive',
                                 fields='nextPageToken, files(id, name)').execute().get('files', [])

    for file in files:
        print(f"Downloading file: {file['name']} from folder: {folder_name}")
        request = service.files().get_media(fileId=file['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        # Define your path where you want to save the downloaded files
        file_path = os.path.join('download_path', folder_name, file['name'])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(fh.getvalue())

def download_and_upload(service, sftp, item, sftp_directory):
    fh = io.BytesIO()
    file_ext = ""
    print(f"Processing file: {item['name']}")
    if item['mimeType'] == 'application/vnd.google-apps.folder':
        # Recursively handle folders
        download_files_in_folder(service, item['id'], item['name'])
    else:
        # Handle file download
        if item['mimeType'].startswith('application/vnd.google-apps.'):
            # Adjust this logic to handle Google Docs files appropriately
            # print("Skipping Google Docs file for direct download. Needs export handling.")
            # return

            if item['mimeType'] in ["application/vnd.google-apps.document",
                                    "application/vnd.google-apps.spreadsheet",
                                    "application/vnd.google-apps.presentation"]:
                # It's a Google Docs, Sheets, or Slides file, so export it
                if item['mimeType'] == "application/vnd.google-apps.document":
                    export_mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    file_ext = '.docx'
                elif item['mimeType'] == "application/vnd.google-apps.spreadsheet":
                    export_mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    file_ext = '.xlsx'
                else:  # Google Slides
                    export_mimeType = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                    file_ext = '.pptx'

                request = service.files().export_media(fileId=item['id'], mimeType=export_mimeType)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                remote_file_path = os.path.join(sftp_directory, item['name'])
                if len(file_ext) > 0:
                    remote_file_path += file_ext
                print(f"Uploading {item['name']} to {remote_file_path}")
                fh.seek(0)  # Ensure we're at the start of the file
                sftp.putfo(fh, remote_file_path)
            else:
                # It's a binary file, download it directly
                request = service.files().get_media(fileId=item['id'])

                # request = service.files().get_media(fileId=item['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                remote_file_path = os.path.join(sftp_directory, item['name'])
                print(f"Uploading {item['name']} to {remote_file_path}")
                fh.seek(0)  # Ensure we're at the start of the file
                sftp.putfo(fh, remote_file_path)

        else:
            request = service.files().get_media(fileId=item['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            fh.seek(0)

            # Upload the file content using SFTP
            remote_file_path = os.path.join(sftp_directory, item['name'])
            print(f"Uploading {item['name']} to {remote_file_path}")
            fh.seek(0)  # Ensure we're at the start of the file
            sftp.putfo(fh, remote_file_path)


# SFTP setup and file upload
sftp_host = 'xx.xxx.xx.xxx'
sftp_port = 22
sftp_username = 'ubuntu'
# sftp_password = 'your_password'
private_key_path = './luqlter.pem'

sftp_directory = '/mnt2/googlebackup/LFDP'
# Connect to SFTP and process items for download and upload
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
ssh_client.connect(sftp_host, port=sftp_port, username=sftp_username, pkey=private_key)
sftp = ssh_client.open_sftp()

for item in items:
    download_and_upload(service, sftp, item, sftp_directory)

sftp.close()
ssh_client.close()
print('All files have been uploaded to the server.')