'''
Created on Aug 22, 2014

@author: Coeurl
'''

import csv
import datetime
from rnr.models import DictRecord
import os.path


class CSVParseOptions(object):
    '''
class for parsing settings
time_amount     u'4'
encoding_choosen u'1251'
csrfmiddlewaretoken u'SPNLNV0vcHYQ0bTqS2DrMq3UDsueHeNy'
time_operation     u'minus'
rows_to_translate  u'8'
    
    
    
    output_encoding
    output_format
    ignore_decode_errors
    
    time_operation
    time_amount
    
    process_cols_dict
    process_cols_time
    
    cut_client_name
    
    add_region
    add_region_based_on
    
    
    start_process_from
    
    '''
    pass
    def __init__(self, input_options={}):
        self.options = {}
#default parse settings
        self.options['output_encoding']='1251'
        self.options['output_format'] = 'standard'
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
        
        if input_options:
            self.options.update(input_options)
            

class CSVProcessor(object):
    '''
    class to process uploaded csv file
    
    '''


    def __init__(self, input_file_descriptor, output_file_descriptor, parse_options=CSVParseOptions()):
        '''
        Constructor
        input - file contents as bytes
        '''
        self.input_file_descriptor = input_file_descriptor
        self.output_file_descriptor = output_file_descriptor
        self.parse_options = parse_options
        
        
    def process_file(self):
        '''
        Read and parse file contents
        '''
        csv_reader = csv.reader(self.input_file_descriptor, delimiter=';', quotechar='"')
        
        output_file = csv.writer( self.output_file_descriptor, delimiter=';', quotechar='"' )        
        input_file_contents = [_row for _row in csv_reader]
        
    #fill temporary dictionary with objects
        my_dict_objects = DictRecord.objects.all()
        translation_dict = {}
        for x in my_dict_objects:
            translation_dict[x.init_word]=x.replace_word
        
        start_row_number = None
        x = 0
        for i in input_file_contents:
            if i[0]=='1':
                start_row_number = x
                break
            else:
                x += 1
        print start_row_number
        
#         if start_row_number:
#             for input_row in input_file_contents[start_row_number:]:
#                 output_row = self.process_row(input_row, translation_dict)
#                 output_file.writerow(output_row)
#         else:
        
        x = 0
        
        for input_row in input_file_contents:
            
            output_row = input_row
            if x > start_row_number:
                output_row = self.process_row(input_row, translation_dict)
            
            elif x == start_row_number-1 and self.parse_options.options['add_region']=="Yes":
                output_row.append("Region")
            
            elif x == start_row_number and self.parse_options.options['add_region']=="Yes":
                output_row.append("10")


            output_file.writerow(output_row)
            
            x += 1
            
            
        return self.output_file_descriptor
        
    
    
    def process_row(self, csv_row, translation_dict):
        '''
        Process one row
        '''
        if self.parse_options.options['process_cols_dict']:
            for x in self.parse_options.options['process_cols_dict'].split(' '):
                int_x = int(x)
                if int(int_x)>0:
                    csv_row[int_x -1] = self.translate_cell(csv_row[int_x-1], translation_dict)
                    
        if self.parse_options.options['process_cols_time']:
            for x in self.parse_options.options['process_cols_time'].split(' '):
                int_x = int(x)
                if int(int_x)>0:
                    csv_row[int_x -1] = self.convert_time_cell(csv_row[int_x-1])
                    
        if self.parse_options.options['cut_client_name'] == 'Yes':
            csv_row[0] = self.cut_client_cell(csv_row[0])
            
            
        if self.parse_options.options['add_region'] == 'Yes':
            col_based_num = int(self.parse_options.options['add_region_based_on'])-1
            csv_row.append(self.add_region_cell(csv_row[col_based_num]))
             
#         print csv_row
        return csv_row
