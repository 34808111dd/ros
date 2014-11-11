from django import forms
from models import DictRecord, Language, Contact, Client, Work, WorkType, OutageType, NotificationTemplate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
#import simplejson

#===============================================================================
# For CSVProcessor
#===============================================================================

class UploadFileForm(forms.Form):
    '''
    Upload Form used in views.csv_parser
    Sample:
            self.options['output_encoding']='1251'
            self.options['output_format'] = [';"']
            self.options['ignore_decode_errors'] = "Yes"
            self.options['time_operation'] = "minus"
            self.options['time_amount'] = '4:00'
            self.options['process_cols_dict'] = '8' #count from 1, not from 0
            self.options['process_cols_time'] =  '2'
            self.options['cut_client_name'] =  'Yes'
            self.options['add_region'] = 'Yes'
            self.options['add_region_based_on'] = '4'
            self.options['add_region_new_column_number'] = '10'
            self.options['start_process_from'] = '0'
    '''
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        self.fields['output_encoding'].label = "Encoding:"
        self.fields['output_format'].label = "Format:"
        self.fields['ignore_decode_errors'].label = "Ignore errors:"
        self.fields['time_operation'].label = "Time + or -:"
        self.fields['time_amount'].label = "Time in hours:"
        self.fields['process_cols_dict'].label = "Translate columns:"
        self.fields['process_cols_time'].label = "Time columns:"
        self.fields['cut_client_name'].label = "Trim client's name:"
        self.fields['add_region'].label = "Add Regions:"
        self.fields['add_region_based_on'].label = "Look at column:"
        self.fields['add_region_new_column_number'].label = "New Column number:"
        self.fields['start_process_from'].label = "Start from row:"
        
    
    input_file = forms.FileField()

# optional

    output_encoding = forms.ChoiceField( choices = ( ('1251','1251'), ('utf-8','utf-8') ), label="Output encoding" )
    output_format = forms.ChoiceField( choices = ( ('standard','standard'), ('ignored','ignored') ) )
    ignore_decode_errors = forms.ChoiceField( choices = ( ('Yes','Yes'), ('No','No') ) )
    time_operation = forms.ChoiceField( choices = ( ('minus','minus'), ('plus','plus') ) )
    time_amount = forms.TimeField()
    process_cols_dict = forms.CharField(max_length=20)
    process_cols_time = forms.CharField(max_length=20)
    cut_client_name = forms.ChoiceField( choices = ( ('Yes','Yes'), ('No','No') ) )
    add_region = forms.ChoiceField( choices = ( ('Yes','Yes'), ('No','No') ) )
    add_region_based_on = forms.CharField(max_length=20)
    add_region_new_column_number = forms.CharField(max_length=20)
    start_process_from = forms.CharField(max_length=20)
    

class NewRecordForm(forms.Form):
    '''
    Add records to dictionary form. Used in views.csv_parser
    '''
    init_word = forms.CharField()
    replace_word = forms.CharField()

class RecordsForm(forms.Form):
    '''
    All records form, every record displayed as checkbox (for deletion usability)
    '''
    records = DictRecord.objects.all().order_by('replace_word')
    _l = ( (x.init_word, x.replace_word) for x in records )
    OPTIONS = tuple(_l)
    Records = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class':'css-checkbox'}), choices=OPTIONS)
    
    
    
    
#===============================================================================
# For RNR Application
#===============================================================================


class MultiEmailField(forms.Field):
    '''
    Multiemail field for django object.
    Every email should be valid (should allow usage of non-unique email addresses)
    '''
    def to_python(self, value):
        "Normalize data to a list of strings."
        # Return an empty list if no input was given.
        if not value:
            return []
        value = value.replace(" ","")
        return set(value.split(','))

    def validate(self, value):
        "Check if value consists only of valid emails."
        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)
        for email in value:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("Email " + email + " is not in valid format, use user@host.dom, user2@host2.dom")
            if Contact.objects.filter(contact_email=email).exists():
                raise forms.ValidationError("Email " + email + " already exists")

class ClientNameField(forms.CharField):
    def validate(self, value):
        "Check if value consists only of valid emails."
        # Use the parent's handling of required fields, etc.
        super(ClientNameField, self).validate(value)
        if Client.objects.filter(client_name=value).exists():
                raise forms.ValidationError("Client " + value + " already exists")

class WorkNumber(forms.CharField):
    def validate(self, value):
        # Use the parent's handling of required fields, etc.
        super(WorkNumber, self).validate(value)
        if Work.objects.filter(work_number=value).exists():
                raise forms.ValidationError("Work with number " + value + " already exists")


class ClientForm(forms.Form):
    '''
    Form for adding new client.
    '''
    client_name = ClientNameField(max_length = 128)
    client_language = forms.ModelChoiceField(queryset=Language.objects.all(), to_field_name="slug")
    client_emails = MultiEmailField()
    
class WorkForm(forms.Form):
    '''
    Form for adding new work.
    '''
    work_number = WorkNumber(max_length = 128)
    work_type = forms.ModelChoiceField(queryset=WorkType.objects.all(), to_field_name="slug")
    work_circuit = forms.CharField(max_length = 128)
    work_start_datetime = forms.DateTimeField(input_formats=["%m/%d/%Y %H:%M"])
    work_end_datetime = forms.DateTimeField(input_formats=["%m/%d/%Y %H:%M"])
    work_region = forms.CharField(max_length=128)

class OutageForm(forms.Form):
    '''
    Add outage for notification.
    '''
    outage_type = forms.ModelChoiceField(queryset=OutageType.objects.all(), to_field_name="slug")
    outage_work = forms.ModelChoiceField(queryset=Work.objects.all(), to_field_name="slug")
    outage_client = forms.ModelChoiceField(queryset=Client.objects.all(), to_field_name="slug")
    outage_circuit = forms.CharField(max_length=128)
    outage_start_date = forms.DateTimeField(input_formats=["%m/%d/%Y %H:%M"])
    outage_end_date = forms.DateTimeField(input_formats=["%m/%d/%Y %H:%M"])
    outage_description = forms.CharField(max_length=128)
    
class NotificationForm(forms.Form):
    '''
    Add notification for client
    '''
    notification_client = forms.ModelChoiceField(queryset=Client.objects.all(), to_field_name="slug")
    notification_work = forms.ModelChoiceField(queryset=Work.objects.all(), to_field_name="slug")
    notification_template = forms.ModelChoiceField(queryset=NotificationTemplate.objects.all(), to_field_name="slug")
    notification_complete_text = forms.CharField(widget=forms.Textarea)
    