# Sprints Case Study - Part 1

This repository contains a Python script that processes financial data from an [external API](https://technical-case-platform-engineer.onrender.com/docs), filters and aggregates the data, converts it to a target currency (SEK), and posts the processed data to an endpoint.

The script also includes additional functionality for extracting insights such as identifying the highest-value company per month and computing total annual values.

## How it works

1. **Fetching Data**

The script fetches monthly financial data and exchange rates from the [external API](https://technical-case-platform-engineer.onrender.com):

- Monthly financial data: `/monthly-data`
- Exchange rates: `exchange-rates`
- Posts processed annual data to: `/annual-data`

2. **Data Processing**

- Filters out invalid timestamps.
- Removes entries with negative values.
- Filters out unsupported currencies (not available in the exchange rates API).
- Converts values to SEK using exchange rates.
- Aggregates data annually per company.

3. **Posting Processed Data**

- The aggregated annual data is formatted according to the API's expected schema.
- Each record is posted individually to the `/annual-data endpoint`.
- If any record fails to post (i.e., HTTP status is not 200), logging captures the error.


### Additional Insights
The script also generates additional insights (see below for output location):

1. _For each year and month, the company that had the highest value in SEK_ 
2. _Total value of all monthly entries for Nexara Technologies in SEK_ 

## Getting Started

1. Copy the sample environment file.
```
cp sample.env ./app/.env
```

2. Build image and up the server:
```bash
docker compose up --build
```
... which runs the scripts with Python from the entrypoint, posting to the output data to the `/annual-data endpoint.`
```bash
python yearly_data.py 
```

The script uses a logger (`app/logs/logger_config.py`) to track progress and errors. Log messages include:
- Data fetching status
- Data filtering and conversion process
- Posting success or failure

The logs are stored in the `outputs/logs` folder.

The script also contains a "Further questions" section at the end, that produces the files `monthly_highest_sek.csv` and `total_nexara_sek.txt` respectively for the two additional insights requested. These are contained in the `outputs/data`