from datetime import datetime


# Эта функция не выполняет никаких ассинхронных операций
def get_truncated_time(time):
    return datetime.strptime((time.strftime("%H:%M:00")), "%H:%M:00")
