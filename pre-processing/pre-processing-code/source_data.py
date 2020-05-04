import os
import boto3
from urllib.request import urlopen
from html.parser import HTMLParser
import operator
import csv
import json

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)

        # various variables to be used while parsing html page

        self.full_data = []
        self.step_data = {}

        self.current_tag = ''
        self.current_class = ''

        self.within_date_details = False
        self.date_details_str = ''

        self.within_text = False
        self.text_str = None

        self.within_link = False

        self.within_reopened_details = False
        self.within_soon_details = False
        self.opened_dict = []


    def handle_starttag(self, tag, attr):
        self.current_tag = tag.lower()
        if self.current_tag == 'div':

            class_str = ''
            id_str = ''
            data_state = ''

            for item in attr:
                if item[0].lower() == 'class':
                    class_str = item[1].strip()
                if item[0].lower() == 'id':
                    id_str = item[1].strip()
                if item[0].lower() == 'data-state':
                    data_state = item[1].strip()
            
            self.current_class = class_str

            if id_str == 'g-state-' + data_state and self.current_class.startswith('g-state g-cat-'):
                    
                if len(self.step_data) > 0:
                    if self.within_reopened_details == True:
                        self.step_data['reopened'] = self.opened_dict
                    elif self.within_soon_details == True:
                        self.step_data['reopening_soon'] = self.opened_dict
                    
                    self.within_reopened_details = False
                    self.within_soon_details = False
                    self.opened_dict = []

                    if 'reopened' not in self.step_data:
                        self.step_data['reopened'] = None
                    if 'reopening_soon' not in self.step_data:
                        self.step_data['reopening_soon'] = None

                    self.full_data.append(self.step_data)
                    self.step_data = {}
                    
                self.step_data['state_abbreviation'] = data_state
                self.step_data['status'] = self.current_class[14:]
            
            elif class_str == 'g-stateCaseChartShell':
                self.step_data['state'] = data_state

            elif class_str == 'g-date-details':
                self.within_date_details = True

            elif class_str == 'g-text':
                self.within_text = True

            elif class_str == 'g-link':
                self.step_data['status_details'] = self.text_str
                self.within_text = False
                self.text_str = None
                
                self.within_link = True
            
            elif class_str == 'g-details-wrap':
                self.within_reopened_details = True
            
            elif class_str == 'g-details-wrap g-details_soon':

                self.step_data['reopened'] = self.opened_dict
                self.within_reopened_details = False
                self.opened_dict = []

                self.within_soon_details = True

        if self.current_tag == 'a' and self.within_link:
            for item in attr:
                if item[0].lower() == 'href':
                    self.step_data['external_link'] = item[1]
            
            self.within_link = False


    def handle_endtag(self, tag):
        if tag.lower() == 'div' and self.within_date_details: 
            self.step_data['date_details'] = self.date_details_str
            self.within_date_details = False
            self.date_details_str = ''

        if tag.lower() == 'body':
            if self.within_reopened_details == True:
                self.step_data['reopened'] = self.opened_dict
            elif self.within_soon_details == True:
                self.step_data['reopening_soon'] = self.opened_dict

            if 'reopened' not in self.step_data:
                self.step_data['reopened'] = None
            if 'reopening_soon' not in self.step_data:
                self.step_data['reopening_soon'] = None

            self.full_data.append(self.step_data)

            self.full_data.sort(key=operator.itemgetter('state'))

     
    def handle_data(self, data):
        if self.within_date_details and self.current_tag == 'span':
            if len(self.date_details_str) == 0:
                self.date_details_str = data
            else:
                self.date_details_str = self.date_details_str + ' ' + data
        
        elif self.within_text:
            if len(data) == 0:
                self.text_str = None
            else:
                self.text_str = data
        
        elif (self.within_reopened_details or self.within_soon_details) and self.current_class == 'g-cat-name':
            self.opened_dict.append(data)
        elif (self.within_reopened_details or self.within_soon_details) and self.current_class == 'g-cat-text':
            self.opened_dict[len(
                self.opened_dict) - 1] = self.opened_dict[len(self.opened_dict) - 1] + ' - ' + data

def source_dataset(new_filename, s3_bucket, new_s3_key):

    source = 'https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html'

    html = urlopen(source)
    str_html = html.read().decode().replace('\n', '').replace('\t', '')
    parser = MyHTMLParser()
    parser.feed(str_html)

    population_source = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv'
    population_csv = urlopen(population_source).read().decode().splitlines()

    population_data = {}

    for state in population_csv[2:]:
        row = state.split(',')
        population_data[row[4]] = row[5]

    with open('/tmp/' + new_filename + '.json', 'w', encoding='utf-8') as j:
        j.write('[') 
        j.write(',\n'.join(json.dumps(
            {**state, 'population': int(population_data[state['state']])}) for state in parser.full_data))
        j.write(']')

    with open('/tmp/' + new_filename + '.csv', 'w', encoding='utf-8') as c:
        writer = csv.DictWriter(c, fieldnames=([*parser.full_data[0].keys(), 'population']))
        writer.writeheader()

        for row in parser.full_data:
            
            if (type(row['reopened']) == list):
                row['reopened'] = ', '.join(row['reopened'])

            if (type(row['reopening_soon']) == list):
                row['reopening_soon'] = '. '.join(row['reopening_soon'])
            
            row['population'] = int(population_data[row['state']])

            writer.writerow(row)

    asset_list = []

    s3 = boto3.client('s3')

    for filename in os.listdir('/tmp'):
        s3.upload_file('/tmp/' + filename, s3_bucket, new_s3_key + filename)
        asset_list.append({'Bucket': s3_bucket, 'Key': new_s3_key + filename})

    return asset_list