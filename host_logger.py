import serial
import csv
import numpy as np
from datetime import datetime

PORT = "/tmp/ttyV1"
BAUD = 9600
TIMEOUT = 15
V_LOW = 1.5
V_HIGH = 3.0
OUT_FILE = "results.csv"

readings = []

print(f"Connecting to {PORT}...")
ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
print("Connected. Waiting for data...\n")

while True:
	line = ser.readline().decode("utf-8").strip()
	if not line:
		break

	parts = line.split(",")
	if len(parts) != 3:
		continue

	pkt_id = int(parts[0].split(":")[1])
	adc_raw = int(parts[1].split(":")[1])
	voltage = float(parts[2].split(":")[1])

	result = "PASS" if V_LOW <= voltage <= V_HIGH else "FAIL"

	readings.append({
		"pkt_id": pkt_id,
		"adc_raw": adc_raw,
		"voltage": voltage,
		"result": result,
	})

	print(f"PKT {pkt_id:02d} | ADC {adc_raw:04d} | {voltage:.4f} V | {result}")

ser.close()

voltages = np.array([r["voltage"] for r in readings])
failures = [r for r in readings if r["result"] == "FAIL"]

print(f"\n--- Summary ---")
print(f"Total packets : {len(readings)}")
print(f"Pass          : {len(readings) - len(failures)}")
print(f"Fail          : {len(failures)}")
print(f"Min voltage   : {np.min(voltages):.4f} V")
print(f"Max voltage   : {np.max(voltages):.4f} V")
print(f"Mean voltage  : {np.mean(voltages):.4f} V")
print(f"Std dev       : {np.std(voltages):.4f} V")

with open(OUT_FILE, "w", newline="") as f:
	writer = csv.writer(f)
	writer.writerow(["pkt_id", "adc_raw", "voltage_V", "result"])
	for r in readings:
		writer.writerow([r["pkt_id"], r["adc_raw"], r["voltage"], r["result"]])

print(f"\nResults written to {OUT_FILE}")
