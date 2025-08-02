import datetime


def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string format
    raise TypeError("Type not serializable")
