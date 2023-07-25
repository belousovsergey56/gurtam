"""Application for interaction with Wialon.

The application interacts with fms 4.

Features:

Admin-panel
Ability to add/remove users.
Remove/Change access permissions.
Works in a hierarchical system.
The user below cannot interact with the account above.
Ability to change password, e-mail (if you have rights)

Import to FMS4
Function for updating data on the leasing agreement on the portal wialon.
The user prepares an excel file with the necessary fields to update the object
card, the excel file template can be downloaded on the page of the same page.
The application parses the excel file into json
and uploads the data to the wialon.
If the object is not found, the script creates an object on the vialon,
then loads the data from the file.
The script sends a report on the execution to the mail to the authorized user.

Delete Bulk delete objects from groups.
The script parses an excel file and converts it to json.
Then it reads the mask of the group from the first line.
Saves all groups in the groups found by group mask to a list.
Saves all object id to a list.
Then, in a loop, from each group it removes
the list of objects by ID from the list.

Updating the fields for Karkade.
The script parses an excel file and converts it to json.
Finds an object by IMEI.
Updates fields Info1, Info4, 5, Info6, info7.
If fields not to be filled are not found, the script creates a field
and fills it with data.
The script saves the downloaded file as the last database snapshot.
The next time the data is updated, the downloaded file will be compared
with the snapshot and save to the json file only those objects that
do not match the data from the snapshot by any criterion.
This significantly reduces the processing time for uploading data
to the vialon from 5-6 hours to 40 minutes.

Updating the fields for GPBL.
The script parses an excel file and converts it to json.
Finds an object by IMEI.
Updates fields INN.
If fields not to be filled are not found, the script creates a field
and fills it with data.
"""
