#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import xlrd
import datetime
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from models import Audit

# [START waste_item]
class WasteItem(ndb.Model):
    id = ndb.IntegerProperty()
    date = ndb.DateProperty()
    '''
    These are the current column names in the upload template - can turn them into properties of the model

    Line
    Date
    Inspection Type
    Lead Appraiser
    Country
    Province
    Regional District
    City/Town
    Neighbourhood
    Street Number
    Street Name
    Apt. # (if applicable)
    Postal Code
    Building Type
    Building Subtype
    # of Inhabitants/Personnel
    Primary Material
    Secondary Material
    Tertiary/Quaternary 
    Disposal Method
    Waste kg 
    Recycled kg 
    Reused kg 
    Total kg 
    kg/inhabitant 
    Additional Comments 
    '''


# [END waste_item]


# [START spreadsheet_import]
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        process_spreadsheet(blob_info)

        blobstore.delete(blob_info.key())  # optional: delete file after import
        self.redirect("/")

def process_spreadsheet(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    #reader = csv.reader(blob_reader, delimiter=';')
    wb = xlrd.open_workbook(file_contents=blob_reader.read())
    sh = wb.sheet_by_index(0) #get the first worksheet in the workbook
    # the headers are currently on line 8 of the spreadsheet, fyi.
    for rownum in range(8,sh.nrows):
    #for row in reader:
    #need to map all of the columns here - it is done by index of the column per ordering above
    #see the 'UploadPlaceholder as a simpler example, also included some code for getting data value from a spreadsheet
        date, data, value = sh.row_values(rownum)
        entry = WasteItem(date=datetime.date(1900, 1, 1) + datetime.timedelta(int(date)-2), data=data, value=int(value))
        entry.put()

# [END spreadsheet_import]
