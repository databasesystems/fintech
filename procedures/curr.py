from forex_python.converter import CurrencyCodes

def get_currency_symbol_from_locale(locale):
    """Get the currency symbol based on the browser locale."""
    locale_currency_map = {
        "en-GB": "GBP", "en-US": "USD", "fr-FR": "EUR", "de-DE": "EUR",
        "es-ES": "EUR", "it-IT": "EUR", "ja-JP": "JPY", "zh-CN": "CNY",
        "in-IN": "INR", "au-AU": "AUD", "ca-CA": "CAD"
    }
    return locale_currency_map.get(locale, "USD")  # Default to USD

def get_currency_symbol(locale):
    """Returns the currency symbol using the provided locale."""
    currency_code = get_currency_symbol_from_locale(locale)
    currency = CurrencyCodes()
    return currency.get_symbol(currency_code)
