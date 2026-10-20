#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>

#define PORT "/tmp/ttyV0"
#define NUM_PACKETS 20
#define PACKET_INTERVAL_US 100000  /* 100 ms between packets */

#define ADC_MAX 4095
#define VREF 3.3f

/* Normal readings: about 2.25 V plus up to +/-0.16 V of noise,
   which stays inside the host's 1.5 to 3.0 V limits. */
#define ADC_NOMINAL 2792
#define ADC_NOISE 200

/* Fault injection: these packets send a low reading, so the host
   should report exactly these two packets as FAIL. */
#define FAULT_PKT_A 5
#define FAULT_PKT_B 13
#define FAULT_ADC 1200  /* 1200 * 3.3 / 4095 = 0.967 V, below V_LOW */

int main(void) {
	int fd = open(PORT, O_WRONLY);
	if (fd < 0) {
		perror("open " PORT);
		return 1;
	}

	printf("Device simulator connected to %s\n", PORT);

	srand(time(NULL));

	for (int i = 0; i < NUM_PACKETS; i++) {
		int adc_count = ADC_NOMINAL + (rand() % (2 * ADC_NOISE + 1)) - ADC_NOISE;

		if (i == FAULT_PKT_A || i == FAULT_PKT_B)
			adc_count = FAULT_ADC;

		float voltage = adc_count * (VREF / ADC_MAX);

		char packet[64];
		int len = snprintf(packet, sizeof(packet), "PKT:%02d,ADC:%04d,VOLT:%.4f\n", i, adc_count, voltage);

		if (write(fd, packet, len) != len) {
			perror("write");
			close(fd);
			return 1;
		}

		usleep(PACKET_INTERVAL_US);
	}

	close(fd);
	printf("Transmission complete.\n");
	return 0;
}
