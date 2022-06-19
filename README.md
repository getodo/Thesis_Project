# Thesis Project
Tiny activity classification using TensorFlow Lite <br />
## Setup: <br />
1. Clone repository. <br />
2. Use ENGG4812_Neural_Network_Design to train model using data set (use dense model setup, LSTM not supported on TFLM). <br />
3. Download TFLM binary header file after training. <br />
4. Add TFLM header file to includes. <br />
5. Build and flash. <br />
6. Use GUI to receive BLE messages from device (may require some restarts to get working few bugs). <br />
<br />
Device variables (characteristic) may need to be changed in BLE.c. <br />
Array variable in predictor.c may need to be changed if array is different. <br />
