def convert_int_list_base(int_list, format_type):
    if format_type.lower() == "hex":
        return [hex(i) for i in int_list]
    elif format_type.lower() == "dec":
        return [str(i) for i in int_list]
    elif format_type.lower() == "bin":
        return [bin(i) for i in int_list]
    else:
        raise ValueError(f"Unsupported format: {format_type}. Use 'hex', 'dec', or 'bin'")
    
def bin8_to_int(binary_input):
    if isinstance(binary_input, str):
        binary_list = [int(c) for c in binary_input]
    elif isinstance(binary_input, list):
        binary_list = binary_input
    else:
        raise TypeError("Input must be a string or list")
    
    # Convert binary to integer
    result = 0
    for i, bit in enumerate(binary_list):
        result += bit * (2 ** (7 - i))
    
    return [result]

def two_bytes_to_int(byte_list):
    if not isinstance(byte_list, list) or len(byte_list) != 2:
        raise ValueError("Input must be a list with exactly 2 elements")
    
    if not all(isinstance(b, int) and 0 <= b <= 255 for b in byte_list):
        raise ValueError("Each element must be an integer between 0 and 255")
    
    return (byte_list[0] << 8) | byte_list[1]
