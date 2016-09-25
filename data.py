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
    # ItemId = ndb.IntegerProperty()  # Represented by entity key, which is auto-generated after we store object to data store
    EntryLineNum = ndb.IntegerProperty() # Shouldn't really be needed, but just in case
    AppraisalDate = ndb.DateProperty()
    InspectionType = ndb.StringProperty()
    LeadAppraiser = ndb.StringProperty()
    Country = ndb.StringProperty()
    Province = ndb.StringProperty()
    RegionalDistrict = ndb.StringProperty()
    City_Town = ndb.StringProperty()
    Neighbourhood = ndb.StringProperty()
    StreetNumber = ndb.IntegerProperty()
    StreetName = ndb.StringProperty()
    ApartmentNumer = ndb.IntegerProperty()
    PostalCode = ndb.StringProperty()
    BuildingType = ndb.StringProperty()
    NumberInhabitants = ndb.IntegerProperty()
    PrimaryMaterial = ndb.StringProperty() # TODO read this as csv list
    SecondaryMaterial = ndb.StringProperty() # TODO read this as csv list
    TertQuatMaterial = ndb.StringProperty() # TODO read this as csv list
    DisposalMethod = ndb.StringProperty()
    WasteKg = ndb.FloatProperty()
    RecycledKg = ndb.FloatProperty()
    ReusedKg = ndb.FloatProperty()
    TotalKg = ndb.FloatProperty()
    KgInhabitant = ndb.FloatProperty()
    AdditionalComments = ndb.StringProperty()
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
    # So row[8] is the ninth row on the spreadsheet, where the actual data starts
    for rownum in range(8,sh.nrows):
    #for row in reader:
    #need to map all of the columns here - it is done by index of the column per ordering above
    #see the 'UploadPlaceholder as a simpler example, also included some code for getting data value from a spreadsheet
        #date, data, value = sh.row_values(rownum)
        #entry = WasteItem(date=datetime.date(1900, 1, 1) + datetime.timedelta(int(date)-2), data=data, value=int(value))
        #entry.put()
        # Columns A-Z
        #for colnum in range(0,25):
        line = int(sh.cell_value(rownum,0))
        date = (xlrd.xldate.xldate_as_datetime(sh.cell_value(rownum,1),wb.datemode)).date()
        ins_type = str(sh.cell_value(rownum,2))
        appraiser = str(sh.cell_value(rownum,3))
        ctry = str(sh.cell_value(rownum,4))
        prov = str(sh.cell_value(rownum,5))
        reg_dist = str(sh.cell_value(rownum,6))
        city = str(sh.cell_value(rownum,7))
        nebhood = str(sh.cell_value(rownum,8))
        str_num = int(sh.cell_value(rownum,9))
        str_nam = str(sh.cell_value(rownum,10))
        apt_num = int(sh.cell_value(rownum,11))
        poc_code = str(sh.cell_value(rownum,12))
        bld_type = str(sh.cell_value(rownum,13))
        sbd_type = str(sh.cell_value(rownum,14))
        numb_inh = int(sh.cell_value(rownum,15))
        prim_mat = str(sh.cell_value(rownum,16))
        seco_mat = str(sh.cell_value(rownum,17))
        terq_mat = str(sh.cell_value(rownum,18))
        disp_mth = str(sh.cell_value(rownum,19))
        waste_kg = float(sh.cell_value(rownum,20))
        rcycd_kg = float(sh.cell_value(rownum,21))
        rused_kg = float(sh.cell_value(rownum,22))
        total_kg = float(sh.cell_value(rownum,23))
        kg_inhab = float(sh.cell_value(rownum,24))
        add_commnts = str(sh.cell_value(rownum,25))
        
        entry = WasteItem(EntryLineNum = line,AppraisalDate = date,InspectionType = ins_type,LeadAppraiser = appraiser,Country = ctry,Province = prov,RegionalDistrict = reg_dist,City_Town = city,Neighbourhood = nebhood,StreetNumber = str_num,StreetName = str_nam,ApartmentNumer = apt_num,PostalCode = poc_code,BuildingType = bld_type,BuildingSubType = sbd_type,NumberInhabitants = numb_inh,PrimaryMaterial = prim_mat,SecondaryMaterial = seco_mat,TertQuatMaterial = terq_mat,DisposalMethod = disp_mth,WasteKg = waste_kg,RecycledKg = rcycd_kg,ReusedKg = rused_kg,TotalKg = total_kg,KgInhabitant = kg_inhab,AdditionalComments = add_commnts)
        entry.put()
        
# [END spreadsheet_import]
