#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_AMOUNT_MSG = "Invalid amount!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
DIGITS = "0123456789"
SMALL_MONTHS = [4, 6, 9, 11]
FEBRUARY = 2
BIG_MONTH_DAY_COUNT = 31
LEAP_YEAR_DAY_COUNT = 29
DAY_LENGTH = 2
MONTH_LENGTH = 2
YEAR_LENGTH = 4
DATE_HYPHEN_COUNT = 2
INCOME_PARAMS_COUNT = 2
COST_PARAMS_COUNT = 3
STATS_PARAMS_COUNT = 1

Date = tuple[int, int, int]

Funds = dict[str, float | dict[str, float]]

Stats = tuple[Funds, tuple[float, float, float]]

database: dict[int, dict[int, dict[int, Funds]]] = {}


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return (not bool(year % 4) and bool(year % 100)) or not bool(year % 400)


def process_day(raw_day: str) -> int | None:
    if (len(raw_day) != DAY_LENGTH
            or raw_day[0] not in DIGITS
            or raw_day[1] not in DIGITS):
        return None

    day = int(raw_day)

    if day not in range(1, 32):
        return None

    return day


def process_month(raw_month: str) -> int | None:
    if (len(raw_month) != MONTH_LENGTH
            or raw_month[0] not in DIGITS
            or raw_month[1] not in DIGITS):
        return None

    month = int(raw_month)

    if month not in range(1, 13):
        return None

    return month


def process_year(raw_year: str) -> int | None:
    if (len(raw_year) != YEAR_LENGTH
            or raw_year[0] not in DIGITS
            or raw_year[1] not in DIGITS
            or raw_year[2] not in DIGITS
            or raw_year[3] not in DIGITS):
        return None

    return int(raw_year)


def extract_date(maybe_dt: str) -> Date | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: Date | None
    """

    if maybe_dt.count("-") != DATE_HYPHEN_COUNT:
        return None

    raw_day, raw_month, raw_year = maybe_dt.split("-")

    day = process_day(raw_day)

    if day is None:
        return None

    month = process_month(raw_month)

    if (month is None
            or (month in SMALL_MONTHS and day == BIG_MONTH_DAY_COUNT)):
        return None

    year = process_year(raw_year)

    if (year is None
            or (day != LEAP_YEAR_DAY_COUNT
                and month == FEBRUARY and is_leap_year(year))
            or (day > LEAP_YEAR_DAY_COUNT - 1
                and month == FEBRUARY and not is_leap_year(year))):
        return None

    return day, month, year


def add_date(day: int, month: int, year: int) -> None:
    if year not in database:
        database[year] = {}

    if month not in database[year]:
        database[year][month] = {}

    if day not in database[year][month]:
        database[year][month][day] = {}


def add_income(amount: float, date: Date) -> str:
    day, month, year = date

    add_date(day, month, year)

    income = database[year][month][day].get("income", float(0))

    if isinstance(income, float):
        database[year][month][day]["income"] = income + amount

    return OP_SUCCESS_MSG


def add_cost(category_name: str, amount: float, date: Date) -> str:
    day, month, year = date

    add_date(day, month, year)

    costs = database[year][month][day].get("costs", {})

    if isinstance(costs, dict):
        category_cost = costs.get(category_name, float(0))

        costs[category_name] = category_cost + amount

        database[year][month][day]["costs"] = costs

    return OP_SUCCESS_MSG


def get_capital(date: Date) -> tuple[float, float, float]:
    final_day, final_month, final_year = date
    total_capital, monthly_income, monthly_costs = float(0), float(0), float(0)

    for year, months in database.items():
        if year > final_year:
            continue

        for month, days in months.items():
            if year == final_year and month > final_month:
                continue

            for day, data in days.items():
                if year == final_year and month == final_month and day > final_day:
                    continue

                day_income = data.get("income", float(0))

                costs_dict = data.get("costs", {})
                day_costs = sum(costs_dict.values()) if isinstance(costs_dict, dict) else float(0)

                if not isinstance(day_income, float):
                    continue

                total_capital += (day_income - day_costs)

                if year == final_year and month == final_month:
                    monthly_income += day_income
                    monthly_costs += day_costs

    return total_capital, monthly_income, monthly_costs


def get_stats(date: Date) -> Stats | None:
    day, month, year = date

    if (year not in database
            or month not in database[year]
            or day not in database[year][month]):
        return None

    return database[year][month][day], get_capital(date)


def format_stats(stats: Stats, date: str) -> str:
    funds, info = stats

    total_capital, monthly_income, monthly_costs = info

    difference_type = "прибыль составила" if monthly_costs <= monthly_income else "убыток составил"
    difference = abs(monthly_costs - monthly_income)

    result: list[str] = [f"Ваша статистика по состоянию на {date}:"]
    result.append(f"Суммарный капитал: {total_capital} рублей")
    result.append(f"B этом месяце {difference_type} {difference} рублей")
    result.append(f"Доходы: {monthly_income} рублей")
    result.append(f"Расходы: {monthly_costs} рублей\n")
    result.append("Детализация (категория: сумма):")

    costs = funds.get("costs", {})

    if isinstance(costs, dict) and costs:
        for number, category in enumerate(sorted(costs.keys()), 1):
            result.append(f"{number}. {category}: {costs[category]}")

    return "\n".join(result)


def income_handler(params: list[str]) -> str:
    if len(params) != INCOME_PARAMS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount = float(params[0].replace(",", "."))

    if amount is None:
        return INCORRECT_AMOUNT_MSG

    if amount <= float(0):
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(params[1])

    if date is None:
        return INCORRECT_DATE_MSG

    return add_income(amount, date)


def cost_handler(params: list[str]) -> str:
    if len(params) != COST_PARAMS_COUNT:
        return UNKNOWN_COMMAND_MSG

    category_name = params[0]

    amount = float(params[1].replace(",", "."))

    if amount is None:
        return INCORRECT_AMOUNT_MSG

    if amount <= float(0):
        return NONPOSITIVE_VALUE_MSG

    date = extract_date(params[2])

    if date is None:
        return INCORRECT_DATE_MSG

    return add_cost(category_name, amount, date)


def stats_handler(params: list[str]) -> str:
    if len(params) != STATS_PARAMS_COUNT:
        return UNKNOWN_COMMAND_MSG

    date = extract_date(params[0])

    if date is None:
        return INCORRECT_DATE_MSG

    stats = get_stats(date)

    if stats is None:
        return INCORRECT_DATE_MSG

    return format_stats(stats, params[0])


def main() -> None:
    input_list = input().split(" ")

    query = input_list[0]

    while query != "exit":
        match query:
            case "income":
                response = income_handler(input_list[1:])

            case "cost":
                response = cost_handler(input_list[1:])

            case "stats":
                response = stats_handler(input_list[1:])

            case _:
                response = UNKNOWN_COMMAND_MSG

        print(response)

        input_list = input().split(" ")

        query = input_list[0]


if __name__ == "__main__":
    main()
