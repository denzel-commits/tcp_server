from http.client import responses
from urllib.parse import urlparse, parse_qs


def get_param(url, param_key):
    query_string = parse_qs(urlparse(url).query)

    return (query_string[param_key][0] if param_key in query_string else None)


def parse_client_request(client_data):
    request = client_data.split("\r\n")

    request_parts = ("method", "uri", "version")

    return {"headers": [header for header in request[1:] if header != ""],
            "request": dict(zip(request_parts, request[0].split()))}


def validate_status_code(status_code):
    return 200 if not status_code or int(status_code) not in responses else int(status_code)
