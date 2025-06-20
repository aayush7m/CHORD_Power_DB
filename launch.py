import flask_server, spi_ops, config, prometheus_server
from prometheus_client import start_http_server
import threading
import socket
import sys

def find_available_port(start_port, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def start_prometheus_server():
    """Start Prometheus server with error handling"""
    try:
        available_port = find_available_port(config.prometheus_port)
        if available_port:
            start_http_server(config.prometheus_port, addr=config.prometheus_ip)
            if available_port != config.prometheus_port:
                print(f"Port {config.prometheus_port} is already in use, so found an available port.")
            print(f"Prometheus server started on {config.prometheus_ip}:{config.prometheus_port}")
        else:
            raise Exception()
    except Exception as e:
        print(f"Failed to start Prometheus server: {e}")

if __name__=='__main__':
    try:
        spi_ops.setup_spi()
        start_prometheus_server()
        
        # Start Prometheus data fetching in a separate thread
        prometheus_thread = threading.Thread(target=prometheus_server.fetch_and_update, daemon=True)
        prometheus_thread.start()
        print("Prometheus data fetching thread started")
        
        # Start Flask server (this will block)
        print(f"Starting Flask server on {config.flask_ip}:{config.post_port}")
        flask_server.app.run(debug=True, host=config.flask_ip, port=config.post_port)
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        spi_ops.close_spi()
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        spi_ops.close_spi()
        sys.exit(1)