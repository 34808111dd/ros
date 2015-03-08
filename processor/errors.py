'''
Created on Oct 21, 2014

@author: Coeurl
'''
import simplejson
from rnr.models import Language, AppErrorDescription, AppErrorType

class AppError(Exception):
    '''
    Every error should rerise this error with appropriate type.
    Should return a json object {success:false, error:error_string}
    '''
    def __init__(self, type_id, language='en', error_string=""):
        self.type_id = type_id
        self.error_string = error_string
        self.language = language
        
        lang_obj = Language.objects.get(language_name=self.language)
        app_error_type_obj = AppErrorType.objects.get(apperror_type=self.type_id)
        self.app_error_desc_obj = AppErrorDescription.objects.get(apperror_desc_type=app_error_type_obj, apperror_desc_lang=lang_obj)
        self.error_in_json=simplejson.dumps({"success":False, "error":self.app_error_desc_obj.apperror_desc_desc+self.error_string})
        
class FileParseError():
    '''
    Raised on bad format, has type 11
    '''
    def __init__(self, error_string, type_id=11):
        self.type_id = type_id
        self.error_string = error_string

class TimeParseError(Exception):
    '''
    Raised when cannot parse time, should say work_number and string in which was error
    has type 15
    '''
    def __init__(self, error_string, type_id=15):
        self.error_string = error_string
        self.type_id = type_id
        
    def __str__(self):
        return self.error_string


class UnknownWorkConditionError():
    '''
    Raised on unknown condition found
    '''
    def __init__(self, error_string, type_id=14):
        self.error_string = error_string
        self.type_id = type_id
        
    def __str__(self):
        return self.error_string


class UnknownClient():
    '''
    Raised on unknown client found
    '''
    def __init__(self, error_string, type_id=12):
        self.error_string = error_string
        self.type_id = type_id
        
    def __str__(self):
        return self.error_string

class BlankWorkNumber():
    '''
    '''
    def __init__(self, error_string, type_id=13):
        self.error_string = error_string
        self.type_id = type_id
        
    def __str__(self):
        return self.error_string


class WorkAlreadyExists():
    '''
    raised on manual work add.
    '''
    def __init__(self, error_string, type_id=16):
        self.error_string = error_string
        self.type_id = type_id
        
    def __str__(self):
        return self.error_string


class WorkEndTimeLessThenStart():
    '''
    raised if end date less or equal then start date
    '''
    def __init__(self, error_string, type_id=17):
        self.error_string = error_string
        self.type_id = type_id
        
    def __str__(self):
        return self.error_string


class ClientAlreadyExists():
    '''
    raised if client already exists by form ClientForm
    '''
    def __init__(self, error_string, type_id=42):
        self.error_string = error_string
        self.type_id = type_id
        
    def __str__(self):
        return self.error_string

class RecordParseError(Exception):
    '''
    Reraised on other substring parse exception to provide work number.
    ''' 
    def __init__(self, work_number, problem_string):
        self.work_number = work_number
        self.problem_string = problem_string
        
    def __str__(self):
        return self.work_number + " " + self.problem_string
    
    
class InvalidDictRecord():
    '''
    used in forms.DictWordField
    '''
    def __init__(self, error_string, type_id=51):
        self.error_string = error_string
        self.type_id = type_id
        
    def __str__(self):
        return self.error_string
'''
Errors:
Types:
    - File Parsing Error
    - Invalid value in field (Non-unique, not formatted, etc)
    - Database error
    - SMTP error
'''