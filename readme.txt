To use AT Commands for Sim800L V2:
minicom -b 9600 -D /dev/serial0


## BeaconDB in this system

This system uses **BeaconDB** as a free and open alternative to the discontinued Mozilla Location Service (MLS).
The SIM800L GSM module provides the current network cell tower information (LAC and CellID), which is then
queried against BeaconDB to estimate the device’s approximate geographic location without relying on GPS.

- **Why BeaconDB?**
  - MLS was shut down in 2024.
  - BeaconDB provides a community-maintained, free, and open API for cell tower and Wi-Fi based geolocation.

- **How it works:**
  1. The device sends AT commands to the GSM modem to retrieve the current cell tower info.
  2. LAC and CellID values are converted to decimal format.
  3. The data is sent to the BeaconDB API.
  4. The response contains approximate latitude/longitude and accuracy in meters.