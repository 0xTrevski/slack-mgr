import os
import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ["SLACK_TOKEN"])

with open("inactive_channels.csv", "r") as csvfile:
    reader = csv.reader(csvfile)
    next(reader) # skip the header row
    for row in reader:
        channel_id = row[0]
        try:
            time.sleep(1) #leave this in to avoid rate limit
            response = client.conversations_archive(channel=channel_id)
            print("Archived channel {} (name: {})".format(channel_id, row[1]))
        except SlackApiError as e:
            print("Error archiving channel {}: {}".format(channel_id, e))
