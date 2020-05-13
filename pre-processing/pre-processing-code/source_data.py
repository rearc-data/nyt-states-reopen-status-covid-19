import os
import boto3
from urllib.request import urlopen
from html.parser import HTMLParser
import operator
import csv
import json
from datetime import datetime

# parse/format dates in date_details field for use in restriction_start and
# restriction_end field
def parse_date(date_details):
    restriction_start = None
    restriction_end = None

    if ' effect since ' in date_details:
        date_str = ' '.join(date_details.split(
            ' effect since ', 1)[1].split(' ', 2)[:2])
        restriction_start = datetime.strptime(
            date_str + ' 2020', '%B %d %Y').date().strftime('%Y-%m-%d')

    if ' set to expire ' in date_details:
        date_str = ' '.join(date_details.split(
            ' set to expire ', 1)[1].split(' ', 2)[:2])
        restriction_end = datetime.strptime(
            date_str + ' 2020', '%B %d %Y').date().strftime('%Y-%m-%d')
    elif ' expired on ' in date_details:
        date_str = ' '.join(date_details.split(
            ' expired on ', 1)[1].split(' ', 2)[:2])
        restriction_end = datetime.strptime(
            date_str + ' 2020', '%B %d %Y').strftime('%Y-%m-%d')

    return [restriction_start, restriction_end]

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)

        # various variables to be used while parsing html content
        self.full_data = []
        self.step_data = {}

        self.current_tag = ''
        self.current_class = ''

        self.within_date_details = False
        self.date_details_str = ''

        self.within_text = False

        self.within_reopened = False
        self.within_reopening_soon = False

        self.current_cat = ''

        self.categories = set()

    def handle_starttag(self, tag, attr):
        self.current_tag = tag.lower()

        class_str = ''
        id_str = ''
        data_state = ''
        href_str = ''

        # iterate through attr on tag
        for item in attr:
            if item[0].lower() == 'class':
                class_str = item[1].strip()
            if item[0].lower() == 'id':
                id_str = item[1].strip()
            if item[0].lower() == 'data-state':
                data_state = item[1].strip()
            if item[0].lower() == 'href':
                href_str = item[1].strip()

        self.current_class = class_str

        if self.current_tag == 'div':

            # identify a new state
            if id_str == 'g-state-' + data_state and self.current_class.startswith('g-state g-cat-'):

                # if an previous state has already begun processing,
                # finished exisiting processing to transition to new state
                if len(self.step_data) > 0:

                    if len(self.current_cat) > 0:
                        if self.within_reopened:
                            self.step_data['reopened_' +
                                           self.current_cat] = True
                            self.within_reopened = False

                        if self.within_reopening_soon:
                            self.step_data['reopening_soon_' +
                                           self.current_cat] = True
                            self.within_reopening_soon = False

                        self.current_cat = ''

                    self.full_data.append(self.step_data)
                    self.step_data = {}

            # assign attributes of state entries
                self.step_data['state_abbreviation'] = data_state
                self.step_data['status'] = self.current_class.split(
                    'g-state g-cat-', 1)[1]

            if self.current_class == 'g-stateCaseChartShell':
                self.step_data['state'] = data_state

            if self.current_class == 'g-date-details':
                self.within_date_details = True

            if self.current_class == 'g-text-wrap':
                self.within_text = True

            if self.current_class == 'g-details-wrap':
                self.within_reopened = True

            if self.current_class == 'g-details-wrap g-details_soon':
                if len(self.current_cat) > 0:
                    if self.within_reopened:
                        self.step_data['reopened_' + self.current_cat] = True
                        self.within_reopened = False

                    self.current_cat = ''

                self.within_reopening_soon = True

        if self.within_text and self.current_tag == 'a':
            self.step_data['external_link'] = href_str

        # finish processing final state at end of article
        if self.current_class == 'g-subhed g-optimize-type':
            if len(self.step_data) > 0:
                if len(self.current_cat) > 0:
                    if self.within_reopened:
                        self.step_data['reopened_' +
                                       self.current_cat] = True
                        self.within_reopened = False

                    if self.within_reopening_soon:
                        self.step_data['reopening_soon_' +
                                       self.current_cat] = True
                        self.within_reopening_soon = False

                    self.current_cat = ''

                self.full_data.append(self.step_data)
                self.step_data = {}

                self.full_data.sort(
                    key=operator.itemgetter('state_abbreviation'))

    def handle_endtag(self, tag):

        # finished processing for date_details attribute when leaving div tag
        if tag.lower() == 'div' and self.within_date_details:
            self.step_data['date_details'] = self.date_details_str

            date_str = parse_date(self.date_details_str.replace('.', ''))

            if date_str[0] != None:
                self.step_data['restriction_start'] = date_str[0]

            if date_str[1] != None:
                self.step_data['restriction_end'] = date_str[1]

            self.within_date_details = False
            self.date_details_str = ''

        # close self.within_text when leaving div tag
        if tag.lower() == 'div' and self.within_text:
            self.with_text = False

    def handle_data(self, data):

        # construct date_details attribute
        if self.within_date_details and self.current_tag == 'span':
            if len(self.date_details_str) == 0:
                self.date_details_str = data
            else:
                self.date_details_str = self.date_details_str + ' ' + data

        if self.within_text and self.current_class == 'g-text':
            self.step_data['status_details'] = data

        # set key for status variations
        if self.current_class == 'g-cat-name':

            if len(self.current_cat) > 0:
                if self.within_reopened:
                    self.step_data['reopened_' + self.current_cat] = True

                if self.within_reopening_soon:
                    self.step_data['reopening_soon_' + self.current_cat] = True

            self.current_cat = data.lower().replace(' ', '_')
            self.categories.add(self.current_cat)

        # set value for status variations
        if self.current_class == 'g-cat-text':
            if len(self.current_cat) > 0:
                if self.within_reopened:
                    self.step_data['reopened_' + self.current_cat] = data

                if self.within_reopening_soon:
                    self.step_data['reopening_soon_' + self.current_cat] = data

            self.current_cat = ''

