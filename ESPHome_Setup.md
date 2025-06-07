# ESPHome BenQ Projector Control Setup Guide

This guide explains how to set up the ESPHome-based BenQ projector control system as a replacement for the Python `benqd.py` script.

## Hardware Requirements

1. **ESP32 Development Board** (ESP32-DEVKIT-V1 or similar)
2. **RS232 to TTL Converter Module** (MAX3232 based)
3. **BenQ Projector with RS232 Control Port**
4. **Connecting Wires**

## Wiring Diagram

```
ESP32          RS232-TTL Module      BenQ Projector
GPIO17 (TX) -> TX                    
GPIO16 (RX) -> RX                    
3.3V        -> VCC                   
GND         -> GND                   
                                     
               RS232 Connector   -> RS232 Control Port
```

## Software Setup

### 1. Install ESPHome

```bash
pip install esphome
```

### 2. Create Secrets File

Create a `secrets.yaml` file in the same directory as your configuration:

```yaml
# secrets.yaml
wifi_ssid: "YourWiFiNetwork"
wifi_password: "YourWiFiPassword"
domain_name: "your.domain.com"
api_encryption_key: "your-32-character-api-key-here"
ota_password: "your-ota-password"
```

### 3. Compile and Upload

```bash
# Validate configuration
esphome config esp32-projector.yaml

# Compile firmware
esphome compile esp32-projector.yaml

# Upload to ESP32 (first time, use USB cable)
esphome upload esp32-projector.yaml

# For subsequent updates (over WiFi)
esphome upload esp32-projector.yaml --device IP_ADDRESS
```

## Home Assistant Integration

Once the ESP32 is running, it will automatically be discovered by Home Assistant if you have the ESPHome integration installed.

### Available Entities

1. **Switch: Projector Power** - Turn projector on/off
2. **Binary Sensor: Projector Power State** - Current power state
3. **Sensor: Projector Communication Errors** - Error counter for troubleshooting
4. **Text Sensor: Projector Last Response** - Last raw response from projector
5. **Standard ESP32 sensors** - WiFi signal, uptime, temperature

### Example Home Assistant Automations

#### Turn on projector when TV turns on:
```yaml
automation:
  - alias: "Projector follows TV"
    trigger:
      - platform: state
        entity_id: media_player.living_room_tv
        to: 'on'
    action:
      - service: switch.turn_on
        entity_id: switch.projector_power
```

#### Turn off projector after 30 minutes of inactivity:
```yaml
automation:
  - alias: "Auto-off projector"
    trigger:
      - platform: state
        entity_id: binary_sensor.projector_power_state
        to: 'on'
        for: "00:30:00"
    condition:
      - condition: state
        entity_id: media_player.living_room_tv
        state: 'off'
    action:
      - service: switch.turn_off
        entity_id: switch.projector_power
```

## Troubleshooting

### Common Issues

1. **No Communication with Projector**
   - Check wiring connections
   - Verify RS232 module power supply
   - Ensure projector RS232 control is enabled
   - Check baud rate settings (should be 115200)

2. **ESP32 Won't Connect to WiFi**
   - Verify credentials in `secrets.yaml`
   - Check WiFi signal strength
   - Monitor serial output for connection attempts

3. **Home Assistant Discovery Issues**
   - Ensure ESPHome integration is installed
   - Check API encryption key matches
   - Verify ESP32 and HA are on same network

### Debug Information

The configuration includes several debugging features:

- **UART Debug Output**: Shows raw serial communication
- **Communication Error Counter**: Tracks failed communications
- **Last Response Sensor**: Shows the last response received from projector
- **Detailed Logging**: Set logger level to DEBUG for verbose output

### Serial Monitor Commands

You can monitor the ESP32's output via serial connection:

```bash
esphome logs esp32-projector.yaml
```

Look for messages like:
- `"Projector is ON"` / `"Projector is OFF"` - Successful state queries
- `"No response from projector - timeout"` - Communication issues
- `"Unknown response: ..."` - Unexpected projector responses

## BenQ Command Protocol

The ESPHome configuration uses the same protocol as the original Python script:

- **Power Query**: `\r*pow=?#\r`
- **Power On**: `\r*pow=on#\r`  
- **Power Off**: `\r*pow=off#\r`

Expected responses:
- Power On: `*POW=ON#`
- Power Off: `*POW=OFF#`

## Migration from Python Script

If you're migrating from the original `benqd.py` script:

1. **Port Mapping**: The ESPHome system replaces the Flask web API
2. **State Tracking**: Power state is now available as a Home Assistant entity
3. **Automation**: Use Home Assistant automations instead of the Python timer system
4. **Monitoring**: Use Home Assistant's built-in monitoring instead of uptime sensors

## Advanced Configuration

### Changing Update Interval

To change how often the projector state is queried, modify the interval:

```yaml
interval:
  - interval: 60s  # Change from 30s to 60s
    then:
      - script.execute: query_projector_power
```

### Custom GPIO Pins

To use different GPIO pins for UART:

```yaml
uart:
  id: uart_bus
  tx_pin: GPIO4   # Change from GPIO17
  rx_pin: GPIO5   # Change from GPIO16
  baud_rate: 115200
```

### Adding More Commands

To add support for additional projector commands (brightness, input selection, etc.), extend the scripts section with new commands following the same pattern.
