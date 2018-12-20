import requests
import time
import sys
import private
from slacker import Slacker

def download_files(files):

    for file in files:
        
        global total_file_count
        global delete_from_slack
        global id2user

        timestamp = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(float(file['timestamp'])))
        user = id2user[file['user']]
        fname = file['name']
        file_id = file['id']
        filename = timestamp + "_" + user + "_" + fname
        print(str(total_file_count) + ". " + filename)

        #Handle dropbox files by downloading thumbnail from slack.
        if 'url_private_download' in file:
            url = file['url_private_download']
        else:
            print "No download url, grabbing thumbnail 1024"
            if 'thumb_1024' in file:
                url = file['thumb_1024']
                print url
            else:
                if delete_from_slack:
                    slack.files.delete(file['id'])
                    print "Deleted from slack: " + filename
                continue

        r = requests.get(url, headers={'Authorization': 'Bearer %s' % token})
        if r.status_code == 200:

            with open("./downloads/"+filename, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

            if delete_from_slack:
                slack.files.delete(file['id'])
                print "Deleted: " + filename

        else:
            print "Error!: " + r.status_code

        total_file_count = total_file_count + 1

################################################################

#get token here: https://api.slack.com/custom-integrations/legacy-tokens
token = private.token

#if set to false, file will be downloaded but not deleted from slack
delete_from_slack = False

# pages are batches of uploads in 100 counts. Higher pages are older uploads.
currentpage = 1

#get user_id for a username from here:https://api.slack.com/methods/files.list/test
user_id = "U7W23907P"

total_file_count = 1
slack = Slacker(token)
response = slack.users.list()
users = response.body['members']
id2user = {}
for u in users:
  id2user[u["id"].encode("utf-8")] = u["name"].encode("utf-8")

while (currentpage > 0):
    print("---------------------------------")
    print("current page: " + str(currentpage))
    print("---------------------------------")
    response = slack.files.list(user=user_id,page=currentpage)
    files = response.body['files']
    amount = len(files)
    download_files(files)
    currentpage = currentpage + 1
    if amount == 0:
        currentpage = 0
