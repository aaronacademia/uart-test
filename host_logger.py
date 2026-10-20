import csv

import numpy as np
import serial

from limits import V_LOW, V_HIGH

PORT = "/tmp/ttyV1"
# Required by pyserial, but a virtual PTY pair has no real line rate,
# so this value does not change the timing of the test.
BAUD = 9600
# Stop after this many seconds with no new data
TIMEOUT = 3
OUT_FILE = "results.csv"


def parse_packet(line):
	"""Parse 'PKT:05,ADC:1200,VOLT:0.9670' into (pkt_id, adc_raw, voltage).
	Returns None if the line is malformed."""
	parts = line.split(",")
	if len(parts) != 3:
		return None
	try:
		pkt_id = int(parts[0].split(":")[1])
		adc_raw = int(parts[1].split(":")[1])
		voltage = float(parts[2].split(":")[1])
	except (IndexError, ValueError):
		return None
	return pkt_id, adc_raw, voltage


readings = []
bad_lines = 0

print(f"Connecting to {PORT}...")
ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
print("Connected. Waiting for data...\n")

while True:
	line = ser.readline().decode("utf-8", errors="replace").strip()
	if not line:
		break

	packet = parse_packet(line)
	if packet is None:
		bad_lines += 1
		print(f"Skipped malformed line: {line!r}")
		continue

	pkt_id, adc_raw, voltage = packet
	result = "PASS" if V_LOW <= voltage <= V_HIGH else "FAIL"

	readings.append({
		"pkt_id": pkt_id,
		"adc_raw": adc_raw,
		"voltage": voltage,
		"result": result,
	})

	print(f"PKT {pkt_id:02d} | ADC {adc_raw:04d} | {voltage:.4f} V | {result}")

ser.close()

if not readings:
	print("No packets received. Check that device_sim ran and the ports match.")
	raise SystemExit(1)

voltages = np.array([r["voltage"] for r in readings])
failures = [r for r in readings if r["result"] == "FAIL"]

# Packet IDs should run 0, 1, 2, ... with no gaps
expected_ids = set(range(max(r["pkt_id"] for r in readings) + 1))
missing = sorted(expected_ids - {r["pkt_id"] for r in readings})

print(f"\n--- Summary ---")
print(f"Limits        : {V_LOW} to {V_HIGH} V")
print(f"Total packets : {len(readings)}")
print(f"Pass          : {len(readings) - len(failures)}")
print(f"Fail          : {len(failures)}")
print(f"Malformed     : {bad_lines}")
print(f"Missing IDs   : {missing if missing else 'none'}")
print(f"Min voltage   : {np.min(voltages):.4f} V")
print(f"Max voltage   : {np.max(voltages):.4f} V")
print(f"Mean voltage  : {np.mean(voltages):.4f} V")
print(f"Std dev       : {np.std(voltages):.4f} V")

with open(OUT_FILE, "w", newline="") as f:
	writer = csv.writer(f, lineterminator="\n")
	writer.writerow(["pkt_id", "adc_raw", "voltage_V", "result"])
	for r in readings:
		writer.writerow([r["pkt_id"], r["adc_raw"], r["voltage"], r["result"]])

print(f"\nResults written to {OUT_FILE}")
