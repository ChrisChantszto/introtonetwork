# Developed on Python 3.12.0
# Requires the following packages:
# pip install prompt-toolkit

import threading
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout

import be


# Worker thread function
def worker(stop_event: threading.Event) -> None:
    """
    Function run by the worker thread.
    Prints a message every 5 seconds until stop_event is set.
    """
    while not stop_event.is_set():
        print("Hello from the worker thread.")
        time.sleep(5)

ping_list = []
traceroute_list = []

# helper function
def ping_at_interval(address, interval, check, result):
    while True:
        ping_address, ping_time = be.ping(address)
        print(f"{check}: {result} - Ping Result: {ping_address}, {ping_time}")
        time.sleep(interval)

def traceroute_at_interval(address, interval, check, result):
    while True:
        current_result = be.traceroute(address)
        print(f"{check}: {result} - Ping Result: {current_result}")
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
    command_completer: WordCompleter = WordCompleter(['exit'], ignore_case=True)

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
                    for address, interval, check, result in ping_list:
                        thread = threading.Thread(target=ping_at_interval, args=(address, interval, "HTTP Status", True))
                        thread.start()
                    
                    for address, interval, check, result in traceroute_list:
                        thread = threading.Thread(target=traceroute_at_interval, args=(address, interval, "HTTP Status", True))
                        thread.start()

                else:
                
                    if user_input == "HTTP":
                        domain_ip: str = session.prompt("Enter the target domain or IP address: \n")
                        result = be.check_server_http(domain_ip)
                        if True in result:
                            p_oder_t: str = session.prompt("Do you want to ping or traceroute? \n")
                            time_interval: str = session.prompt("Enter frequency of check (in seconds): \n")
                            time_interval = int(time_interval)  # Convert the time_interval to an integer
                            if p_oder_t == "ping":
                                ping_list.append((domain_ip, time_interval, "HTTP Status", result))
                                print(ping_list)

                            elif p_oder_t == "traceroute":
                                traceroute_list.append((domain_ip, time_interval, "HTTP Status", result))

                    elif user_input == "HTTPS":
                        pass

                    elif user_input == "ICMP":
                        pass

                    elif user_input == "DNS":
                        pass

                    elif user_input == "NTP":
                        pass

                    elif user_input == "TCP":
                        pass

                    elif user_input == "UDP":
                        pass

                    elif user_input == "TCP Local Server":
                        pass

                    is_running = True
                
    finally:
        # Signal the worker thread to stop and wait for its completion
        stop_event.set()
        worker_thread.join()


if __name__ == "__main__":
    main()