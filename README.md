# Braze Message Archiving into Salesforce via Amazon S3

This is a guide on how Emails (and generally Push/SMS) channels sent via Braze can be seen in Salesforce on a Contact record. Please note that this is an unofficial support guide including the code herein is provided as a guide and not for production.

![Braze -> S3 -> Salesforce](https://braze-images.com/appboy/communication/assets/image_assets/images/67292b90b4326e006374015f/original.png?1730751376)

## Message Archiving
[Message Archiving](https://www.braze.com/docs/user_guide/data_and_analytics/export_braze_data/message_archiving) is a Braze feature that saves a copy of messages sent to users for archival or compliance purposes to your AWS S3 bucket, Azure Blob Storage container or Google Cloud Storage bucket. It can also be used to retrieve personalized copies of messages for Sales/Support team members.

For full set up instructions please review the [documentation](https://www.braze.com/docs/user_guide/data_and_analytics/export_braze_data/message_archiving/#how-it-works).

## Amazon S3 Bucket
For this example, we have used Amazon S3 as a destination from Braze. The gzipped JSON file will be dropped into the bucket for each message sent to a user through the selected channels (email, SMS or push). We have set up a Lambda function to trigger off an event. This event is whenever this gzipped JSON file is uploaded to the bucket as shown below.

1. The trigger configuration can be set up using Lambda > Add triggers, and then ensure you are using S3 as the template for the trigger. The below example configuration be set up to trigger the Lambda function whenever an object is created in the S3 bucket with a suffix of .json.gz.

```
{
    Bucket arn: arn:aws:s3:::xxx
    Event types: s3:ObjectCreated:*
    isComplexStatement: No
    Notification name: xxx
    Service principal: s3.amazonaws.com
    Source account: xxx
    Statement ID: xxx
    Suffix: .json.gz        
}
```

2. Create the function now. This can be in the form of a Python script, an example of which is in this repo as ```lambda_script.py```. Some configuration may be required in the Lambda instance to deploy the function with the appropriate dpenedencies, i.e. deploy the script as a virtualenv folder with the required dependencies installed as a .zip file. 

3. (Optional) You can also create a test event to see if the function executes and runs successfully (i.e. Salesforce Contact object gets updated with the latest Email object).

[S3BucketExample](https://braze-images.com/appboy/communication/assets/image_assets/images/6729330926f8e900706b25ef/original.png?1730753289)



## Salesforce


## Key Considerations
- Please ensure that storage in Salesforce can be quite costly. You can set up a hook to fetch the singular message copy upon click in the Visualforce component from your Cloud Storage bucket.