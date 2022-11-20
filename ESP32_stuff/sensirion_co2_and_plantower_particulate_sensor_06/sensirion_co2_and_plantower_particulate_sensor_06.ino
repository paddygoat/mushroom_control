#include "Adafruit_PM25AQI.h"
#include <Arduino.h>
#include <SensirionI2CScd4x.h>
#include <Wire.h>
#include <SX126x-Arduino.h>
#include <SPI.h>

#define GREEN_LED 33
#define BLUE_LED 26
#define BUZZ_PIN 12

hw_config hwConfig;

#ifdef ESP32
// ESP32 - SX126x pin configuration
int PIN_LORA_RESET = 0;  // LORA RESET
int PIN_LORA_DIO_1 = 36; // LORA DIO_1
int PIN_LORA_BUSY = 39;  // LORA SPI BUSY
int PIN_LORA_NSS = 25;	// LORA SPI CS
int PIN_LORA_SCLK = 18;  // LORA SPI CLK
int PIN_LORA_MISO = 19;  // LORA SPI MISO
int PIN_LORA_MOSI = 23;  // LORA SPI MOSI
int RADIO_TXEN = -1;	 // LORA ANTENNA TX ENABLE
int RADIO_RXEN = 39;	 // LORA ANTENNA RX ENABLE
#endif

// Function declarations
void OnTxDone(void);
void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr);
void OnTxTimeout(void);
void OnRxTimeout(void);
void OnRxError(void);
void OnCadDone(bool cadResult);

// Check if the board has an LED port defined
#ifdef ESP32
#define GREEN_LED 33
#endif

// Define LoRa parameters
#define RF_FREQUENCY 433500000  // Hz
#define TX_OUTPUT_POWER 2		// dBm  was 22.
#define LORA_BANDWIDTH 2		// [0: 125 kHz, 1: 250 kHz, 2: 500 kHz, 3: Reserved]
#define LORA_SPREADING_FACTOR 12 // [SF7..SF12]
#define LORA_CODINGRATE 1		// [1: 4/5, 2: 4/6,  3: 4/7,  4: 4/8]
#define LORA_PREAMBLE_LENGTH 8  // Same for Tx and Rx
#define LORA_SYMBOL_TIMEOUT 0   // Symbols
#define LORA_FIX_LENGTH_PAYLOAD_ON false
#define LORA_IQ_INVERSION_ON false
#define RX_TIMEOUT_VALUE 3000
#define TX_TIMEOUT_VALUE 3000

#define BUFFER_SIZE 64 // Define the payload size here

static RadioEvents_t RadioEvents;
static uint16_t BufferSize = BUFFER_SIZE;
static uint8_t RcvBuffer[BUFFER_SIZE];

static bool isMaster = true;
const uint8_t PingMsg[] = "PING";
const uint8_t PongMsg[] = "PONG";

time_t timeToSend;
time_t cadTime;

uint8_t pingCnt = 0;
uint8_t pongCnt = 0;

Adafruit_PM25AQI aqi = Adafruit_PM25AQI();

#define RXD2 16
#define TXD2 17

float humidity = 0.0f;
float temperature = 0.0f;
int readingsAlreadyTaken = 0;

SensirionI2CScd4x scd4x;

void loop()
{
  flash_GREEN_LED();
  readingsAlreadyTaken = 0;
  takeReadings();
  
	// We are on FreeRTOS, give other tasks a chance to run
	delay(100);
	yield();

  String header = "#*&_";
  String label = "hum:_";
  float sensorValue = humidity;

  Serial.println("Sending a data transmit:");
  myTransmit(header, label, sensorValue);

  delay(1000);  // Min = 1 seconds?
  // Do not remove this next delay line !!!
  delay(100);
  yield();

  header = "#*%_";
  label = "temp2:_";
  sensorValue = temperature;

  Serial.println("Sending another data transmit:");
  myTransmit(header, label, sensorValue);

  delay(20000);
}

