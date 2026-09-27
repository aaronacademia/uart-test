import csv
import matplotlib
matplotlib.use("Agg")   # no display needed — saves to file
import matplotlib.pyplot as plt

pkt_ids  = []
voltages = []
results  = []

with open("results.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pkt_ids.append(int(row["pkt_id"]))
        voltages.append(float(row["voltage_V"]))
        results.append(row["result"])

colors = ["#2ecc71" if r == "PASS" else "#e74c3c" for r in results]

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(pkt_ids, voltages, color="#888888", linewidth=1, zorder=1)
ax.scatter(pkt_ids, voltages, c=colors, s=60, zorder=2)

ax.axhline(1.5, color="#e67e22", linewidth=1.2, linestyle="--", label="V_LOW (1.5 V)")
ax.axhline(3.0, color="#9b59b6", linewidth=1.2, linestyle="--", label="V_HIGH (3.0 V)")

ax.set_xlabel("Packet ID")
ax.set_ylabel("Voltage (V)")
ax.set_title("UART ADC Voltage Readings — Pass/Fail")
ax.legend()
ax.set_xticks(pkt_ids)

plt.tight_layout()
plt.savefig("voltage_plot.png", dpi=150)
print("Plot saved to voltage_plot.png")
