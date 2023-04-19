def prompt_port_number(proxy_name: str, protocol: str, current_ports: set):
    port = "0"
    while True:
        try:
            port = int(
                input(f"\nEnter an available {protocol} port number for {proxy_name}: ")
            )
            if 1 <= port <= 65535:
                if port in current_ports:
                    print(
                        "This port is already selected for another proxy, please choose another one."
                    )
                else:
                    current_ports.add(port)
                    break
            else:
                print("Input not valid. Please try again.")
        except ValueError:
            print("That's not an integer. Please try again.")

    return str(port), current_ports
