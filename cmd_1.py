# Developed on Python 3.12.0
# Requires the following packages:
# pip install prompt-toolkit

import threading
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout

import be

http_list = []
https_list = []
icmp_list = []
dns_list = []
ntp_list = []
tcp_list = []
udp_list = []
echo_list = []

print_event = threading.Event()

# Worker thread function
def worker(stop_event: threading.Event) -> None:
    """
    Function run by the worker thread.
    Prints a message every 5 seconds until stop_event is set.
    """
    while not stop_event.is_set():
        time.sleep(5)

# Worker thread function for HTTP monitoring
def http_worker(http_item):
    address, interval = http_item
    while True:
        if print_event.is_set():
            result = be.check_server_http(address)
            print(f"HTTP Status for {address}: {result}")
            time.sleep(interval)

def https_worker(https_item):
    address, interval = https_item
    while True:
        if print_event.is_set():
            result = be.check_server_https(address)
            print(f"HTTPS Status for {address}: {result}")
            time.sleep(interval)

def icmp_worker(icmp_item):
    address, interval = icmp_item
    while True:
        if print_event.is_set():
            result_add, result_time = be.ping(address)
            print(f"ICMP Status for {address}: Response Address {result_add} Total Ping Time: {result_time}")
            time.sleep(interval)

def dns_worker(dns_item):
    server, query, record_type, interval = dns_item
    while True:
        if print_event.is_set():
            status, result = be.check_dns_server_status(server, query, record_type)
            status_str = "UP" if status else "DOWN"
            print(f"DNS Server {server} is {status_str}. Query result: {result}")
            time.sleep(interval)

def ntp_worker(ntp_item):
    ntp_server, time_interval = ntp_item
    while True:
        if print_event.is_set():
            ntp_server_status, ntp_server_time = be.check_ntp_server(ntp_server)
            status_str = "UP" if ntp_server_status else "DOWN"
            print(f"NTP Server {ntp_server} is {status_str}. Query result: {ntp_server_time}")
            time.sleep(time_interval)

def tcp_worker(tcp_item):
    TCP_server, TCP_port_number, time_interval = tcp_item
    while True:
        if print_event.is_set():
            tcp_port_status, tcp_port_description = be.check_tcp_port(TCP_server, TCP_port_number)
            print(f"Server: {TCP_server}, TCP Port: {TCP_port_number}, TCP Port Status: {tcp_port_status}, Description: {tcp_port_description}")
            time.sleep(time_interval)

def udp_worker(udp_item):
    UDP_server, UDP_port_number, time_interval = udp_item
    while True:
        if print_event.is_set():
            udp_port_status, udp_port_description = be.check_udp_port(UDP_server, UDP_port_number)
            print(f"Server: {UDP_server}, TCP Port: {UDP_port_number}, TCP Port Status: {udp_port_status}, Description: {udp_port_description}")
            time.sleep(time_interval)

def echo_worker(echo_item):
    address, port, interval = echo_item
    while True:
        if print_event.is_set():
            result = be.tcp_server(address, port, "Hello, echo server!")
            status_str = "UP" if result else "DOWN"
            print(f"Echo Server {address}:{port} is {status_str}.")
            time.sleep(interval)

