from datetime import date, timedelta


def is_business_day(day: date, feriados: set[date]) -> bool:
    """Dia útil = segunda a sexta, sem feriado cadastrado."""
    return day.weekday() < 5 and day not in feriados


def add_business_days(data_base: date, dias: int, feriados: set[date]) -> date:
    """
    Conta `dias` úteis excluindo o dia base e incluindo o do vencimento
    (padrão CPC art. 224), pulando sábados, domingos e feriados.
    """
    if dias < 1:
        raise ValueError("A quantidade de dias úteis deve ser pelo menos 1")

    current = data_base
    counted = 0
    while counted < dias:
        current += timedelta(days=1)
        if is_business_day(current, feriados):
            counted += 1
    return current
