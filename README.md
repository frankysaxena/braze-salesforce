# Braze Message Archiving into Salesforce via Amazon S3

This is a guide on how Emails (and generally Push/SMS) channels sent via Braze can be seen in Salesforce on a Contact record. Please note that this is an unofficial support guide including the code herein is provided as a guide and not for production.

![Braze -> S3 -> Salesforce](https://braze-images.com/appboy/communication/assets/image_assets/images/67292b90b4326e006374015f/original.png?1730751376)

## Message Archiving
[Message Archiving](https://www.braze.com/docs/user_guide/data_and_analytics/export_braze_data/message_archiving) is a Braze feature that saves a copy of messages sent to users for archival or compliance purposes to your AWS S3 bucket, Azure Blob Storage container or Google Cloud Storage bucket. It can also be used to retrieve personalized copies of messages for Sales/Support team members.

For full set up instructions please review the [documentation](https://www.braze.com/docs/user_guide/data_and_analytics/export_braze_data/message_archiving/#how-it-works).

## Amazon S3 Bucket
For this example, we have used Amazon S3 to set up 

## Salesforce


## Key Considerations
- Please ensure that storage in Salesforce can be quite costly. You can set up a hook to fetch the singular message copy upon click in the Visualforce component from your Cloud Storage bucket.