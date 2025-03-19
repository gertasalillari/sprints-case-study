import pandas as pd

from logs.logger_config import logger


def convert_currency(amounts: pd.Series, currencies: pd.Series, target_currency: str, rates: dict, default_rate=None):
    """
    Converts currency amounts to a target currency based on exchange rates.

    Parameters:
    - amounts (pd.Series): Series of amounts to be converted.
    - currencies (pd.Series): Series of currency codes corresponding to the amounts.
    - target_currency (str): The currency to convert all amounts into.
    - rates (dict): Exchange rates in the format {('from_currency', 'to_currency'): rate}.
    - default_rate (float, optional): Default exchange rate if no matching rate is found.

    Returns:
    - pd.Series: Converted amounts.
    """
    # Ensure both Series have the same length
    assert len(amounts) == len(currencies), "Error: The 'amounts' and 'currencies' series must have the same length."

    logger.info("Converting currencies...")
    # Create a Series of exchange rates by mapping (from_currency, target_currency) pairs
    conversion_rates = currencies.map(lambda c: rates.get((c, target_currency), default_rate))

    # Convert amounts where a valid rate exists, keep original if already in target currency
    converted_amounts = round(amounts.where(currencies == target_currency, amounts * conversion_rates), 2)
    logger.info("Currency conversion completed.")

    return converted_amounts
