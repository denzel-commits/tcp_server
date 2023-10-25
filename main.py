import socket
from http.client import responses
from urllib.parse import urlparse, parse_qs
from configuration import LOCALHOST, PORT


def get_param(url, param_key):
    parsed_url = urlparse(url)
    return parse_qs(parsed_url.query)[param_key][0]


def parse_client_request(client_data):
    request = client_data.split("\r\n")

    request_parts = ("method", "uri", "version")

    return {"headers": [header for header in request[1:] if header != ""],
            "request": dict(zip(request_parts, request[0].split()))}


def get_status_code(status_code):
    if int(status_code) not in responses:
        return 200

    return status_code


def http_headers(status_code):
    status_code = get_status_code(status_code)
    return (
        f"HTTP/1.0 {status_code} {responses[status_code]}\r\n"
        f"Server: otusdemo\r\n"
        f"Date: Sat, 01 Oct 2022 09:39:37 GMT\r\n"
        f"Content-Type: text/html; charset=UTF-8\r\n"
        f"\r\n"
        ).encode()


def http_body(client_data_parsed, client_address):
    status_code = get_status_code(int(get_param(client_data_parsed["request"]["uri"], "status")))

    method = client_data_parsed["request"]["method"]
    headers = "\r\n".join(client_data_parsed["headers"])

    return (
            f"\r\nRequest Method: {method}"
            f"\r\nRequest Source: {client_address}"
            f"\r\nResponse status: {status_code} {responses[status_code]}"
            f"\r\n{headers}"
        ).encode()


end_of_stream = '\r\n\r\n'


def handle_client(connection, client_address):
    client_data = ''
    with connection:
        while True:
            data = connection.recv(1024)
            print("Received:", data)
            if not data:
               break
            client_data += data.decode()
            if end_of_stream in client_data:
                break

        client_data_parsed = parse_client_request(client_data)
        print(client_data_parsed)

        # Send current server time to the client
        connection.send(http_headers(int(get_param(client_data_parsed["request"]["uri"], "status")))
                        + http_body(client_data_parsed, client_address)
                        + "\r\n".encode()
                        )

        #print("Sent %s to %s"%(serverTimeNow, clientAddress));


with socket.socket() as server_socket:

    # Bind the tcp socket to an IP and port
    server_socket.bind((LOCALHOST, PORT))
    # Keep listening
    server_socket.listen()

    while(True): # Keep accepting connections from clients
        (client_connection, client_address) = server_socket.accept()
        handle_client(client_connection, client_address)
        print(f"Sent data to {client_address}")
