/*
rank2device.cu
*/

// rank -> device number
int rank2device(int commrank, int nhost, const int ndevice[])
{
	int device = 0;

	if (nhost <= 1) {
		// single node
		device = commrank;
	}
	else {
		// cluster
		device = -1;
		int rank = -1;
		for (int ihost = 0; ihost < nhost; ihost++) {
			for (int idevice = 0; idevice < ndevice[ihost]; idevice++) {
				if (++rank == commrank) {
					device = idevice;
					break;
				}
			}
			if (device >= 0) {
				break;
			}
		}
		if (device < 0) device = 0;
	}

	int num_device;
	cudaGetDeviceCount(&num_device);
	if (device >= num_device) device = num_device - 1;

	return device;
}
