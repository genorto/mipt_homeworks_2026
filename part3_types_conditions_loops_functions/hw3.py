#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


SHORT_MONTHS = (4, 6, 9, 11)
FEBRUARY = 2
LONG_MONTH_DAYS = 31
LEAP_YEAR_FEBRUARY_DAYS = 29

MAX_DAY = 31
MAX_MONTH = 12
MAX_YEAR = 9999


DATE_HYPHEN_COUNT = 2
INCOME_PARAMS_COUNT = 2
COST_PARAMS_COUNT = 3
CATEGORY_PARAMS_COUNT = 1
STATS_PARAMS_COUNT = 1


AMOUNT = "amount"
CATEGORY = "category"
DATE = "date"


financial_transactions_storage: list[dict[str, Any]] = []


StatsType = list[float]
DateType = tuple[int, int, int]


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True

    return year % 4 == 0 and year % 100 != 0


def process_day(raw_day: str) -> int | None:
    if not raw_day.isdigit():
        return None

    day = int(raw_day)
    if day < 1 or day > MAX_DAY:
        return None

    return day


def process_month(raw_month: str) -> int | None:
    if not raw_month.isdigit():
        return None

    month = int(raw_month)
    if month < 1 or month > MAX_MONTH:
        return None

    return month


def process_year(raw_year: str) -> int | None:
    if not raw_year.isdigit():
        return None

    year = int(raw_year)
    if year > MAX_YEAR:
        return None

    return year


def is_february(day: int, year: int) -> bool:
    return day > LEAP_YEAR_FEBRUARY_DAYS or (day == LEAP_YEAR_FEBRUARY_DAYS and not is_leap_year(year))


def extract_date(maybe_dt: str) -> DateType | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if maybe_dt.count("-") != DATE_HYPHEN_COUNT:
        return None

    raw_date = maybe_dt.split("-")

    day = process_day(raw_date[0])
    month = process_month(raw_date[1])
    year = process_year(raw_date[2])

    if day is None or month is None or year is None:
        return None
    if month in SHORT_MONTHS and day == LONG_MONTH_DAYS:
        return None
    if month == FEBRUARY and is_february(day, year):
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({AMOUNT: amount, DATE: date})
    return OP_SUCCESS_MSG


def cost_check(category_name: str, amount: float, date: DateType | None) -> str | None:
    if category_name.count("::") != 1:
        return NOT_EXISTS_CATEGORY
    target_category, common_category = category_name.split("::")

    if target_category not in EXPENSE_CATEGORIES or common_category not in EXPENSE_CATEGORIES[target_category]:
        return NOT_EXISTS_CATEGORY
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if date is None:
        return INCORRECT_DATE_MSG
    return None


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    verdict = cost_check(category_name, amount, date)
    if verdict is not None:
        financial_transactions_storage.append({})
        return verdict

    financial_transactions_storage.append({CATEGORY: category_name, AMOUNT: amount, DATE: date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        [
            f"{common_category}::{target_category}"
            for common_category, categories in EXPENSE_CATEGORIES.items()
            for target_category in categories
        ]
    )


def reverse(tup: tuple[int, int, int]) -> tuple[int, int, int]:
    return tup[2], tup[1], tup[0]


def is_later(date: DateType, target_date: DateType) -> bool:
    return reverse(date) > reverse(target_date)


def is_same_month(date: DateType, target_date: DateType) -> bool:
    return date[1:] == target_date[1:]


def process_data(data: dict[str, Any], report_date: DateType, current_date: DateType) -> StatsType:
    amount = float(data.get(AMOUNT, float(0)))
    category = data.get(CATEGORY)
    if not is_same_month(report_date, current_date):
        return [amount, float(0), float(0)]
    if category is None:
        return [amount, amount, float(0)]
    return [-amount, float(0), amount]


def componentwise_addition(source: list[float], target: list[float]) -> None:
    target[0] += source[0]
    target[1] += source[1]
    target[2] += source[2]


def get_stats(report_date: DateType) -> list[float]:
    stats: StatsType = [float(0), float(0), float(0)]

    for data in financial_transactions_storage:
        current_date = data.get(DATE, (0, 0, 0))
        if is_later(report_date, current_date):
            break
        result = process_data(data, report_date, current_date)
        componentwise_addition(result, stats)

    return stats


def get_details(report_date: DateType) -> dict[str, float]:
    result: dict[str, float] = {}

    for data in financial_transactions_storage:
        current_date = data.get(DATE, (0, 0, 0))
        if is_later(report_date, current_date):
            break
        if not is_same_month(report_date, current_date):
            continue
        amount = float(data.get(AMOUNT, float(0)))
        category = data.get(CATEGORY)
        if category is not None:
            result[category] = result.get(category, 0) + amount

    return result


def form_details(report_date: DateType) -> str:
    details = get_details(report_date)
    result = ["Details (category: amount):"]
    sorted_categories = sorted(details.keys())

    for index, category in enumerate(sorted_categories, start=1):
        result.append(f"{index}. {category}: {details[category]}")

    return "\n".join(result)


def form_insight(report_date: DateType) -> str:
    capital, income, cost = get_stats(report_date)
    status = "profit" if income > cost else "loss"
    return "\n".join(
        [
            f"Your statistics as of {report_date}:",
            f"Total capital: {capital} rubles",
            f"This month, the {status} amounted to {abs(income - cost)} rubles.",
            f"Income: {income} rubles",
            f"Expenses: {cost} rubles",
        ]
    )


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG

    insight = form_insight(date)
    details = form_details(date)
    return f"{insight}\n\n{details}"


def income_helper(params: list[str]) -> str:
    if len(params) != INCOME_PARAMS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount = float(params[0].replace(",", "."))
    date = params[1]

    return income_handler(amount, date)


def cost_helper(params: list[str]) -> str:
    if len(params) == CATEGORY_PARAMS_COUNT and params[0] == "categories":
        return cost_categories_handler()
    if len(params) != COST_PARAMS_COUNT:
        return UNKNOWN_COMMAND_MSG

    category_name = params[0]
    amount = float(params[1].replace(",", "."))
    date = params[2]

    return cost_handler(category_name, amount, date)


def stats_helper(params: list[str]) -> str:
    if len(params) != STATS_PARAMS_COUNT:
        return UNKNOWN_COMMAND_MSG

    date = params[0]

    return stats_handler(date)


def main() -> None:
    query = ""
    while query != "exit":
        input_list = input().split()
        query = input_list[0]

        match query:
            case "income":
                print(income_helper(input_list[1:]))
            case "cost":
                print(cost_helper(input_list[1:]))
            case "stats":
                print(stats_helper(input_list[1:]))
            case _:
                print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
