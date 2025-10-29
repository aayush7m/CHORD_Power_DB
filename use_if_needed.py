# def find_available_port(start_port, max_attempts=100):
#     """Find an available port starting from start_port"""
#     for port in range(start_port, start_port + max_attempts):
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.bind(('localhost', port))
#                 return port
#         except OSError:
#             print(f"port : {port} is bad")
#             continue
#         except Exception as e:
#             print(f"port : {port} is bad. (big)")
#             continue
#     return None


# def start_prometheus_server():
#     """Start Prometheus server with error handling"""
#     try:
#         available_port = find_available_port(config.prometheus_port)
#         if available_port:
#             start_http_server(config.prometheus_port, addr=config.prometheus_ip)
#             if available_port != config.prometheus_port:
#                 print(f"Port {config.prometheus_port} is already in use, so found an available port.")
#             print(f"Prometheus server started on {config.prometheus_ip}:{config.prometheus_port}")
#         else:
#             raise Exception()
#     except Exception as e:
#         print(f"Failed to start Prometheus server: {e}")