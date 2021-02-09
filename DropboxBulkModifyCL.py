import pandas as pd
import dropbox
from tqdm import tqdm

from dropbox import DropboxOAuth2FlowNoRedirect

'''
This sets up a dropbox OAuthed client
'''
APP_KEY = 'xxx'
APP_SECRET = 'xxx'

auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

authorize_url = auth_flow.start()
print("1. Go to: " + authorize_url)
print("2. Click \"Allow\" (you might have to log in first).")
print("3. Copy the authorization code.")
auth_code = input("Enter the authorization code here: ").strip()

try:
    oauth_result = auth_flow.finish(auth_code)
except Exception as e:
    print('Error: %s' % (e,))
    exit(1)

with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
    dbx.users_get_current_account()
    print("Successfully set up client!")
    

'''
This sets up the varibles needed
'''
mode = input('\nWould you like to:\na: Create or replace content\nb: Delete content\n').strip()
print('\nFor folder\nThe input should be /folder1/folder2/\n')
print('\nFor files\nThe input should be /folder1/folder2/file1.ex\n')
child = input("Enter the child folders' location here: ").strip()
mContent = input("Enter the master content's location here: ").strip()
mName = mContent.split('/')[-2]
Spreadsheet = input("Enter the Spreadsheet's location here: ").strip()

#Reads speadsheet
metadata, res = dbx.files_download(path= Spreadsheet)
sht = pd.read_excel(res.content)

#Create relocation list
entries = pd.DataFrame([])
entries['to_path'] = child + sht.loc[sht['MOD'] == 'x']['Name'] + '/' + mName
entries['from_path'] = mContent
entries.reset_index(drop = True)

#Bulk change
if mode == 'a':
    for index, row in tqdm(entries.iterrows(), total=entries.shape[0]):
        try:
            dbx.files_delete_v2(row['to_path'])
        except Exception:
            pass
        dbx.files_copy_v2(row['from_path'],row['to_path'])
else:
    for index, row in tqdm(entries.iterrows(), total=entries.shape[0]):
        try:
            dbx.files_delete_v2(row['to_path'])
        except Exception:
            pass
    
print('Complete!')
