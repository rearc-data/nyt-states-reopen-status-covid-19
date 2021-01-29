# Changelog
All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## 2020-7-1
### Changed
- Adjustments to the resulting dataset was needed to account for changes to the New York Times article. Resulting datasets now offer details in `opened_` and `closed_` prefixes.

## 2021-1-29
### Changed
- Per changes to the source New York Times article:
    - Removed `status` field and replaced with `businesses`, `masks` and `community` fields
    - Removed `date_details`, `restriction_start` and `restriction_end`