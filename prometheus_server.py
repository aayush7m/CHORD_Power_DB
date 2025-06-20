"""
Prometheus server that periodically fetches diagnostic data from the Flask server
and exposes it on /metrics for scraping.
"""
import time
import requests
import config, spi_ops, utilities
from prometheus_client import Gauge

# Define Prometheus Gauge metrics

gauge_diag_flag = Gauge(
    'chip_diagnostic_flag',
    'Individual diagnostic flag for each chip (0 or 1)',
    ['board', 'chip', 'flag_position', 'flag_name']
)

# URL of the Flask server diagnostic endpoint
DIAG_URL = f"http://{config.post_ip}:{config.post_port}/std_diag"

# The index corresponds to the bit position in the 16-bit string, from MSB (0) to LSB (15)
FLAG_NAMES = {
    0: "std_diag_frame_identifier",  # Bit 15: Standard Diagnosis Frame (always 0)
    1: "vs_undervoltage",            # Bit 14: Vs Undervoltage Monitor (1 = undervoltage)
    2: "vdd_low_operating_range",    # Bit 13: VDD Lower Operating Range Monitor (1 = low voltage)
    3: "operative_mode_bit_1",       # Bit 12: Part of MODE (11=Idle, 10=Active, 01=Limp Home)
    4: "operative_mode_bit_0",       # Bit 11: Part of MODE
    5: "transmission_error",         # Bit 10: TER - Transmission Error (1 = error)
    6: "open_load_on_state",         # Bit 9:  OL ON - Open Load in ON state (1 = detected)
    7: "open_load_off_state",        # Bit 8:  OL OFF - Open Load in OFF state (1 = detected)
    8: "ch7_overload_overtemp",      # Bit 7:  ERR7 - Overload/Overtemp on Channel 7 (1 = failure)
    9: "ch6_overload_overtemp",      # Bit 6:  ERR6 - Overload/Overtemp on Channel 6 (1 = failure)
    10: "ch5_overload_overtemp",     # Bit 5:  ERR5 - Overload/Overtemp on Channel 5 (1 = failure)
    11: "ch4_overload_overtemp",     # Bit 4:  ERR4 - Overload/Overtemp on Channel 4 (1 = failure)
    12: "ch3_overload_overtemp",     # Bit 3:  ERR3 - Overload/Overtemp on Channel 3 (1 = failure)
    13: "ch2_overload_overtemp",     # Bit 2:  ERR2 - Overload/Overtemp on Channel 2 (1 = failure)
    14: "ch1_overload_overtemp",     # Bit 1:  ERR1 - Overload/Overtemp on Channel 1 (1 = failure)
    15: "ch0_overload_overtemp"      # Bit 0:  ERR0 - Overload/Overtemp on Channel 0 (1 = failure)
}

def fetch_and_update():
    """
    Periodically fetch diagnostic data and update Prometheus metrics.
    """
    while True:
        try:
            response = requests.get(DIAG_URL)
            
            if response.status_code == 200:
                data = response.json()
                flat_diag_list = data.get('std_diag_response', [])
                
                if isinstance(flat_diag_list, list) and len(flat_diag_list) % 2 == 0:
                    # Reverse the flat list to get correct order (0a, 0b, 1a, 1b, etc.)
                    flat_diag_list.reverse()
                    print(f"Reversed flat diag list: {flat_diag_list}")
                    
                    # Group every 2 elements as one chip's diagnostic data
                    chip_diags = []
                    for i in range(0, len(flat_diag_list), 2):
                        chip_diags.append([flat_diag_list[i], flat_diag_list[i+1]])
                    
                    print(f"Grouped chip diags: {chip_diags}")
                    
                    # Convert to hex values and binary flags
                    for i, chip_bytes in enumerate(chip_diags):
                        if len(chip_bytes) == 2:
                            # Calculate board and chip from index
                            board_index = i // 2
                            chip_letter = 'A' if i % 2 == 0 else 'B'
                            
                            # Convert 2 bytes to hex value
                            hex_value = utilities.two_bytes_to_int(chip_bytes)
                            
                            # Convert to 16-bit binary and update individual flag metrics
                            binary_str = format(hex_value, '016b')  # 16-bit binary string
                            
                            for flag_pos, bit_char in enumerate(binary_str):
                                flag_value = int(bit_char)
                                flag_name = FLAG_NAMES.get(flag_pos, f"unknown_flag_{flag_pos}")
                                
                                gauge_diag_flag.labels(
                                    board=str(board_index),
                                    chip=chip_letter,
                                    flag_position=str(flag_pos),
                                    flag_name=flag_name
                                ).set(flag_value)
                            
                            print(f"Board {board_index}, Chip {chip_letter}: hex=0x{hex_value:04x}, binary={binary_str}")
                        else:
                            print(f"Warning: Invalid chip data at index {i}: {chip_bytes}")
                    
                    print(f"Updated metrics for {len(chip_diags)} chips")
                else:
                    print(f"Unexpected data format or length: {flat_diag_list}")
            else:
                print(f"HTTP error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"Error fetching diagnostics: {e}")

        # Wait before next fetch
        time.sleep(config.get_diag_freq)