def source_dataset(new_filename, s3_bucket, new_s3_key):

    # download nyt webpage, and parse the html to format data
    source = 'https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html'

    html = urlopen(source)
    str_html = html.read().decode().replace('\n', '').replace('\t', '')
    parser = MyHTMLParser()
    parser.feed(str_html)

    # download and format population data
    population_source = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv'
    population_csv = urlopen(population_source).read().decode().replace(
        'Puerto Rico Commonwealth', 'Puerto Rico').splitlines()

    population_data = {}

    for state in population_csv[2:]:
        row = state.split(',')
        population_data[row[4]] = row[5]

    # creating fieldnames variable to set order of data
    fieldnames = ['state_abbreviation', 'state',
                  'status', 'date_details', 'restriction_start', 'restriction_end', 'status_details', 'external_link']

    # adding categories variations to fieldnames
    for category in parser.categories:
        fieldnames.append('reopened_' + category)

    for category in parser.categories:
        fieldnames.append('reopening_soon_' + category)

    fieldnames.append('population')

    # creating the csv file
    with open('/tmp/' + new_filename + '.csv', 'w', encoding='utf-8') as c:
        writer = csv.DictWriter(c, fieldnames=fieldnames)
        writer.writeheader()

        for row in parser.full_data:
            row['population'] = int(population_data[row['state']])
            writer.writerow(row)

    # creating the json file
    with open('/tmp/' + new_filename + '.json', 'w', encoding='utf-8') as j, open('/tmp/' + new_filename + '.csv', 'r') as c:
        reader = csv.DictReader(c)
        j.write('[')
        j.write(',\n'.join(json.dumps(row).replace('""', 'null')
                           for row in reader))
        j.write(']')

    # uploading to s3
    asset_list = []

    s3 = boto3.client('s3')

    for filename in os.listdir('/tmp'):
        s3.upload_file('/tmp/' + filename, s3_bucket, new_s3_key + filename)
        asset_list.append({'Bucket': s3_bucket, 'Key': new_s3_key + filename})

    return asset_list