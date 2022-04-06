from datetime import datetime, timedelta

def from_iso_to_datetime(iso_date: str) -> datetime:
    t = datetime.strptime(iso_date.split(".")[0], '%Y-%m-%dT%H:%M:%S')
    t = t + timedelta(microseconds=int(iso_date.split(".")[1][:-1])/1000)

    return t