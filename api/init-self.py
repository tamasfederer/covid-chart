import csv
import json
import os
import sqlite3
import requests
import datetime
import logging

# Config logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

# Config
IS_DOWNLOAD = False

# Data source
GITHUB_URL = 'https://raw.githubusercontent.com/'

# Country codes
CC_URL = '/lukes/ISO-3166-Countries-with-Regional-Codes/master/slim-3/'
CC_FILE = 'slim-3.json'

# Our World In Data
OWID_URL = 'owid/covid-19-data/master/public/data/'
OWID_FILES = [
    'jhu/biweekly_cases.csv',
    'jhu/biweekly_cases_per_million.csv',
    'jhu/biweekly_deaths.csv',
    'jhu/biweekly_deaths_per_million.csv',
    'jhu/new_cases.csv',
    'jhu/new_cases_per_million.csv',
    'jhu/new_deaths.csv',
    'jhu/new_deaths_per_million.csv',
    'jhu/total_cases.csv',
    'jhu/total_cases_per_million.csv',
    'jhu/total_deaths.csv',
    'jhu/total_deaths_per_million.csv',
    'jhu/weekly_cases.csv',
    'jhu/weekly_cases_per_million.csv',
    'jhu/weekly_deaths.csv',
    'jhu/weekly_deaths_per_million.csv'
    # 'jhu/COVID-19%20-%20Johns%20Hopkins%20University.csv'
]

# Vaccination file
VACCIONATION_FILE = 'vaccinations/vaccinations.csv'

# Download foleder
DL_FOLDER = './dl/'

# Outputs
OUTPUT_DB = './covid.db'
# OUTPUT_COUNTRIES = './countries.json'
OUTPUT_COUNTRIES = '../src/countries.json'

# Set start date
start_date = datetime.date(2020, 1, 22)


# Download data
def download(url):
    headers = requests.utils.default_headers()
    headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
    })

    print(f'Download {url}')
    req = requests.get(url, headers)

    return req.content


# Write data
def write(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)
        print(f'Done {filename}')


# Download data if needed
logging.info(f'Download data ... ')

if IS_DOWNLOAD:
    # Download country codes
    url = GITHUB_URL + CC_URL + CC_FILE
    filename = DL_FOLDER + os.path.basename(url)

    write(filename, download(url))

    # Download vaccination data
    url = GITHUB_URL + OWID_URL + VACCIONATION_FILE
    filename = DL_FOLDER + os.path.basename(url)

    write(filename, download(url))

    # Download dataset
    for file_url in OWID_FILES:
        url = GITHUB_URL + OWID_URL + file_url
        filename = DL_FOLDER + os.path.basename(url)

        write(filename, download(url))

    logging.info(f'  DONE')
else:
    logging.info(f'  SKIPPED')


# Read countries
logging.info(f'Read countries ...')

filename = DL_FOLDER + os.path.basename(CC_FILE)
countries = []

unicode_names = {
    'land Islands': 'Aland Islands',
    'Cura': 'Curacao',
    'union': 'Reunion',
    'Saint Barth': 'Saint Barthelemy',
    'Ivoire': 'Cote d\'Ivoire'
}

matching_names = {
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Brunei Darussalam': 'Brunei',
    'Cabo Verde': 'Cape Verde',
    'Congo, Democratic Republic of the': 'Democratic Republic of Congo',
    'Faroe Islands': 'Faeroe Islands',
    'Iran (Islamic Republic of)': 'Iran',
    "Lao People's Democratic Republic": 'Laos',
    'Micronesia (Federated States of)': 'Micronesia (country)',
    'Moldova, Republic of': 'Moldova',
    'Palestine, State of': 'Palestine',
    'Russian Federation': 'Russia',
    'Korea, Republic of': 'South Korea',
    'Syrian Arab Republic': 'Syria',
    'Taiwan, Province of China': 'Taiwan',
    'Tanzania, United Republic of': 'Tanzania',
    'Timor-Leste': 'Timor',
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
    'United States of America': 'United States',
    'Holy See': 'Vatican',
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'Viet Nam': 'Vietnam',
    'Falkland Islands (Malvinas)': 'Falkland Islands',
    'Saint Helena, Ascension and Tristan da Cunha': 'Saint Helena',
    'Bonaire, Sint Eustatius and Saba': 'Bonaire Sint Eustatius and Saba',
    'Virgin Islands (British)': 'British Virgin Islands'
}

