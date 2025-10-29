import requests, argparse, json, config

BASE_URL = f"http://{config.post_ip}:{config.post_port}"

def handle_response(response):
    """Helper function to print response."""
    try:
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON response. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
    except Exception as e:
        print(f"An error occurred while handling the response: {e}")

def write_command(args):
    """Handles the write_command."""
    url = f"{BASE_URL}/write_command"
    payload = {
        "board_idx": args.board_idx,
        "chip_letter": args.chip_letter,
        "operation": args.operation,
        "states": args.states
    }
    params = {"verify": str(args.verify).lower()}
    try:
        response = requests.post(url, json=payload, params=params)
        response.raise_for_status()
        handle_response(response)
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to {url}: {e}")

def read_command(args):
    """Handles the read_command."""
    url = f"{BASE_URL}/read_command"
    payload = {
        "board_idx": args.board_idx,
        "chip_letter": args.chip_letter,
        "operation": args.operation
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        handle_response(response)
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to {url}: {e}")

def std_diag(args):
    """Handles the std_diag command."""
    url = f"{BASE_URL}/std_diag"
    try:
        response = requests.get(url)
        response.raise_for_status()
        handle_response(response)
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to {url}: {e}")

def create_parser():
    """Creates and configures the argument parser."""
    parser = argparse.ArgumentParser(description="CLI to send commands to the Flask server.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Subparser for write_command
    parser_write = subparsers.add_parser("write_command", help="Send a write command to a chip.")
    parser_write.add_argument("board_idx", type=int, help="Board index (integer).")
    parser_write.add_argument("chip_letter", type=str, choices=['a', 'b', 'A', 'B'], help="Chip letter ('a' or 'b').")
    parser_write.add_argument("operation", type=str, help="Operation name (e.g., OUT, DIAG_OLONEN, HWCR_OCL).")
    parser_write.add_argument("states", type=str, help="8-bit binary string for states (e.g., '10101010').")
    parser_write.add_argument("--verify", action="store_true", help="Verify after write (default: False).")
    parser_write.set_defaults(func=write_command)

    # Subparser for read_command
    parser_read = subparsers.add_parser("read_command", help="Send a read command to a chip.")
    parser_read.add_argument("board_idx", type=int, help="Board index (integer).")
    parser_read.add_argument("chip_letter", type=str, choices=['a', 'b', 'A', 'B'], help="Chip letter ('a' or 'b').")
    parser_read.add_argument("operation", type=str, help="Operation name (e.g., OUT, DIAG_OLON, HWCR_OCL, STD_DIAG).")
    parser_read.set_defaults(func=read_command)
 
    # Subparser for std_diag
    parser_std_diag = subparsers.add_parser("std_diag", help="Get standard diagnostic information.")
    parser_std_diag.set_defaults(func=std_diag)
    
    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)