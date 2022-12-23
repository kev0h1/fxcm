def calculate_lotsize(risk_percentage, stoploss_in_pips, equity):
    return ((risk_percentage / 100) * equity) / (stoploss_in_pips * 10)


def ten_pip_value(currency_pair):
    if "JPY" in currency_pair:
        return 0.1
    return 0.001
