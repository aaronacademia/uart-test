#!/bin/bash

echo "Starting UART test..."

# Start socat in the background
socat PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0 & SOCAT_PID=$!

# Give socat time to create the virtual ports
sleep 1

# Start the Python logger in the background
source venv/bin/activate
python3 host_logger.py & LOGGER_PID=$!

# Give Python time to open the port
sleep 1

# Run the C firmware simulator
./device_sim

# Wait for Python to finish processing
wait $LOGGER_PID

# Clean up socat
kill $SOCAT_PID 2>/dev/null

echo "Test complete."
