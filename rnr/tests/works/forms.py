'''
Created on Dec 22, 2014

@author: Coeurl
'''
import unittest

from processor.errors import WorkAlreadyExists, WorkEndTimeLessThenStart
from rnr.forms import WorkForm
from rnr.models import WorkType, Work

class test_WorkForm(unittest.TestCase):
    valid_form_data={'work_number': '000000',
           'work_type': WorkType.objects.get(id=1).slug,
           'work_start_datetime': '12/12/2014 14:00',
           'work_end_datetime': '12/12/2014 15:00',
           'work_region': 'blablabla'}
        
    def test_WorkForm_add(self):
        '''
        Add new work, check exceptions WorkAlreadyExists, WorkEndTimeLessThenStart
        '''
        workform = WorkForm(self.valid_form_data)
        self.assertTrue(workform.is_valid(), "WorkForm validation failed with data: "+str(self.valid_form_data))
        
    def test_WorkForm_work_exists(self):
        '''WorkAlreadyExists must be raised if work with this number is already exists'''
        
        existing_work_number = Work.objects.get(id=1).work_number
        invalid_form_data=self.valid_form_data.copy()
        invalid_form_data['work_number'] = existing_work_number
        workform = WorkForm(invalid_form_data)
        
        with self.assertRaises(WorkAlreadyExists):
            if workform.is_valid():
                work_obj = Work(workform.ceaned_data)
                work_obj.save()
        
    def test_WorkForm_worng_time(self):
        '''
        WorkEndTimeLessThenStart raised when start time >= end_time
        '''
        invalid_form_data=self.valid_form_data.copy()
        invalid_form_data['work_start_datetime']='12/12/2014 16:00'
        
        workform = WorkForm(invalid_form_data)
        with self.assertRaises(WorkEndTimeLessThenStart):
            workform.is_valid()
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testWorkView']
    unittest.main()