#!/bin/bash
# Runs the full UART test: virtual serial link, C device simulator,
# Python host logger, then the plot.
set -e
cd "$(dirname "$0")"

if ! command -v socat >/dev/null 2>&1; then
	echo "socat is not installed. Install it with:"
	echo "  macOS:  brew install socat"
	echo "  Ubuntu: sudo apt install socat"
	exit 1
fi

# Build the device simulator if it's missing or older than its source
if [ ! -x device_sim ] || [ device_sim.c -nt device_sim ]; then
	echo "Compiling device_sim.c..."
	gcc -Wall -Wextra -o device_sim device_sim.c
fi

# Use the virtual environment if there is one
if [ -f venv/bin/activate ]; then
	source venv/bin/activate
fi

echo "Starting UART test..."

# Create a linked pair of virtual serial ports
socat PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0 &
SOCAT_PID=$!
trap 'kill $SOCAT_PID 2>/dev/null' EXIT

# Wait (up to 5 s) for socat to create both ports
for _ in $(seq 50); do
	[ -e /tmp/ttyV0 ] && [ -e /tmp/ttyV1 ] && break
	sleep 0.1
done

# Start the host logger, then give it a moment to open its port
python3 host_logger.py &
LOGGER_PID=$!
sleep 1

# Run the device simulator (sends the packets)
./device_sim

# Wait for the logger to finish and keep its exit code
wait $LOGGER_PID

python3 plot_results.py

echo "Test complete."
