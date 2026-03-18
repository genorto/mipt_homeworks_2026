#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_AMOUNT_MSG = "Invalid amount!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

INCOME = "income"
COSTS = "costs"

SHORT_MONTHS = (4, 6, 9, 11)
FEBRUARY = 2
LONG_MONTH_DAYS = 31
LEAP_YEAR_FEBRUARY_DAYS = 29

DATE_HYPHEN_COUNT = 2
INCOME_PARAMS_COUNT = 2
COST_PARAMS_COUNT = 3
STATS_PARAMS_COUNT = 1

Date = tuple[int, int, int]
Funds = dict[str, float | dict[str, float]]
Stats = tuple[Funds, tuple[float, float, float]]

MonthData = dict[int, Funds]
YearData = dict[int, MonthData]
database: dict[int, YearData] = {}


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True

    return bool(year % 4) and not bool(year % 100)


def process_day(raw_day: str) -> int | None:
    if not raw_day.isdigit():
        return None

    day = int(raw_day)

    if day not in range(1, 32):
        return None

    return day


def process_month(raw_month: str) -> int | None:
    if not raw_month.isdigit():
        return None

    month = int(raw_month)

    if month not in range(1, 13):
        return None

    return month


def process_year(raw_year: str) -> int | None:
    if not raw_year.isdigit():
        return None

    year = int(raw_year)

    if year not in range(10000):
        return None

    return year


def extract_date(maybe_dt: str) -> Date | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: Date | None
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

    is_leap = is_leap_year(year)
    if month == FEBRUARY and (day > LEAP_YEAR_FEBRUARY_DAYS or (day == LEAP_YEAR_FEBRUARY_DAYS and not is_leap)):
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

    funds = database[year][month][day]
    if isinstance(funds, dict):
        income = funds.get(INCOME, float(0))

        if isinstance(income, float):
            database[year][month][day][INCOME] = income + amount

    return OP_SUCCESS_MSG


def add_cost(category_name: str, amount: float, date: Date) -> str:
    day, month, year = date
    add_date(day, month, year)

    costs = database[year][month][day].get(COSTS, {})

    if isinstance(costs, dict):
        category_cost = costs.get(category_name, float(0))
        costs[category_name] = category_cost + amount
        database[year][month][day][COSTS] = costs

    return OP_SUCCESS_MSG


def get_capital(date: Date) -> tuple[float, float, float]:
    total_capital = float(0)
    monthly_income = float(0)
    monthly_costs = float(0)

    for year, months in database.items():
        if year <= date[2]:
            for month, days in months.items():
                if year < date[2] or month <= date[1]:
                    for day, data in days.items():
                        if year == date[2] and month == date[1] and day > date[0]:
                            continue

                        day_income = data.get(INCOME, float(0))
                        costs_dict = data.get(COSTS, {})
                        day_costs = float(0)

                        if isinstance(costs_dict, dict):
                            day_costs = sum(cost for cost in costs_dict.values() if isinstance(cost, float))
                        if isinstance(day_income, float):
                            total_capital += (day_income - day_costs)

                            if year == date[2] and month == date[1]:
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
    costs = stats[0].get(COSTS, {})
    total_capital, monthly_income, monthly_costs = stats[1]

    difference_type = "прибыль составила" if monthly_costs <= monthly_income else "убыток составил"

    result: list[str] = [f"Ваша статистика по состоянию на {date}:"]
    result.append(f"Суммарный капитал: {total_capital} рублей")
    result.append(f"B этом месяце {difference_type} {abs(monthly_costs - monthly_income)} рублей")
    result.append(f"Доходы: {monthly_income} рублей")
    result.append(f"Расходы: {monthly_costs} рублей\n")
    result.append("Детализация (категория: сумма):")

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
