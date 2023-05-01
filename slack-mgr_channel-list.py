import os
import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import datetime
import time
from tqdm import tqdm

# Initialize a Slack API client with a bot token
client = WebClient(token=os.environ["SLACK_TOKEN"])

# Set the time threshold for when a channel is considered inactive
time_threshold = datetime.datetime.now() - datetime.timedelta(days=540) # 18 months

# Initialize a CSV file to store the results
with open("inactive_channels.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Channel ID", "Channel Name", "Last Message Date"])

    # Set up pagination
    cursor = None
    while True:
        try:
            # Get a page of public channels, limited to 200 results
            response = client.conversations_list(
                types="public_channel",
                limit=200,
                cursor=cursor
            )
            channels = response["channels"]
            cursor = response["response_metadata"]["next_cursor"]
        except SlackApiError as e:
            print("Error getting channel list: {}".format(e))
            break

        # Iterate through each public channel and check its message history
        for channel in tqdm(channels, desc="Checking channels"):
            # Skip archived channels
            if channel["is_archived"]:
                continue

            try:
                # Use rate limiting to avoid hitting API rate limits
                time.sleep(1)
                
                response = client.conversations_history(
                    channel=channel["id"],
                    limit=1
                )
                messages = response["messages"]
            except SlackApiError as e:
                print("Error getting channel history for channel {}: {}".format(channel["name"], e))
                continue

            # Check if the most recent message was sent more than 18 months ago
            if len(messages) > 0:
                latest_message_time = datetime.datetime.fromtimestamp(float(messages[0]["ts"]))
                if latest_message_time < time_threshold:
                    writer.writerow([channel["id"], channel["name"], latest_message_time.strftime("%Y-%m-%d")])

        # If there are no more pages, break out of the loop
        if not cursor:
            break

# Print a message indicating where the results are stored
print("Results saved to inactive_channels.csv")