float takeReadings()
{
  Serial.println("");
  Serial.println("Try to take some readings ......... ");
  if (readingsAlreadyTaken == 1)
  {
    Serial.println("Readings have already been taken!");
  }

  PM25_AQI_Data data;
  
  if (! aqi.read(&data)) 
  {
    Serial.println("Could not read from AQI .... pausing for 5 seconds ....");
    delay(5000);  // try again in a bit!
    // return;
  }

  uint16_t error;
  char errorMessage[256];

  delay(100);

  // Read Measurement
  uint16_t co2 = 0;
  // float temperature = 0.0f;
  // float humidity = 0.0f;
  bool isDataReady = false;
  error = scd4x.getDataReadyFlag(isDataReady);

  if (error) 
  {
    Serial.print("Error trying to execute readMeasurement(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
    // return;
  }
  
  if (!isDataReady) 
  {
    // return;
  }
  error = scd4x.readMeasurement(co2, temperature, humidity);

  if (error) 
  {
    Serial.print("Error trying to execute readMeasurement(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
  } else if (co2 == 0) {
    Serial.println("Invalid sample detected, skipping.");
  } else {
    Serial.print("PM_1.0:"); Serial.print(data.pm10_standard); Serial.print(", ");
    Serial.print("PM_2.5:"); Serial.print(data.pm25_standard); Serial.print(", ");
    Serial.print("PM_10:"); Serial.print(data.pm100_standard); Serial.print(", ");
    Serial.print("Co2/10:"); Serial.print(co2/10); Serial.print(", ");
    Serial.print("Temperature:"); Serial.print(temperature); Serial.print(", ");
    Serial.print("Humidity:"); Serial.println(humidity);
    Serial.println();
    readingsAlreadyTaken = 1;
  }
  return humidity;
  return temperature;
  return readingsAlreadyTaken;
}

void myTransmit(String header, String label, float sensorValue)
{
  yield();
  buzz();
    int h = 0;
    int i = 0;
    int j =0;
    int h2 = 0;
    int i2 = 0;
    int j2 =0;
    int k= 0;
    int l = 0;
    static uint8_t TxdBuffer[BUFFER_SIZE];

    for (l =0; l< BUFFER_SIZE; l++)
    {
      TxdBuffer[l] = 0;
    }


    String header2 = header;
    Serial.print("header2: ");Serial.print(header2);Serial.print("   ");
    int packetSize = sizeof(header2);
    for (h =0; h< packetSize; h++)
    {
      if (header2[h] != 0)
      {
        TxdBuffer[h] = header2[h];
        Serial.print(TxdBuffer[h]);Serial.print(",");
        h2++;
      }
    }
    Serial.println();
    Serial.print("Current TxdBuffer: ");
    for (l =0; l< 32; l++)
    {
      Serial.print(TxdBuffer[l]);Serial.print(",");
    }
    Serial.println();
 
    String label2 = label;
    Serial.print("label2: ");Serial.print(label2);Serial.print("   ");
    // Serial.print("sizeof label2:");Serial.println(sizeof(label2));
    packetSize = sizeof(label2);
    for (i =0; i< packetSize; i++)
    {
      if (label2[i] != 0)
      {
        TxdBuffer[h2+i] = label2[i];
        Serial.print(TxdBuffer[h2+i]);Serial.print(",");
        i2++;
      }
    }
    Serial.println();
    Serial.print("Current TxdBuffer: ");
    for (l =0; l< 32; l++)
    {
      Serial.print(TxdBuffer[l]);Serial.print(",");
    }
    Serial.println();
    
    String sensorValue2 = (String)sensorValue;
    Serial.print("sensorValue String: ");Serial.print(sensorValue2);Serial.print("   ");
    packetSize = sizeof(sensorValue2);
    for (j =0; j< packetSize; j++)
    {
      if (sensorValue2[j] != 0)
      {
        TxdBuffer[h2+i2+j] = sensorValue2[j];
        Serial.print(TxdBuffer[h2+i2+j]);Serial.print(",");
        j2++;
      }
    }
    Serial.println();
    Serial.print("Current TxdBuffer: ");
    for (l =0; l< 32; l++)
    {
      Serial.print(TxdBuffer[l]);Serial.print(",");
    }
    Serial.println();
    Radio.Send(TxdBuffer, BufferSize);
}

void printUint16Hex(uint16_t value) 
{
  Serial.print(value < 4096 ? "0" : "");
  Serial.print(value < 256 ? "0" : "");
  Serial.print(value < 16 ? "0" : "");
  Serial.print(value, HEX);
}

void printSerialNumber(uint16_t serial0, uint16_t serial1, uint16_t serial2) 
{
  Serial.print("Serial: 0x");
  printUint16Hex(serial0);
  printUint16Hex(serial1);
  printUint16Hex(serial2);
  Serial.println();
}

void setup()
{
  pinMode(27, OUTPUT);  
  pinMode(BUZZ_PIN, OUTPUT);
  digitalWrite(27, HIGH);
  // Define the HW configuration between MCU and SX126x
  hwConfig.CHIP_TYPE = SX1262_CHIP;     // Example uses an eByte E22 module with an SX1262
  hwConfig.PIN_LORA_RESET = PIN_LORA_RESET; // LORA RESET
  hwConfig.PIN_LORA_NSS = PIN_LORA_NSS;  // LORA SPI CS
  hwConfig.PIN_LORA_SCLK = PIN_LORA_SCLK;   // LORA SPI CLK
  hwConfig.PIN_LORA_MISO = PIN_LORA_MISO;   // LORA SPI MISO
  hwConfig.PIN_LORA_DIO_1 = PIN_LORA_DIO_1; // LORA DIO_1
  hwConfig.PIN_LORA_BUSY = PIN_LORA_BUSY;   // LORA SPI BUSY
  hwConfig.PIN_LORA_MOSI = PIN_LORA_MOSI;   // LORA SPI MOSI
  hwConfig.RADIO_TXEN = RADIO_TXEN;     // LORA ANTENNA TX ENABLE
  hwConfig.RADIO_RXEN = RADIO_RXEN;     // LORA ANTENNA RX ENABLE
  hwConfig.USE_DIO2_ANT_SWITCH = false;   // Was true. Example uses an CircuitRocks Alora RFM1262 which uses DIO2 pins as antenna control
  hwConfig.USE_DIO3_TCXO = true;        // Example uses an CircuitRocks Alora RFM1262 which uses DIO3 to control oscillator voltage
  hwConfig.USE_DIO3_ANT_SWITCH = false;  // Only Insight ISP4520 module uses DIO3 as antenna control

  // Initialize Serial for debug output
  Serial.begin(115200);

  pinMode(GREEN_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);
  flash_GREEN_LED();
  flash_BLUE_LED();

  Serial.println("=====================================");
  Serial.println("SX126x Transmit");
  Serial.println("=====================================");
  Serial.print("MOSI: ");Serial.println(MOSI);
  Serial.print("MISO: ");Serial.println(MISO);
  Serial.print("RESET: ");Serial.println(PIN_LORA_RESET);
  Serial.print("DIO_1: ");Serial.println(PIN_LORA_DIO_1);
  Serial.print("BUSY: ");Serial.println(PIN_LORA_BUSY);
  Serial.print("SCLK: ");Serial.println(PIN_LORA_SCLK);
  Serial.print("SS: ");Serial.println(SS);

#ifdef ESP32
  Serial.println("MCU Espressif ESP32");
#endif

  uint8_t deviceId[8];

  BoardGetUniqueId(deviceId);
  Serial.printf("BoardId: %02X-%02X-%02X-%02X-%02X-%02X-%02X-%02X\n",
          deviceId[7],
          deviceId[6],
          deviceId[5],
          deviceId[4],
          deviceId[3],
          deviceId[2],
          deviceId[1],
          deviceId[0]);

  flash_GREEN_LED();
  // Initialize the LoRa chip
  Serial.println("Starting lora_hardware_init ....");
  // Serial.println("TEST_01");
  
  lora_hardware_init(hwConfig);
  flash_GREEN_LED();
  Serial.println("hwConfig initialised.");
  // Serial.println("TEST_02");
  
  // Initialize the Radio callbacks
  RadioEvents.TxDone = OnTxDone;
  RadioEvents.RxDone = OnRxDone;
  RadioEvents.TxTimeout = OnTxTimeout;
  RadioEvents.RxTimeout = OnRxTimeout;
  RadioEvents.RxError = OnRxError;
  RadioEvents.CadDone = OnCadDone;

  // Serial.println("TEST_03");
  // flash_GREEN_LED();
  // Initialize the Radio
  Radio.Init(&RadioEvents);
  // flash_GREEN_LED();
  Serial.println("Radio initialised.");
  // Serial.println("TEST_04");
  
  Radio.Standby();
  
  // Required SyncWord = 0x2414.
  uint8_t my_syncword_0 = 0x14;
  uint8_t my_syncword_1 = 0x24;
  uint16_t readSyncWord = 0;

  SX126xReadRegisters(REG_LR_SYNCWORD, (uint8_t *)&readSyncWord, 0);
  Serial.print("My SyncWord 0: ");Serial.print("0x");Serial.println(readSyncWord,HEX);
  readSyncWord = 0;
  SX126xReadRegisters(REG_LR_SYNCWORD, (uint8_t *)&readSyncWord, 1);
  Serial.print("My SyncWord 1: ");Serial.print("0x");Serial.println(readSyncWord,HEX);
  readSyncWord = 0;
  SX126xReadRegisters(REG_LR_SYNCWORD, (uint8_t *)&readSyncWord, 2);
  Serial.print("My SyncWord 2: ");Serial.print("0x");Serial.println(readSyncWord,HEX);
  Serial.println();

  SX126xWriteRegister(REG_LR_SYNCWORD, my_syncword_0);
  SX126xWriteRegister(REG_LR_SYNCWORD +1, my_syncword_1);

  readSyncWord = 0;
  SX126xReadRegisters(REG_LR_SYNCWORD, (uint8_t *)&readSyncWord, 0);
  Serial.print("My SyncWord 0: ");Serial.print("0x");Serial.println(readSyncWord,HEX);
  readSyncWord = 0;
  SX126xReadRegisters(REG_LR_SYNCWORD, (uint8_t *)&readSyncWord, 1);
  Serial.print("My SyncWord 1: ");Serial.print("0x");Serial.println(readSyncWord,HEX);
  readSyncWord = 0;
  SX126xReadRegisters(REG_LR_SYNCWORD, (uint8_t *)&readSyncWord, 2);
  Serial.print("My SyncWord 2: ");Serial.print("0x");Serial.println(readSyncWord,HEX);
  
  // Set Radio channel
  Radio.SetChannel(RF_FREQUENCY);
  // flash_GREEN_LED();
  Serial.println("Frequency set.");
  // Serial.println("TEST_05");

  // Set Radio TX configuration
  Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_POWER, 0, LORA_BANDWIDTH,
            LORA_SPREADING_FACTOR, LORA_CODINGRATE,
            LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
            true, 0, 0, LORA_IQ_INVERSION_ON, TX_TIMEOUT_VALUE);

  // Set Radio RX configuration
  Radio.SetRxConfig(MODEM_LORA, LORA_BANDWIDTH, LORA_SPREADING_FACTOR,
            LORA_CODINGRATE, 0, LORA_PREAMBLE_LENGTH,
            LORA_SYMBOL_TIMEOUT, LORA_FIX_LENGTH_PAYLOAD_ON,
            0, true, 0, 0, LORA_IQ_INVERSION_ON, true);

  // Start LoRa
  // Serial.println("TEST_06");
  Serial.println("Starting Radio.Rx .....");
  // Radio.Rx(RX_TIMEOUT_VALUE);
  // Serial.println("TEST_07");
  // flash_GREEN_LED();
  Serial.println("Radio.Rx started.");
  Serial.println("Waiting for LoRa transmission ....");
  // Serial.println("TEST_08");
  // LOG_LIB("BRD", "SyncWord = %04X", readSyncWord);
  timeToSend = millis();

  Wire.begin();

  uint16_t error;
  char errorMessage[256];

  scd4x.begin(Wire);

  // Wait one second for sensor to boot up!
  flash_GREEN_LED();

  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  Serial.println("Serial2 was set.");

  if (! aqi.begin_UART(&Serial2)) 
  {
    Serial.println("Could not find PM 2.5 sensor!");
    while (1) delay(10);
  }

  // stop potentially previously started measurement
  error = scd4x.stopPeriodicMeasurement();
  if (error) 
  {
    Serial.print("Error trying to execute stopPeriodicMeasurement(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
  }

  uint16_t serial0;
  uint16_t serial1;
  uint16_t serial2;
  error = scd4x.getSerialNumber(serial0, serial1, serial2);
  if (error) 
  {
    Serial.print("Error trying to execute getSerialNumber(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
  } else {
    printSerialNumber(serial0, serial1, serial2);
  }

  // Start Measurement
  error = scd4x.startPeriodicMeasurement();
  if (error) 
  {
    Serial.print("Error trying to execute startPeriodicMeasurement(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
  }

  Serial.println("Waiting for first measurement... (5 sec)");
  delay(5000);
}

/**@brief Function to be executed on Radio Tx Done event
 */
void OnTxDone(void)
{
  Serial.println("Transmit was successful !!!!");
}

/**@brief Function to be executed on Radio Rx Done event
 */
void OnRxDone(uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr)
{
}

/**@brief Function to be executed on Radio Tx Timeout event
 */
void OnTxTimeout(void)
{
  Serial.println("There was a Tx Timeout.");
}

/**@brief Function to be executed on Radio Rx Timeout event
 */
void OnRxTimeout(void)
{
}

/**@brief Function to be executed on Radio Rx Error event
 */
void OnRxError(void)
{
}

/**@brief Function to be executed on Radio Rx Error event
 */
void OnCadDone(bool cadResult)
{
}

void flash_GREEN_LED()
{
  delay(1000);
  digitalWrite(GREEN_LED, HIGH);
  delay(1000);
  digitalWrite(GREEN_LED, LOW);
}

void flash_BLUE_LED()
{
  delay(1000);
  digitalWrite(BLUE_LED, HIGH);
  delay(1000);
  digitalWrite(BLUE_LED, LOW);
}

void buzz()
{
  for (int i = 350; i>0; --i)
  {
    digitalWrite(BUZZ_PIN, HIGH);
    delayMicroseconds(400);
    digitalWrite(BUZZ_PIN, LOW);
    delayMicroseconds(400);
  }
}
