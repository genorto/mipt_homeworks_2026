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
database: dict[Date, Funds] = {}


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


def add_date(date: Date) -> None:
    if date not in database:
        database[date] = {}


def add_income(amount: float, date: Date) -> str:
    add_date(date)

    funds = database[date]
    if isinstance(funds, dict):
        income = funds.get(INCOME, float(0))
        if isinstance(income, float):
            database[date][INCOME] = income + amount

    return OP_SUCCESS_MSG


def add_cost(category_name: str, amount: float, date: Date) -> str:
    add_date(date)

    costs = database[date].get(COSTS, {})
    if isinstance(costs, dict):
        category_cost = costs.get(category_name, float(0))
        costs[category_name] = category_cost + amount
        database[date][COSTS] = costs

    return OP_SUCCESS_MSG


def get_capital_date(data: tuple[Date, Funds], target_date: Date) -> list[float]:
    result = [float(0), float(0), float(0)]

    income = data[1].get(INCOME, float(0))
    costs_dict = data[1].get(COSTS, {})
    costs = float(0)

    if isinstance(costs_dict, dict):
        costs = sum(cost for cost in costs_dict.values() if isinstance(cost, float))

    if isinstance(income, float):
        result[0] += income - costs

        if data[0][2] == target_date[2] and data[0][1] == target_date[1]:
            result[1] += income
            result[2] += costs

    return result


def get_capital(target_date: Date) -> tuple[float, float, float]:
    total_capital = float(0)
    monthly_income = float(0)
    monthly_costs = float(0)

    for data in database.items():
        if data[0][2] == target_date[2] and data[0][1] == target_date[1] and data[0][0] > target_date[0]:
            continue

        result = get_capital_date(data, target_date)
        total_capital += result[0]
        monthly_income += result[1]
        monthly_costs += result[2]

    return total_capital, monthly_income, monthly_costs


def get_stats(date: Date) -> Stats:
    if date not in database:
        return {}, get_capital(date)
    return database[date], get_capital(date)


def format_stats(stats: Stats, date: str) -> str:
    costs: dict[str, float] = {}

    if isinstance(stats, dict) and stats:
        costs = stats[0][COSTS]

    difference_type = "прибыль составила" if stats[1][2] <= stats[1][1] else "убыток составил"

    result: list[str] = [f"Ваша статистика по состоянию на {date}:"]
    result.append(f"Суммарный капитал: {stats[1][0]} рублей")
    result.append(f"B этом месяце {difference_type} {abs(stats[1][1] - stats[1][2])} рублей")
    result.append(f"Доходы: {stats[1][1]} рублей")
    result.append(f"Расходы: {stats[1][2]} рублей\n")
    result.append("Детализация (категория: сумма):")

    if isinstance(costs, dict):
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

    return format_stats(get_stats(date), params[0])


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
