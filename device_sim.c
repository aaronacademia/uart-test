#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>

#define PORT "/tmp/ttyV0"
#define NUM_PACKETS 20
#define BAUD_DELAY 100000

int main(void) {
	int fd = open(PORT, O_WRONLY);
	if (fd < 0) {
		perror("open");
		return 1;
	}

	printf("Device simulator connected to %s\n", PORT);

	srand(time(NULL));

	for (int i = 0; i < NUM_PACKETS; i++) {
		int adc_count = (int)(rand() % 4096);

		if (i == 5 || i == 13)
			adc_count = 1200;

		float voltage = adc_count * (3.3f / 4095.0f);

		char packet[64];
		snprintf(packet, sizeof(packet), "PKT:%02d,ADC:%04d,VOLT:%.4f\n", i, adc_count, voltage);
		write(fd, packet, strlen(packet));

		usleep(BAUD_DELAY);
	}

	close(fd);
	printf("Transmission complete.\n");
	return 0;

}
