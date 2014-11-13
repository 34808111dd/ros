'''
Created on Oct 21, 2014

@author: Coeurl
'''

class AppError(Exception):
    '''
    Every error should rerise this error with appropriate type.
    Should return a json object {success:false, error:error_string}
    '''
    def __init__(self, type_id, error_string):
        self.type_id = type_id
        self.error_string = error_string
        



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
    
    
'''
Errors:
Types:
    - File Parsing Error
    - Invalid value in field (Non-unique, not formatted, etc)
    - Database error
    - SMTP error
'''