import flask_server, spi_ops, config, prometheus_server
import sys

if __name__=='__main__':
    try:
        spi_ops.setup_spi()
        prometheus_server.start_prometheus_server()
        flask_server.start_flask_server()

    except KeyboardInterrupt:
        print("\nShutting down...")
        spi_ops.close_spi()
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        spi_ops.close_spi()
        sys.exit(1)