# Main function
def main() -> None:
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and ensures
    the prompt stays at the bottom of the terminal.
    """
    # Event to signal the worker thread to stop
    stop_event: threading.Event = threading.Event()

    # Create and start the worker thread
    worker_thread: threading.Thread = threading.Thread(target=worker, args=(stop_event,))
    worker_thread.start()

    # Command completer for auto-completion
    # This is where you will add new auto-complete commands
    command_completer: WordCompleter = WordCompleter(['exit', 'HTTP', 'HTTPS', 'ICMP', 'DNS', "NTP", "begin", "ECHO"], ignore_case=True)

    # Create a prompt session
    session: PromptSession = PromptSession(completer=command_completer)

    # Variable to control the main loop
    is_running: bool = True

    try:
        with patch_stdout():
            while is_running:

                # Using prompt-toolkit for input with auto-completion
                user_input: str = session.prompt("Select the service that you want to monitor: ")

                # This is where you create the actions for your commands
                if user_input == "exit":
                    print("Exiting application...")
                    is_running = False
                
                elif user_input == "begin":
                    print_event.set()

                else:
                
                    if user_input == "HTTP":
                        domain_ip: str = session.prompt("Enter the target domain: \n")
                        time_interval: str = session.prompt("Enter frequency of check (in seconds): \n")
                        time_interval = int(time_interval)  # Convert the time_interval to an integer
                        http_list.append((domain_ip, time_interval))

                        # Create and start a new thread for each item in http_list
                        for http_item in http_list:
                            http_thread = threading.Thread(target=http_worker, args=(http_item,))
                            http_thread.daemon = True  # Ensures thread stops when main program exits
                            http_thread.start()

                    elif user_input == "HTTPS":
                        domain_ip_https: str = session.prompt("Enter the target domain: \n")
                        time_interval_https: str = session.prompt("Enter frequency of check (in seconds): \n")
                        time_interval_https = int(time_interval_https)
                        https_list.append((domain_ip_https, time_interval_https))

                        # Create and start a new thread for each item in http_list
                        for https_item in https_list:
                            https_thread = threading.Thread(target=https_worker, args=(https_item,))
                            https_thread.daemon = True  # Ensures thread stops when main program exits
                            https_thread.start()
                        

                    elif user_input == "ICMP":
                        icmp_ping: str = session.prompt("Enter the target ip: \n")
                        time_interval_icmp: str = session.prompt("Enter frequency of check (in seconds): \n")
                        time_interval_icmp = int(time_interval_icmp)
                        icmp_list.append((icmp_ping, time_interval_icmp))

                        # Create and start a new thread for each item in http_list
                        for icmp_item in icmp_list:
                            icmp_thread = threading.Thread(target=icmp_worker, args=(icmp_item,))
                            icmp_thread.daemon = True  # Ensures thread stops when main program exits
                            icmp_thread.start()

                    elif user_input == "DNS":
                        dns_server: str = session.prompt("Enter the DNS server address: \n")
                        query_domain: str = session.prompt("Enter the domain to query: \n")
                        record_type: str = session.prompt("Enter the DNS record type (A, AAAA, MX, etc.): \n")
                        time_interval_dns: str = session.prompt("Enter frequency of check (in seconds): \n")
                        time_interval_dns = int(time_interval_dns)  # Convert the time_interval to an integer

                        # Append the DNS monitoring settings to the dns_list
                        dns_list.append((dns_server, query_domain, record_type, time_interval_dns))

                        # Create and start a new thread for each item in dns_list
                        for dns_item in dns_list:
                            dns_thread = threading.Thread(target=dns_worker, args=(dns_item,))
                            dns_thread.daemon = True  # Ensures thread stops when main program exits
                            dns_thread.start()

                    elif user_input == "NTP":
                        ntp_server: str = session.prompt("Enter the NTP server address: \n")
                        time_interval_ntp: str = session.prompt("Enter frequency of check (in seconds): \n")
                        time_interval_ntp = int(time_interval_ntp)

                        ntp_list.append((ntp_server, time_interval_ntp))

                        for ntp_item in ntp_list:
                            ntp_thread = threading.Thread(target=ntp_worker, args=(ntp_item,))
                            ntp_thread.daemon = True  # Ensures thread stops when main program exits
                            ntp_thread.start()
                        
                    elif user_input == "TCP":
                        TCP_server: str = session.prompt("Enter the TCP server address: \n")
                        TCP_port_number: str = session.prompt("Enter the TCP port no.: \n")
                        TCP_port_number = int(TCP_port_number)
                        time_interval_tcp: str = session.prompt("Enter frequency of check (in seconds): \n")
                        time_interval_tcp = int(time_interval_tcp)

                        tcp_list.append((TCP_server, TCP_port_number, time_interval_tcp))

                        for tcp_item in tcp_list:
                            tcp_thread = threading.Thread(target=tcp_worker, args=(tcp_item,))
                            tcp_thread.daemon = True  # Ensures thread stops when main program exits
                            tcp_thread.start()

                    elif user_input == "UDP":
                        UDP_server: str = session.prompt("Enter the UDP target ip address: \n")
                        UDP_port_number: str = session.prompt("Enter the UDP port no.: \n")
                        UDP_port_number = int(UDP_port_number)
                        time_interval_udp: str = session.prompt("Enter frequency of check (in seconds): \n")
                        time_interval_udp = int(time_interval_udp)

                        udp_list.append((UDP_server, UDP_port_number, time_interval_udp))

                        for udp_item in udp_list:
                            udp_thread = threading.Thread(target=udp_worker, args=(udp_item,))
                            udp_thread.daemon = True  # Ensures thread stops when main program exits
                            udp_thread.start()

                    elif user_input == "ECHO":
                        echo_ip: str = session.prompt("Enter the target echo server IP: \n")
                        echo_port: str = session.prompt("Enter the target echo server port: \n")
                        echo_interval: str = session.prompt("Enter frequency of check (in seconds): \n")
                        echo_interval = int(echo_interval)  # Convert the echo_interval to an integer
                        echo_port = int(echo_port)  # Convert the echo_port to an integer
                        echo_list.append((echo_ip, echo_port, echo_interval))

                        # Create and start a new thread for each item in echo_list
                        for echo_item in echo_list:
                            echo_thread = threading.Thread(target=echo_worker, args=(echo_item,))
                            echo_thread.daemon = True  # Ensures thread stops when main program exits
                            echo_thread.start()

                    is_running = True
                
    finally:
        # Signal the worker thread to stop and wait for its completion
        stop_event.set()
        worker_thread.join()


if __name__ == "__main__":
    main()