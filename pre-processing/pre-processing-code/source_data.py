import os
import boto3
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import operator
import csv
import json
from multiprocessing.dummy import Pool
import time
from s3_md5_compare import md5_compare


class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)

        # various variables to be used while parsing html content
        self.full_data = []
        self.step_data = {}
        self.current_tag = ''
        self.current_class = ''
        self.within_text = False
        self.within_opened = False
        self.within_closed = False
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
                        if self.within_opened:
                            self.step_data['opened_' +
                                           self.current_cat] = True
                            self.categories.add('opened_' + self.current_cat)
                            self.within_opened = False

                        if self.within_closed:
                            self.step_data['closed_' +
                                           self.current_cat] = True
                            self.categories.add('closed_' + self.current_cat)
                            self.within_closed = False

                        self.current_cat = ''
                    self.within_opened = False
                    self.within_closed = False

                    self.full_data.append(self.step_data)
                    self.step_data = {}

            # assign attributes of state entries
                self.step_data['state_abbreviation'] = data_state

            if self.current_class == 'g-stateCaseChartShell':
                self.step_data['state'] = data_state

            if self.current_class == 'g-text-wrap':
                self.within_text = True

            if self.current_class == 'g-details-wrap g-details':
                self.within_opened = True
                self.within_closed = False

            if self.current_class == 'g-details-wrap g-details_closed':
                if len(self.current_cat) > 0:
                    if self.within_opened:
                        self.step_data['opened_' + self.current_cat] = True
                        self.within_opened = False

                    self.current_cat = ''

                self.within_closed = True
                self.within_opened = False

        if self.within_text and self.current_tag == 'a':
            self.step_data['external_link'] = href_str

        # finish processing final state at end of article
        if self.current_class == 'g-subhed g-optimize-type':
            if len(self.step_data) > 0:
                if len(self.current_cat) > 0:
                    if self.within_opened:
                        self.step_data['opened_' +
                                       self.current_cat] = True
                        self.categories.add('opened_' + self.current_cat)
                        self.within_opened = False

                    if self.within_closed:
                        self.step_data['closed_' +
                                       self.current_cat] = True
                        self.categories.add('closed_' + self.current_cat)
                        self.within_closed = False

                    self.current_cat = ''

                self.full_data.append(self.step_data)
                self.step_data = {}

                self.full_data.sort(
                    key=operator.itemgetter('state_abbreviation'))

    def handle_endtag(self, tag):

        # close self.within_text when leaving div tag
        if tag.lower() == 'div' and self.within_text:
            self.with_text = False

    def handle_data(self, data):

        if self.within_text and self.current_class == 'g-text':
            self.step_data['status_details'] = data

        if self.current_class.startswith('g-rule g-'):
            self.step_data[self.current_class.split('g-rule g-', 1)[1]] = data

        # set key for status variations
        if self.current_class == 'g-cat-name':

            if len(self.current_cat) > 0:
                if self.within_opened:
                    self.step_data['opened_' + self.current_cat] = True
                    self.categories.add('opened_' + self.current_cat)
                if self.within_closed:
                    self.step_data['closed_' + self.current_cat] = True
                    self.categories.add('closed_' + self.current_cat)

            self.current_cat = data.lower().replace(' ', '_')

        # set value for status variations
        if self.current_class == 'g-cat-text':
            if len(self.current_cat) > 0:
                if self.within_opened:
                    self.step_data['opened_' + self.current_cat] = data
                    self.categories.add('opened_' + self.current_cat)
                if self.within_closed:
                    self.step_data['closed_' + self.current_cat] = data
                    self.categories.add('closed_' + self.current_cat)

            self.current_cat = ''


def download_data(url):
    response = None
    retries = 5
    for attempt in range(retries):
        try:
            response = urlopen(url)
        except HTTPError as e:
            if attempt == retries:
                raise Exception('HTTPError: ', e.code)
            time.sleep(0.2 * attempt)
        except URLError as e:
            if attempt == retries:
                raise Exception('URLError: ', e.reason)
            time.sleep(0.2 * attempt)
        else:
            break

    if response is None:
        raise Exception('There was an issue downloading the dataset')
    else:
        return response.read().decode()


def source_dataset(): #new_filename, s3_bucket, new_s3_key):

    dataset_name = os.getenv('DATASET_NAME')
    asset_bucket = os.getenv('ASSET_BUCKET')

    data_dir = '/tmp'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    file_location_csv = os.path.join(data_dir, dataset_name + '.csv')
    file_location_json = os.path.join(data_dir, dataset_name + '.json')

    urls = [
        'https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html',
        'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv'
    ]

    with (Pool(2)) as p:
        data_source = p.map(download_data, urls)

    html = data_source[0].replace('\n', '').replace('\t', '')
    parser = MyHTMLParser()
    parser.feed(html)

    # download and format population data
    population_csv = data_source[1].replace(
        'Puerto Rico Commonwealth', 'Puerto Rico').splitlines()

    population_data = {}

    for state in population_csv[2:]:
        row = state.split(',')
        population_data[row[4]] = row[5]

    # creating fieldnames variable to set order of data
    fieldnames = ['state_abbreviation', 'state', 'businesses',
                  'masks', 'community', 'status_details', 'external_link']

    # adding categories variations to fieldnames
    for category in parser.categories:
        fieldnames.append(category)

    fieldnames.append('population')

    # 5/10/2021 as source data has changed
    fieldnames.append('reopening')


    # creating the csv file
    with open(file_location_csv, 'w', encoding='utf-8') as c:
        writer = csv.DictWriter(c, fieldnames=fieldnames)
        writer.writeheader()

        for row in parser.full_data:
            row['population'] = int(population_data[row['state']])
            writer.writerow(row)

    # creating the json file
    with open(file_location_json, 'w', encoding='utf-8') as j, open(file_location_csv, 'r') as c:
        reader = csv.DictReader(c)
        j.write('[')
        j.write(',\n'.join(json.dumps(row).replace('""', 'null')
                           for row in reader))
        j.write(']')

    # uploading to s3
    s3_uploads = []
    s3 = boto3.client('s3')

    for filename in os.listdir('/tmp/'):
        if filename.startswith(dataset_name):

            file_location = '/tmp/' + filename

            obj_name = file_location.split('/', 3).pop().replace(' ', '_').lower()
            new_s3_key = dataset_name + '/dataset/' + obj_name

            has_changes = md5_compare(s3, asset_bucket, new_s3_key, file_location)
            if has_changes:
                s3.upload_file(file_location, asset_bucket, new_s3_key)
                print('Uploaded: ' + filename)
            else:
                print('No changes in: ' + filename)

            asset_source = {'Bucket': asset_bucket, 'Key': new_s3_key}
            s3_uploads.append({'has_changes': has_changes,
                                'asset_source': asset_source})

    count_updated_data = sum(
        upload['has_changes'] == True for upload in s3_uploads)
    asset_list = []
    if count_updated_data > 0:
        asset_list = list(
            map(lambda upload: upload['asset_source'], s3_uploads))
        if len(asset_list) == 0:
            raise Exception('Something went wrong when uploading files to s3')

    return asset_list