with open(filename, encoding='utf-8') as f:
    data = json.load(f)
    for country in data:
        try:
            name = country['name'].encode('ascii', 'strict').decode("ascii")
        except UnicodeEncodeError:
            match = False

            for pattern in unicode_names:
                if (pattern in country['name']):
                    name = unicode_names[pattern]
                    match = True

            if not match:
                logging.error(f'unicode error - {country["name"]=}')
                exit()

        for pattern in matching_names:
            if name == pattern:
                print(f'match, {pattern=}')
                name = matching_names[pattern]

        countries.append({
            'name': name,
            'iso': country['alpha-3']
        })

logging.info(f'  DONE')

# Create data superset
logging.info(f'Create dataset ...')

dataset = {}

delta = datetime.timedelta(days=1)
end_date = datetime.date.today() - delta

while start_date <= end_date:
    str_date = str(start_date)
    dataset[str_date] = {}

    for country in countries:
        dataset[str_date][country['name']] = {
            'name': country['name'],
            'iso': country['iso'],
            'date': str_date,
            'biweekly_cases': 0,
            'biweekly_cases_per_million': 0,
            'biweekly_deaths': 0,
            'biweekly_deaths_per_million': 0,
            'new_cases': 0,
            'new_cases_per_million': 0,
            'new_deaths': 0,
            'new_deaths_per_million': 0,
            'total_cases': 0,
            'total_cases_per_million': 0,
            'total_deaths': 0,
            'total_deaths_per_million': 0,
            'weekly_cases': 0,
            'weekly_cases_per_million': 0,
            'weekly_deaths': 0,
            'weekly_deaths_per_million': 0,
            'total_vaccinations': 0,
            'people_vaccinated': 0,
            'people_fully_vaccinated': 0,
            'daily_vaccinations_raw': 0,
            'daily_vaccinations': 0,
            'total_vaccinations_per_hundred': 0,
            'people_vaccinated_per_hundred': 0,
            'people_fully_vaccinated_per_hundred': 0,
            'daily_vaccinations_per_million': 0,
            'total_boosters': 0,
            'total_boosters_per_hundred': 0,
            'daily_people_vaccinated': 0,
            'daily_people_vaccinated_per_hundred': 0
        }

    start_date += delta

logging.info(f'  DONE')

# Go through the OWID files and save them to the dataset
logging.info(f'Parse data ...')

countries_to_skip = [
    'date',
    'World',
    'Africa',
    'Asia',
    'Europe',
    'European Union',
    'International',
    'Kosovo',
    'North America',
    'Oceania',
    'South America',
    'Summer Olympics 2020',
    'High income',
    'Low income',
    'Lower middle income',
    'Upper middle income',
]

for file_url in OWID_FILES:
    filename = DL_FOLDER + os.path.basename(file_url)
    column_name = os.path.basename(file_url).split('.')[0]

    with open(filename, 'r', encoding='utf-8') as csvfile:
        header = []
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in reader:
            # Header will be the first row
            if len(header) == 0:
                header = row

            # Everything else is data
            else:
                for i in range(len(header)):
                    if header[i] in countries_to_skip:
                        continue

                    if row[0] not in dataset:
                        logging.error(f'error - {row[0]} not in the country list')
                        exit()

                    if header[i] not in dataset[row[0]]:
                        logging.error(f'error - {header[i]} not in dataset date')
                        exit()

                    dataset[row[0]][header[i]][column_name] = row[i]

logging.info(f'  DONE')

