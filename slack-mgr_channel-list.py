import os
import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import datetime
import time

client = WebClient(token=os.environ["SLACK_TOKEN"]) #use app token for API from channel manager app

# Set the amount of time for when a channel is considered dead
time_threshold = datetime.datetime.now() - datetime.timedelta(days=720) # 24 months

with open("inactive_channels.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Channel ID", "Channel Name", "Last Message Date"])
    cursor = None
    while True:
        try:
            response = client.conversations_list(
                types="public_channel",
                limit=100, #limit conversations to avoid rate limit
                cursor=cursor
            )
            channels = response["channels"]
            cursor = response["response_metadata"]["next_cursor"]
        except SlackApiError as e:
            print("Error getting channel list: {}".format(e))
            break

        for channel in channels:
            if channel["is_archived"]: # ignore already archived channels
                continue

            try:
                time.sleep(2) # leave in, slows requests to avoid rate limit
                response = client.conversations_history(
                    channel=channel["id"],
                    limit=1
                )
                messages = response["messages"]
            except SlackApiError as e:
                print("Error getting channel history for channel {}: {}".format(channel["name"], e))
                continue

            if len(messages) > 0:
                latest_message_time = datetime.datetime.fromtimestamp(float(messages[0]["ts"]))
                if latest_message_time < time_threshold:
                    writer.writerow([channel["id"], channel["name"], latest_message_time.strftime("%Y-%m-%d")])

        if not cursor:
            break

print("Results saved to inactive_channels.csv")
