bind = "0.0.0.0:12300"
backlog = 2048
worker_class = "sync"
workers = 8
threads = 32
# worker_class = "gevent"
# worker_connections = 1000
timeout = 30
graceful_timeout = 30
keepalive = 5

daemon = True
x_forwarded_for_header = "X-Forwarded-For"
access_log_format = "%({X-Real-IP}i)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s %(D)s"
accesslog = "access.log"
errorlog = "error.log"
