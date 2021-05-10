<a href="https://www.rearc.io/data/">
    <img src="./rearc_logo_rgb.png" alt="Rearc Logo" title="Rearc Logo" height="52" />
</a>

# COVID-19 United States Reopening and Closing Status by State | NY Times

You can subscribe to the AWS Data Exchange product utilizing the automation featured in this repository by visiting [https://aws.amazon.com/marketplace/pp/prodview-ejbvrkmiwc5so](https://aws.amazon.com/marketplace/pp/prodview-ejbvrkmiwc5so). 

## Main Overview
This resource is adapted from an article published by The New York Times - [See How All 50 States Are Reopening (and Closing Again)](https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html). The included dataset offers a state-by-state overview of the current level of reopen and/or shut down as a result of the coronavirus (COVID-19) pandemic. Estimated state population data from the United States Census Bureau is also included.

#### Data Source
This resource is adapted from two sources:

1. [The New York Times | See How All 50 States Are Reopening (and Closing Again)](https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html)

2. [United States Census Bureau | State Population Totals: 2010-2019](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)

The included dataset is presented in CSV and JSON format, and is presented with the following columns:

- `state_abbreviation`: two letter state abbreviation (e.g. `NY`, `CA`)
- `state`: state's name (e.g. `New York`, `California`)
- `businesses`: state of businesses opened
- `masks`: state of masks requirements
- `community`: state of stay-at-home-orders
- `status_details`: additional details regarding specific restrictions in place in a given state
- `external_link`: additional resource referenced in the New York Times article
- `population`: United States Census Bureau's 2019 estimate for a state's total population

The columns beginning with `opened` and `closed` offer specific details on the current state of resources/businesses within a given category. The included categories are:
- `personal_care`
- `retail`
- `outdoor_and_recreation`
- `houses_of_worship`
- `entertainment`
- `food_and_drink`
- `industries`

Note:
- if a  status for a category of businesses in a given state is `opened`/`closed` but does not include further details, the corresponding data field be `TRUE`.
- empty data fields in the CSV file or `null` values in the JSON file do not have applicable values from the data source.

### Changelog
#### 2020-7-1
- Adjustments to the resulting dataset was needed to account for changes to The New York Times article. Resulting dataset now offer details in `opened_` and `closed_` prefixes.

#### 2021-1-29
- Per changes to the source New York Times article:
    - Removed `status` field and replaced with `businesses`, `masks` and `community` fields
    - Removed `date_details`, `restriction_start` and `restriction_end`

#### 2021-5-10
- Per changes to the source New York Times article:
    - Added `reopening` field

## More Information
- Source - [The New York Times | See How All 50 States Are Reopening (and Closing Again)](https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html)
- Source - [United States Census Bureau | State Population Totals: 2010-2019](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)
- [Terms of Use](https://www.copyright.gov/fair-use/more-info.html)
- Frequency: Daily
- Formats: CSV, JSON

## Contact Details
- If you find any issues or have enhancements with this product, open up a GitHub [issue](https://github.com/rearc-data/nyt-states-reopen-status-covid-19/issues) and we will gladly take a look at it. Better yet, submit a pull request. Any contributions you make are greatly appreciated :heart:.
- If you are interested in any other open datasets, please create a request on our project board [here](https://github.com/rearc-data/covid-datasets-aws-data-exchange/projects/1).
- If you have questions about this source data, please send The New York Times an email at nytnews@nytimes.com.
- If you have any other questions or feedback, send us an email at data@rearc.io.

## About Rearc
Rearc is a cloud, software and services company. We believe that empowering engineers drives innovation. Cloud-native architectures, modern software and data practices, and the ability to safely experiment can enable engineers to realize their full potential. We have partnered with several enterprises and startups to help them achieve agility. Our approach is simple — empower engineers with the best tools possible to make an impact within their industry.