# cccc
# ./prometheus --config.file=prometheus.yml
spi_bus = 0 
spi_device = 0
board_ct = 2

speed_hz = 1000000
mode = 0x01

post_ip = "localhost"
post_port = 5000

flask_ip = "0.0.0.0"
flask_port = 5000

prometheus_ip = "localhost"
prometheus_port = 8000 # prometheus server listens on port 8000 as specified in the yml file.
# yml file in ~/Documents/prometheus_server_aayush/smth/prometheus.yml

get_diag_freq = 4


class Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
