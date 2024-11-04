({
    handleRecordChange: function(component, event, helper) {
        // Get the fetched record data
        var record = component.get("v.record");

        // Check if the record is not undefined and contains the HTML__c field
        if (record && record.HTML__c) {
            // Extract the HTML__c field value and set it to the brazeEmailHtml attribute
            component.set("v.brazeEmailHtml", record.HTML__c);
        }
    }
})