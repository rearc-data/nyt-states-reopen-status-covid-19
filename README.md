<a href="https://www.rearc.io/data/">
    <img src="./rearc_logo_rgb.png" alt="Rearc Logo" title="Rearc Logo" height="52" />
</a>

# COVID-19 United States Reopen and Shut Down Status by State | NY Times

You can subscribe to the AWS Data Exchange product utilizing the automation featured in this repository by visiting [https://aws.amazon.com/marketplace/pp/prodview-ejbvrkmiwc5so](https://aws.amazon.com/marketplace/pp/prodview-ejbvrkmiwc5so). 

## Main Overview:
This resource is adapted from an article published by The New York Times - [See Which States Are Reopening and Which Are Still Shut Down](https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html). The included dataset offers a state-by-state overview of the current level of reopen and/or shut down as a result of the coronavirus (COVID-19) pandemic. Estimated state population data from the United States Census Bureau is also included.

#### Data Source
This resource is adapted from two sources:
1. [The New York Times | See Which States Are Reopening and Which Are Still Shut Down](https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html)
2. [United States Census Bureau | State Population Totals: 2010-2019](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)

The included dataset is presented in CSV and JSON format, and is presented with the following columns:

`state_abbreviation, state, status, date_details, restriction_start, restriction_end, status_details, external_link, reopened_personal_care, reopened_retail, reopened_outdoor_and_recreation, reopened_houses_of_worship, reopened_entertainment, reopened_food_and_drink, reopened_industries, reopening_soon_personal_care, reopening_soon_retail, reopening_soon_outdoor_and_recreation, reopening_soon_houses_of_worship, reopening_soon_entertainment, reopening_soon_food_and_drink, reopening_soon_industries, population`

- `state_abbreviation`: two letter state abbreviation (e.g. `NY`, `CA`)
- `state`: state's name (e.g. `New York`, `California`)
- `status`: current state of reopen and/or shut down (e.g. `reopening`, `shutdown-restricted`)
- `date_details`: information regarding when restrictions were put in place, when they or set to expire, or when they were lifted
- `restriction_start`: date parsed from date_details for when some sort of restriction was implimented
- `restriction_end`: date parsed from date_details for when restrictions were - or are planned - to be lifted
- `status_details`: additional details regarding specific restrictions in place in a given state
- `external_link`: additional resource referenced in the New York Times article
- `population`: United States Census Bureau's 2019 estimate for a state's total population

The columns beginning with `reopened` and `reopening_soon` offer specific details on the current state of resources/businesses within a given category. The included categories are:
- `personal_care`
- `retail`
- `outdoor_and_recreation`
- `houses_of_worship`
- `entertainment`
- `food_and_drink`
- `industries`

Note:
- if a  status for a category of businesses in a given state is `reopened`/`reopening_soon` but does not include further details, the corresponding data field be `True`.
- empty data fields in the CSV file or `null` values in the JSON file do not have applicable values from the data source.

## More Information
- Source - [The New York Times | See Which States Are Reopening and Which Are Still Shut Down](https://www.nytimes.com/interactive/2020/us/states-reopen-map-coronavirus.html)
- Source - [United States Census Bureau | State Population Totals: 2010-2019](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)
- [Terms of Use | Fair Use](https://www.copyright.gov/fair-use/more-info.html)
- Frequency: Daily
- Formats: CSV, JSON

## Contact Details
- If you find any issues or have enhancements with this product, open up a GitHub [issue](https://github.com/rearc-data/nyt-states-reopen-status-covid-19/issues) and we will gladly take a look at it. Better yet, submit a pull request. Any contributions you make are greatly appreciated :heart:.
- If you are interested in any other open datasets, please create a request on our project board [here](https://github.com/rearc-data/covid-datasets-aws-data-exchange/projects/1).
- If you have questions about this source data, please send The New York Times an email at nytnews@nytimes.com.
- If you have any other questions or feedback, send us an email at data@rearc.io.

## About Rearc
Rearc is a cloud, software and services company. We believe that empowering engineers drives innovation. Cloud-native architectures, modern software and data practices, and the ability to safely experiment can enable engineers to realize their full potential. We have partnered with several enterprises and startups to help them achieve agility. Our approach is simple — empower engineers with the best tools possible to make an impact within their industry.