# Read vaccination data
countries_to_skip = [
    'location',
    'iso_code',
    'date',
    'Africa',
    'Asia',
    'England',
    'Europe',
    'European Union',
    # 'International',
    'Kosovo',
    'North America',
    'Northern Cyprus',
    'Northern Ireland',
    'Oceania',
    'Scotland',
    'South America',
    'Wales',
    'World',
    'High income',
    'Low income',
    'Lower middle income',
    'Upper middle income',
]

filename = DL_FOLDER + os.path.basename(VACCIONATION_FILE)
print(f'Read {filename}')

header = []
vaccinations = []

with open(filename, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        # Header will be the first row
        if len(header) == 0:
            header = row

        # Everything else is data
        else:
            for i in range(len(header)):
                if row[0] in countries_to_skip:
                    continue

                if header[i] in countries_to_skip:
                    continue

                if row[2] not in dataset:
                    print(f'error - {row[2]} not in dataset')
                    exit()

                if row[0] not in dataset[row[2]]:
                    print(f'error - {row[0]} not in dataset date')
                    exit()

                dataset[row[2]][row[0]][header[i]] = row[i]

# Trim data
countries_with_no_data = {}

for country in countries:
    countries_with_no_data[country['name']] = 0.0

for dk in dataset:
    for cc in dataset[dk]:
        for key in dataset[dk][cc]:
            if key == 'date' or key == 'iso' or key == 'name':
                continue
            else:
                if dataset[dk][cc][key] == '':
                    float_val = 0.0
                else:
                    float_val = float(dataset[dk][cc][key])

                countries_with_no_data[dataset[dk][cc]['name']] += float_val

cwnd = []

for key in countries_with_no_data:
    if countries_with_no_data[key] == 0.0:
        cwnd.append(key)

# Save countries
print(f'Write {OUTPUT_COUNTRIES}')

ctw = []

for country in countries:
    if country['name'] in cwnd:
        continue
    else:
        ctw.append(country)

with open(OUTPUT_COUNTRIES, 'w') as f:
    json.dump(ctw, f)

print(f'Done {OUTPUT_COUNTRIES} - {len(ctw)} countries written')

# Remove database file if there's any
if (os.path.isfile(OUTPUT_DB)):
    print(f'Remove {OUTPUT_DB}')
    os.remove(OUTPUT_DB)

# Create database
print(f'Create {OUTPUT_DB}')

query = 'CREATE TABLE dataset ('
query += 'name TEXT, '
query += 'iso TEXT, '
query += 'date TEXT, '
for file_url in OWID_FILES:
    column_name = os.path.basename(file_url).split('.')[0]
    query += column_name + ' TEXT, '
query += 'total_vaccinations TEXT, '
query += 'people_vaccinated TEXT, '
query += 'people_fully_vaccinated TEXT, '
query += 'daily_vaccinations_raw TEXT, '
query += 'daily_vaccinations TEXT, '
query += 'total_vaccinations_per_hundred TEXT, '
query += 'people_vaccinated_per_hundred TEXT, '
query += 'people_fully_vaccinated_per_hundred TEXT, '
query += 'daily_vaccinations_per_million TEXT, '
query += 'total_boosters TEXT, '
query += 'total_boosters_per_hundred TEXT, '
query += 'daily_people_vaccinated TEXT, '
query += 'daily_people_vaccinated_per_hundred TEXT'
query += ');'

con = sqlite3.connect(OUTPUT_DB)
cur = con.cursor()
cur.execute(query)
con.commit()


for dk in dataset:
    print(f'Write {dk}')

    for cc in dataset[dk]:
        if cc in cwnd:
            continue
        else:
            query = 'INSERT INTO dataset VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

            row = []
            for key in dataset[dk][cc]:
                row.append(dataset[dk][cc][key])

            if len(row) != 32:
                logging.error(f'{len(row)=}')
                print(f'ERROR - {dk}, {cc}, {dataset[dk][cc]}')
                exit()

            try:
                cur.execute(query, row)
            except sqlite3.ProgrammingError:
                print(f'sqlite3.ProgrammingError - {dk}, {cc}, {row}')
                exit()

con.commit()
con.close()

print(f'Done')
