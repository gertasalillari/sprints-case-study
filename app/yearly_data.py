import pandas as pd
import requests
from utils.utils import convert_currency

from logs.logger_config import logger

# Define API endpoints
monthly_data_url = "https://technical-case-platform-engineer.onrender.com/monthly-data"
exchange_rates_url = "https://technical-case-platform-engineer.onrender.com/exchange-rates"
annual_data_url = "https://technical-case-platform-engineer.onrender.com/annual-data"

TARGET_CURRENCY = "SEK"
CONVERTED_COL_NAME = "value_" + TARGET_CURRENCY
DATA_PATH = "outputs/data"
HIGHEST_SEK_FILENAME = DATA_PATH + "/monthly_highest_sek.csv"
NEXARA_TOT_VALUE_FILENAME = DATA_PATH + "/total_nexara_sek.txt"

logger.info("Fetching data...")

# Fetch monthly data
monthly_data_response = requests.get(monthly_data_url)
monthly_data = monthly_data_response.json()

# Fetch exchange rates
exchange_rates_response = requests.get(exchange_rates_url)
exchange_rates = exchange_rates_response.json()

logger.info("Processing data...")
# Convert monthly data to DataFrame
df = pd.DataFrame(monthly_data)

# Filter valid entries

# Create lookup dictionary for rates
rates = {(e["from_currency"], e["to_currency"]): e["rate"] for e in exchange_rates}
unique_currencies = {currency for pair in rates.keys() for currency in pair}

# Filter the DataFrame to include only rows with supported currencies
df = df[df["currency"].isin(unique_currencies)]
logger.info("\tUnsupported currencies removed.")

# Convert timestamps, invalid ones become NaT
df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d", errors="coerce")
# Could also log rows with invalid timestamps to a csv file
# Remove invalid timestamp rows
df = df[df["timestamp"].notna()]
logger.info("\tRemoved invalid timestamps.")

# Historical data
df = df[df["timestamp"] < pd.Timestamp.now()]
logger.info("\tHistorical data filtered.")

# Positive values
df = df[df["value"] > 0]
logger.info("\tNegative value data removed.")


df[CONVERTED_COL_NAME] = convert_currency(df["value"], df["currency"], TARGET_CURRENCY, rates)

# Remove rows where exchange rate conversion failed (i.e., if currency was not found)
df = df[df[CONVERTED_COL_NAME].notna()]

# Aggregate data annually per company
df["year"] = df["timestamp"].dt.year
annual_data = df.groupby(["company", "year"])[CONVERTED_COL_NAME].sum().reset_index()
annual_data = annual_data.rename(columns={CONVERTED_COL_NAME: "value"})
annual_data["currency"] = TARGET_CURRENCY
logger.info("Annual data aggregated.")

# Prepare data for POST request
annual_data_records = annual_data.to_dict(orient="records")

# Post annual data
logger.info("Posting annual data to the endpoint...")
# Correct the JSON structure for the POST request
headers = {"Content-Type": "application/json"}

logger.info("Posting annual data...")
for record in annual_data_records:
    post_response = requests.post(annual_data_url, json=record, headers=headers)

    if post_response.status_code != 200:
        logger.info(f"⛔️ Failed to post annual data. Status code: {post_response.status_code}")
        break

logger.info("✅ Annual data successfully posted.")


###############
# Further questions
###############
# 1. For each year and month, which company had the highest value in SEK?
df["month"] = df["timestamp"].dt.month
idx = df.groupby(["year", "month"])[CONVERTED_COL_NAME].idxmax()
companies_monthly_highest_sek = df.loc[idx].reset_index(drop=True)[['year', 'month', 'company']]
companies_monthly_highest_sek.to_csv(HIGHEST_SEK_FILENAME, index=False)
logger.info(f"Highest SEK value company per month saved in {HIGHEST_SEK_FILENAME}")

# 2. What is the total value of all monthly entries for Nexara Technologies in SEK?
total_nexara_sek = round(df[df["company"] == "Nexara Technologies"][CONVERTED_COL_NAME].sum(), 2)
with open(NEXARA_TOT_VALUE_FILENAME, "w") as f:
    f.write(str(total_nexara_sek)) 
logger.info(f"Nexara total SEK value saved in {NEXARA_TOT_VALUE_FILENAME}")

logger.info("🚀 Successfully terminated.")