#     def translate_cell(self, csv_row, csv_row_number=7, time_row_number=1):
    
    def translate_cell(self, cell_contents, translation_dict):
        '''
        translates cell text based on translation_dict
        '''
        cell_contents = cell_contents.decode(self.parse_options.options['output_encoding'])
        tmpstr = cell_contents
        
        for k,v in translation_dict.items():
            f_index = tmpstr.lower().find(k.lower())
    
            while f_index != -1:
                tmpstr = tmpstr[:f_index] + v + tmpstr[f_index+len(k):]
                f_index = tmpstr.lower().find(k.lower())
                
        return tmpstr.encode(self.parse_options.options['output_encoding'])
        
    def convert_time_cell(self, time_string):
        
            decoded_string = time_string.decode(self.parse_options.options['output_encoding'])
            
            dates_only = [x for x in time_string.split(' ') if len(x)>2]
            
            h = int(self.parse_options.options['time_amount'].hour)
            m = int(self.parse_options.options['time_amount'].minute)
            delta = datetime.timedelta(hours=h, minutes=m)
            
            if len(dates_only) == 3:
                
                work_date = [int(x) for x in dates_only[0].split('.')]
                from_time = [int(x) for x in dates_only[1].split(':')]
                to_time = [int(x) for x in dates_only[2].split(':')]
                
                start_date = datetime.datetime(work_date[-1], work_date[-2], work_date[-3], from_time[0], from_time[1])
                end_date = datetime.datetime(work_date[-1], work_date[-2], work_date[-3], to_time[0], to_time[1])
        
                if self.parse_options.options['time_operation'] == 'plus':
                    start_date += delta
                    end_date += delta
                elif self.parse_options.options['time_operation'] == 'minus':
                    start_date -= delta
                    end_date -= delta
        
                result_string = "From %s To %s (UTC)" %(start_date.strftime('%d.%m.%Y %H:%M'), end_date.strftime('%d.%m.%Y %H:%M'))
            
            elif len(dates_only) == 4:
                
                work_date = [int(x) for x in dates_only[1].split('.')]
                work_end_date = [int(x) for x in dates_only[3].split('.')]
        
                from_time = [int(x) for x in dates_only[0].split(':')]
                to_time = [int(x) for x in dates_only[2].split(':')]
                
                start_date = datetime.datetime(work_date[-1], work_date[-2], work_date[-3], from_time[0], from_time[1])
                end_date = datetime.datetime(work_end_date[-1], work_end_date[-2], work_end_date[-3], to_time[0], to_time[1])
                
                if self.parse_options.options['time_operation'] == 'plus':
                    start_date += delta
                    end_date += delta
                elif self.parse_options.options['time_operation'] == 'minus':
                    start_date -= delta
                    end_date -= delta
        
        
                result_string = "From %s To %s (UTC)" %(start_date.strftime('%d.%m.%Y %H:%M'), end_date.strftime('%d.%m.%Y %H:%M'))
            else:
                result_string = decoded_string
                
            return result_string.encode(self.parse_options.options['output_encoding'])
    
    def cut_client_cell(self, client_string):
        st = client_string.decode(self.parse_options.options['output_encoding'])
        st = ''.join(st.split(';')[0])
        return st.encode(self.parse_options.options['output_encoding'])
    
    def add_region_cell(self, cell_based_on):
        
        t_d = {'03':'Northwestern region, Russia',
'05':'Volga region, Russia',
'14':'Ural region, Russia',
'15':'Far East, Russia',
'09':'South region, Russia',
'08':'Siberia region, Russia',
'20':'Central region, Russia',
'21':'Central region, Russia',
'00':'Provider\'s network'
}
        k1 = cell_based_on.split('/')[0]
        
        if  k1 in t_d.keys():
                return t_d[k1]
            
        return cell_based_on
        pass
                
if __name__ == '__main__':
     
    inp = open("19.08-29.08.csv", 'rt')
    outp = open("test.csv", 'wt')
    a = CSVProcessor(inp, outp)
    a.process_file()
    inp.close()
    outp.close()
