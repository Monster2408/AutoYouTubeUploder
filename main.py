from api import GoogleSpreadSheetsAPI as GSS

import http.client  # httplibはPython3はhttp.clientへ移行
import httplib2
import os
import random
import sys
import time
import glob

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error,
                        IOError,
                        http.client.NotConnected,
                        http.client.IncompleteRead,
                        http.client.ImproperConnectionState,
                        http.client.CannotSendRequest,
                        http.client.CannotSendHeader,
                        http.client.ResponseNotReady,
                        http.client.BadStatusLine)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
CLIENT_SECRETS_FILE = "client_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

    %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE, message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")  # print文
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % \
                        (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e
        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")
            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)



UPLOAD_MOVIE_DIR="D:\\SD\\動画\\エンコード\\shorts\\mlsclip\\未投稿"
UPLOAD_MOVIE_PREFIX="mlsclip"
UPLOAD_TIME=5


def upload_system():
    files = glob.glob(UPLOAD_MOVIE_DIR + os.sep + UPLOAD_MOVIE_PREFIX + "*.mp4")
    upload_time = UPLOAD_TIME
    # spreadsheet_list: list = GSS.getDatas()
    for file in files:
        if upload_time <= 0:
            break
        basename = os.path.basename(file)
        id = basename.replace(UPLOAD_MOVIE_PREFIX, "").replace(".mp4", "")


        print("ID: " + id)
        print("ファイル名: " + basename)

        upload_time = upload_time - 1


if __name__ == '__main__':

    upload_system()

    # argparser.add_argument("--file", required=True, help="Video file to upload")
    # argparser.add_argument("--title", help="Video title", default="Test Title")
    # argparser.add_argument("--description", help="Video description", default=PrivateVar.DESCRIPTION)
    # """
    #     20 ゲーム 
    #     22 ブログ 
    #     その他は→ https://qiita.com/nabeyaki/items/c3d0421538c8faacb130
    # """
    # argparser.add_argument("--category", default="20", help="Numeric video category. See https://developers.google.com/youtube/v3/docs/videoCategories/list") 
    # argparser.add_argument("--keywords", help="Video keywords, comma separated", default="")
    # argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES, default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    # args = argparser.parse_args()

    # if not os.path.exists(args.file):
    #     exit("Please specify a valid file using the --file= parameter.")

    # youtube = get_authenticated_service(args)
    # try:
    #     initialize_upload(youtube, args)
    # except HttpError as e:
    #     print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
