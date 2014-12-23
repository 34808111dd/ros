'''
Created on Dec 23, 2014

@author: Coeurl
'''

import unittest
from django.db import IntegrityError

from processor.errors import BlankWorkNumber, FileParseError, TimeParseError, UnknownWorkConditionError,\
UnknownClient, WorkAlreadyExists, WorkEndTimeLessThenStart, ClientAlreadyExists
from processor import tmp_csv_proc
from rnr.models import Work
from rnr.forms import WorkForm, ClientForm


def try_file_parse(file_name):
    with open(file_name,'rt') as f:
        work_parser = tmp_csv_proc.WorkContainer(f)
        work_parser.parse("CheckErrors", "IgnoreNew")


class TestErrors(unittest.TestCase):
    fixtures=['initial_data.json']
    
#    def setUp(self):
#        print 'doing new objects'
#        lang_objects = Language.objects.all()
#        print lang_objects
#        for local_lang in lang_objects:
#            local_lang_object = Language(language_name=local_lang.language_name)
#            #local_lang_object.save()
    
    def test_blank_work_number(self):
#===========================================================================
# Raise BlankWorkNumber if work number is blank
#===========================================================================
        with self.assertRaises(BlankWorkNumber):
            try_file_parse('./tests/csv_samples/test_blank_work_number.csv')
            
    
    def test_file_parse_error(self):
#===============================================================================
# Raise FileParseError if file has wrong format
#===============================================================================
        with self.assertRaises(FileParseError):
            try_file_parse('./tests/csv_samples/test_file_parse_error.csv')
    
    def test_time_parse_error(self):
#===============================================================================
# Raise TimeParseError if time has wrong format
#===============================================================================
        with self.assertRaises(TimeParseError):
            try_file_parse('./tests/csv_samples/test_time_parse_error.csv')
    
    def test_unknown_work_condition(self):
#===============================================================================
# Raise UnknownWorkConditionError if file has wrong work condition
#===============================================================================
        with self.assertRaises(UnknownWorkConditionError):
            try_file_parse('./tests/csv_samples/test_unknown_work_condition.csv')
    
    def test_unknown_client(self):
#===============================================================================
# Raise UnknownWorkConditionError if file has wrong work condition
#===============================================================================
        with self.assertRaises(UnknownClient):
            try_file_parse('./tests/csv_samples/test_unknown_client.csv')
    
    
    def test_work_already_exists(self):
#===============================================================================
# Check for integrity error if work number exists (yes, another dumb test)
#===============================================================================
        with self.assertRaises(IntegrityError):
            existing_work_obj = Work.objects.get(id=1)
            new_work_obj = Work(work_number=existing_work_obj.work_number,\
                                work_type = existing_work_obj.work_type,\
                                work_start_date = existing_work_obj.work_start_date,\
                                work_end_date = existing_work_obj.work_end_date,\
                                work_region = existing_work_obj.work_region,\
                                work_state = existing_work_obj.work_state,
                                work_added = existing_work_obj.work_added)
            new_work_obj.save()
    
    
    def test_work_already_exists_form(self):
#===============================================================================
# Check manually added work, form must raise an exception when work_number already exists
#===============================================================================
        new_work_form = WorkForm(data={
        "work_number": "00/1401477",
        "work_type" : "fdBBfbb4BFAc",
        "work_start_datetime" : "12/12/2014 3:00",
        "work_end_datetime": "12/12/2014 4:00",
        "work_region": "AFc6F6DcD7eC"})
        with self.assertRaises(WorkAlreadyExists):
            new_work_form.is_valid()
            
    
    def test_client_already_exists_form(self):
#===============================================================================
# Check manually added work, form must raise an exception when work_number already exists
#===============================================================================
        new_client_form = ClientForm(data={
        "client_name": "AT&T",
        "client_display_name" : "fdBBfbb4BFAc",
        "client_language" : "9Fb2cfd4f1Eb",
        "client_emails": "aa@aa.aa"})
        with self.assertRaises(ClientAlreadyExists):
            new_client_form.is_valid()
    
    
    def test_work_end_data_less_then_start(self):
#===============================================================================
# Raise WorkEndTimeLessThenStart on manual work addition
#===============================================================================
        new_work_form = WorkForm(data={
        "work_number": "00/1111401477",
        "work_type" : "fdBBfbb4BFAc",
        "work_start_datetime" : "12/12/2014 4:00",
        "work_end_datetime": "12/12/2014 3:00",
        "work_region": "AFc6F6DcD7eC"})
        with self.assertRaises(WorkEndTimeLessThenStart):
            new_work_form.is_valid()
        
if __name__ == "__main__":
    unittest.main()
