def display_logs(log_callback, msg):
    if log_callback:
        log_callback(msg)
    else:
        print(msg)