# Gunicorn configuration for memory-constrained environments
import multiprocessing

# Server socket
bind = "0.0.0.0:10000"

# Worker processes
workers = 1  # Use only 1 worker to minimize memory usage
worker_class = "sync"
worker_connections = 1000
timeout = 300  # Increased timeout for model loading (5 minutes)

# Memory management
max_requests = 100  # Restart workers after 100 requests to prevent memory leaks
max_requests_jitter = 10
preload_app = False  # Don't preload to avoid loading models at startup

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
