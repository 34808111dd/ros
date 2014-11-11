'''
Created on Oct 21, 2014

@author: Coeurl
'''

class TimeParseError(Exception):
    '''
    Raised when cannot parse time, should say work_number and string in which was error
    '''
    def __init__(self, problem_string):
        self.problem_string = problem_string
        
    def __str__(self):
        return self.problem_string
    
class RecordParseError(Exception):
    '''
    Reraised on other substring parse exception ti provide work number.
    ''' 
    def __init__(self, work_number, problem_string):
        self.work_number = work_number
        self.problem_string = problem_string
        
    def __str__(self):
        return self.work_number + " " + self.problem_string