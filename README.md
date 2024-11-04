# Braze Message Archiving into Salesforce via Amazon S3

This is a guide on how Emails (and generally Push/SMS) channels sent via Braze can be seen in Salesforce on a Contact record. Please note that this is an unofficial support guide including the code herein is provided as a guide and not for production.

![Braze -> S3 -> Salesforce](https://braze-images.com/appboy/communication/assets/image_assets/images/67292b90b4326e006374015f/original.png?1730751376)

## Message Archiving
[Message Archiving](https://www.braze.com/docs/user_guide/data_and_analytics/export_braze_data/message_archiving) is a Braze feature that saves a copy of messages sent to users for archival or compliance purposes to your AWS S3 bucket, Azure Blob Storage container or Google Cloud Storage bucket. It can also be used to retrieve personalized copies of messages for Sales/Support team members.

For full set up instructions of Message Archiving in Braze, please review the [documentation](https://www.braze.com/docs/user_guide/data_and_analytics/export_braze_data/message_archiving/#how-it-works).

## S3 Bucket
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

2. Create the function now. This can be in the form of a Python script, an example of which is in this repo as ```lambda_script.py```. Some configuration may be required in the Lambda instance to deploy the function with the appropriate dpenedencies, i.e. deploy the script as a virtualenv folder with the required dependencies installed as a .zip file. Additionally ensure that your API endpoint for Salesforce is accounting for the Custom Object created.

3. (Optional) You can also create a test event to see if the function executes and runs successfully (i.e. Salesforce Contact object gets updated with the latest Email object).


![S3BucketExample](https://braze-images.com/appboy/communication/assets/image_assets/images/6729330926f8e900706b25ef/original.png?1730753289)


## Salesforce Setup

To display the Braze email HTML content on the Contact record, we need to create a Lightning component that renders the HTML content safely. This component will be added to the Contact page layout and will display the HTML content of the selected BrazeEmail record.


### 1. Create Custom Object
- In Salesforce Setup, navigate to Object Manager
- Click "Create" > "Custom Object"
- Fill in the following details:
  - Label: BrazeEmail
  - Plural Label: BrazeEmails
  - Object Name: BrazeEmails__c
  - Enable the relevant features as needed (Reports, Search, etc.)

### 2. Configure Custom Fields
- Add the following custom fields to the BrazeEmail object:
    - Name: Campaign Name (Text)
    - HTML__c: HTML Content (Long Text Area, with HTML enabled)
    - Contact__c: Contact (Lookup Relationship to Contact object)

### 3. Create Lightning Component
Create the following files in your Salesforce org:

1. **Lightning Component** (`BrazeEmailPreview.cmp`):
 - Located in: `force-app/main/default/aura/BrazeEmailPreview/`
 - Displays the HTML content of the Braze email in a formatted view
 - Uses `lightning:formattedRichText` to safely render HTML content

2. **Component Controller** (`BrazeEmailPreviewController.js`):
 - Located in: `force-app/main/default/aura/BrazeEmailPreview/`
 - Handles the record data changes
 - Updates the HTML preview when a record is loaded

### 4. Configure Page Layouts
1. Add BrazeEmails Related List to Contact Layout:
 - Go to Setup > Object Manager > Contact
 - Navigate to Page Layouts
 - Edit the relevant layout
 - Add the BrazeEmails related list to the layout
 - Configure the columns to display relevant information

2. Add Lightning Component:
 - In the same layout editor
 - Drag the BrazeEmailPreview component to your desired location
 - Save the layout

### 5. Set Up API Access
1. Create Connected App:
 - Go to Setup > App Manager > New Connected App
 - Fill in basic information (name, email, etc.)
 - Enable OAuth Settings
 - Set Callback URL to your domain or https://localhost for testing
 - Under Selected OAuth Scopes, add "Full access (full)"
 - Under OAuth Policies, enable "Client Credentials Flow"
 - Save and note down the Consumer Key and Secret

2. Configure API User:
 - Ensure API Enabled permission
 - Grant access to BrazeEmail custom object
 - Set Create/Read/Edit permissions
 - Generate Security Token if needed

3. Store Credentials in AWS:
 ```json
 {
   "SF_CLIENT_ID": "your_consumer_key",
   "SF_CLIENT_SECRET": "your_consumer_secret",
   "SF_USERNAME": "your_username",
   "SF_PASSWORD": "your_password",
   "SF_SECURITY_TOKEN": "your_security_token"
 }
 ```

#### Component Behavior
- The component automatically loads when a BrazeEmail record is accessed
- It safely renders the HTML content stored in the `HTML__c` field
- If no HTML content is available, it displays a "No HTML content available" message
- The content is displayed in a Lightning card with a formatted view


## Key Considerations
- Storage in Salesforce can be quite costly. You can set up a hook to fetch the singular message copy upon click in the Lightning component from your Cloud Storage bucket.