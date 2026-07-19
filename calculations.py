# ---------------------------------------------------------------------------
# SUPPORTED BILLING FREQUENCIES
# ---------------------------------------------------------------------------

VALID_BILLING_FREQUENCIES = {
    "Weekly",
    "Monthly",
    "Every 3 Months",
    "Every 6 Months",
    "Yearly",
}


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

def validate_price(price: float) -> float:
    """
    Validate and return a subscription price as a float.
    """

    try:
        numeric_price = float(price)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "The subscription price must be a number."
        ) from error

    if numeric_price < 0:
        raise ValueError(
            "The subscription price cannot be negative."
        )

    return numeric_price


def validate_billing_frequency(
    billing_frequency: str,
) -> str:
    """
    Validate and return a supported billing frequency.
    """

    cleaned_frequency = billing_frequency.strip()

    if cleaned_frequency not in VALID_BILLING_FREQUENCIES:
        raise ValueError(
            "Unknown billing frequency: "
            f"{cleaned_frequency!r}"
        )

    return cleaned_frequency


# ---------------------------------------------------------------------------
# COST CALCULATIONS
# ---------------------------------------------------------------------------

def calculate_monthly_cost(
    price: float,
    billing_frequency: str,
) -> float:
    """
    Convert a subscription payment into an estimated monthly cost.

    Examples:

        £12 monthly            -> £12 per month
        £120 yearly            -> £10 per month
        £30 every 3 months     -> £10 per month
        £10 weekly             -> approximately £43.33 per month
    """

    valid_price = validate_price(price)
    valid_frequency = validate_billing_frequency(
        billing_frequency
    )

    if valid_frequency == "Weekly":
        monthly_cost = valid_price * 52 / 12

    elif valid_frequency == "Monthly":
        monthly_cost = valid_price

    elif valid_frequency == "Every 3 Months":
        monthly_cost = valid_price / 3

    elif valid_frequency == "Every 6 Months":
        monthly_cost = valid_price / 6

    elif valid_frequency == "Yearly":
        monthly_cost = valid_price / 12

    else:
        # This should be unreachable because validation happens above.
        raise ValueError(
            f"Unsupported billing frequency: {valid_frequency}"
        )

    return round(monthly_cost, 2)


def calculate_annual_cost(
    price: float,
    billing_frequency: str,
) -> float:
    """
    Convert a subscription payment into an estimated annual cost.

    Examples:

        £12 monthly            -> £144 per year
        £120 yearly            -> £120 per year
        £30 every 3 months     -> £120 per year
        £10 weekly             -> £520 per year
    """

    valid_price = validate_price(price)
    valid_frequency = validate_billing_frequency(
        billing_frequency
    )

    if valid_frequency == "Weekly":
        annual_cost = valid_price * 52

    elif valid_frequency == "Monthly":
        annual_cost = valid_price * 12

    elif valid_frequency == "Every 3 Months":
        annual_cost = valid_price * 4

    elif valid_frequency == "Every 6 Months":
        annual_cost = valid_price * 2

    elif valid_frequency == "Yearly":
        annual_cost = valid_price

    else:
        raise ValueError(
            f"Unsupported billing frequency: {valid_frequency}"
        )

    return round(annual_cost, 2)


# ---------------------------------------------------------------------------
# OPTIONAL EXTRA CALCULATION
# ---------------------------------------------------------------------------

def calculate_savings_after_cancellation(
    price: float,
    billing_frequency: str,
    months: int = 12,
) -> float:
    """
    Estimate how much money would be saved over a chosen number of months
    after cancelling a subscription.

    This is not currently required by main.py, but it may be useful later.
    """

    if months < 0:
        raise ValueError(
            "The number of months cannot be negative."
        )

    monthly_cost = calculate_monthly_cost(
        price,
        billing_frequency,
    )

    return round(monthly_cost * months, 2)


# ---------------------------------------------------------------------------
# OPTIONAL DEVELOPMENT TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_price = 10.99
    test_frequency = "Monthly"

    monthly = calculate_monthly_cost(
        test_price,
        test_frequency,
    )

    annual = calculate_annual_cost(
        test_price,
        test_frequency,
    )

    print(f"Monthly cost: £{monthly:.2f}")
    print(f"Annual cost: £{annual:.2f}")