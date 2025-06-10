# Python Daemon vs ESPHome Comparison

This document compares the two approaches available in this repository for controlling BenQ projectors.

## Feature Comparison

| Feature | Python Daemon (`benqd.py`) | ESPHome (`esp32-projector.yaml`) |
|---------|----------------------------|-----------------------------------|
| **Hardware Requirements** | Computer/RPi running Kodi | ESP32 + RS232-TTL converter |
| **Dependencies** | Python, Flask, pyserial | ESPHome, ESP32 firmware |
| **Home Assistant Integration** | Manual REST API calls | Native ESPHome integration |
| **Power Control** | ✅ On/Off via HTTP API | ✅ On/Off via HA switch |
| **Status Monitoring** | ✅ HTTP endpoint | ✅ Binary sensor + diagnostics |
| **Scheduled Power-off** | ✅ Built-in timer with screensaver | ✅ Via HA automations |
| **Kodi Integration** | ✅ Direct addon | ⚠️ Via HA automations |
| **WiFi Connectivity** | ❌ Depends on host system | ✅ Built-in ESP32 WiFi |
| **Error Handling** | ⚠️ Basic logging | ✅ Error counting + diagnostics |
| **Communication Protocol** | ✅ RS232 with echo handling | ✅ Identical RS232 protocol |
| **OTA Updates** | ❌ Manual file updates | ✅ ESPHome OTA |
| **Dashboard Control** | ❌ API only | ✅ Home Assistant UI |
| **Real-time Monitoring** | ❌ Polling via API | ✅ Live HA entities |
| **Custom Commands** | ❌ Code modification required | ✅ HA service for any command |
| **Connection Status** | ⚠️ Basic error exceptions | ✅ Dedicated connectivity sensor |
| **Cost** | ~$0 (software only) | ~$10-15 (ESP32 + converter) |

## Communication Protocol Compatibility

Both implementations use **identical BenQ RS232 communication**:

### Command Structure
```
Send: \r*pow=?#\r     (Query power state)
Recv: *pow=?#         (Echo line)
Recv: *POW=ON#        (Response line)
```

### Python Implementation
```python
def _send_command(self, cmd):
    self.conn.reset_input_buffer()   # Clear buffers
    self.conn.reset_output_buffer()
    self.conn.write(cmd)             # Send command
    buf = self.conn.readline()       # Read echo
    buf = self.conn.readline()       # Read response
    return buf.decode().strip()      # Return stripped response
```

### ESPHome Implementation
```cpp
// Clear any pending data first
while (uart_bus.available()) {
    uart_bus.read_byte(&dummy);
}

// Read two complete lines (echo + response)
// Line 1: Echo of command
// Line 2: Actual response
// Apply .strip() equivalent whitespace trimming
// Return response for processing
```

Both implementations:
- Clear input buffers before sending commands
- Send identical command bytes
- Read two lines (echo + response)
- Use the second line as the actual response
- Strip whitespace from responses
- Match exact strings (`*POW=ON#` / `*POW=OFF#`)

## Detailed Analysis

### Python Daemon Approach

**Pros:**
- Zero additional hardware cost
- Direct integration with Kodi screensaver via addon
- Self-contained solution on existing hardware
- Familiar Python environment for modifications
- Built-in screensaver timer functionality
- Works without Home Assistant

**Cons:**
- Requires host computer/RPi to be always running
- Manual Home Assistant integration needed (REST API calls)
- Limited monitoring and diagnostics capabilities
- Single point of failure (if Kodi system goes down)
- Manual updates and maintenance required
- No remote access without port forwarding

**Best for:**
- Kodi-only setups without Home Assistant
- Users who prefer software-only solutions
- Existing Kodi systems with available serial ports
- Budget-conscious installations
- Simple setups with basic on/off control needs

### ESPHome Approach

**Pros:**
- Dedicated hardware - higher reliability and uptime
- Native Home Assistant integration with auto-discovery
- Rich monitoring: communication errors, connectivity status, last response
- OTA firmware updates via ESPHome
- WiFi connectivity enables remote access and control
- Independent operation (doesn't depend on Kodi system being up)
- Modern IoT architecture with real-time status updates
- Custom command service for advanced projector features
- Visual status indicators (optional LED)
- Comprehensive error tracking and diagnostics

**Cons:**
- Requires additional hardware purchase (~$10-15)
- More complex initial setup and wiring
- Kodi integration requires Home Assistant automations
- Need to manage ESP32 firmware and WiFi connectivity
- Requires basic electronics knowledge for wiring

**Best for:**
- Home Assistant users seeking native integration
- Users wanting dedicated, reliable IoT devices
- Setups requiring high availability and monitoring
- Modern smart home integrations
- Remote monitoring and control capabilities
- Advanced users who want custom projector commands

## Migration Path

If you're currently using the Python daemon and want to migrate to ESPHome:

### Step 1: Prepare Hardware
1. Purchase ESP32 development board (~$5-10)
2. Purchase RS232-TTL converter module (~$3-5)
3. Set up wiring as described in [ESPHome_Setup.md](ESPHome_Setup.md)

### Step 2: Test ESPHome Setup
1. Deploy ESPHome configuration to ESP32
2. Verify projector communication works using logs
3. Test control from Home Assistant interface

### Step 3: Create Home Assistant Automations
Replace Kodi addon functionality with HA automations:

```yaml
# Replicate the screensaver timer functionality
automation:
  - alias: "Projector Auto-off after Kodi idle"
    trigger:
      - platform: state
        entity_id: media_player.kodi
        to: 'idle'
        for: "00:10:00"  # 10 minutes idle
    condition:
      - condition: state
        entity_id: binary_sensor.projector_power_state
        state: 'on'
    action:
      - service: switch.turn_off
        entity_id: switch.projector_power

  - alias: "Projector on when Kodi starts playing"
    trigger:
      - platform: state
        entity_id: media_player.kodi
        to: 'playing'
    condition:
      - condition: state
        entity_id: binary_sensor.projector_power_state
        state: 'off'
    action:
      - service: switch.turn_on
        entity_id: switch.projector_power
```

### Step 4: Disable Python Daemon
1. Stop and disable benqd service: `sudo systemctl stop benqd && sudo systemctl disable benqd`
2. Remove Kodi addon from Kodi addons directory
3. Disconnect old serial connection from host computer
4. Connect serial cable to ESP32 setup

## Enhanced Features in ESPHome Version

The ESPHome implementation includes several improvements over the Python version:

### Advanced Monitoring
- **Communication Error Counter**: Tracks failed communications
- **Connectivity Status**: Binary sensor showing if projector is responding
- **Last Response Display**: Shows raw projector responses for debugging
- **Connection Health**: Automatic detection of communication issues

### Extended Control Options
- **Manual Query Button**: Trigger immediate status check via Home Assistant
- **Custom Command Service**: Send arbitrary commands to projector
- **Status LED**: Optional visual indicator on ESP32 board

### Improved Reliability
- **Automatic Reconnection**: WiFi auto-reconnect on connection loss
- **Buffer Management**: Proper input buffer clearing like Python version
- **Timeout Handling**: Configurable timeouts for communication
- **OTA Updates**: Update firmware without physical access

## API Compatibility

### Python Daemon API
```bash
# Get status
curl http://localhost:8080/

# Turn on
curl -X POST -H "Content-Type: application/json" \
     -d '{"power_on": true}' http://localhost:8080/

# Turn off  
curl -X POST -H "Content-Type: application/json" \
     -d '{"power_on": false}' http://localhost:8080/

# Screensaver control (Kodi addon integration)
curl -X POST -H "Content-Type: application/json" \
     -d '{"screensaver_on": true}' http://localhost:8080/screensaver
```

### ESPHome Home Assistant Integration
```yaml
# Turn projector on/off
service: switch.turn_on
target:
  entity_id: switch.projector_power

service: switch.turn_off
target:
  entity_id: switch.projector_power

# Check power state
{{ states('binary_sensor.projector_power_state') }}

# Send custom command
service: esphome.esp32_projector_send_projector_command
data:
  command: "*pow=?#"

# Check communication health
{{ states('binary_sensor.projector_communication_ok') }}
{{ states('sensor.projector_communication_errors') }}
```

## Troubleshooting Comparison

### Python Daemon Debug
```bash
# Check service status
systemctl status benqd

# View logs
journalctl -u benqd -f

# Test API directly
curl http://localhost:8080/

# Check serial connection
sudo dmesg | grep ttyUSB
```

### ESPHome Debug
```bash
# View real-time logs with projector communication
esphome logs esp32-projector.yaml

# Check Home Assistant integration
# Go to Settings > Devices & Services > ESPHome

# Monitor UART traffic
# Logs show both TX and RX data automatically

# Check WiFi connectivity
# Built into ESPHome logging and HA diagnostics
```

## Performance Comparison

| Metric | Python Daemon | ESPHome |
|--------|---------------|---------|
| **Boot Time** | ~30-60s (depends on host) | ~10-20s (ESP32 only) |
| **Response Time** | 0.5-2s (via HTTP) | 0.1-0.5s (direct UART) |
| **Memory Usage** | ~20-50MB (Python + Flask) | ~100KB (ESP32 firmware) |
| **CPU Usage** | Variable (host dependent) | Minimal (dedicated MCU) |
| **Power Consumption** | 5-50W (host computer) | ~0.5W (ESP32 only) |
| **Network Dependencies** | Host network + port forwarding | Direct WiFi connection |
| **Reliability** | Depends on host stability | Very high (dedicated hardware) |

## Conclusion

The **ESPHome approach is strongly recommended for new installations**, especially if you already use Home Assistant. It provides:
- Superior reliability and monitoring
- Native smart home integration  
- Better power efficiency
- More advanced diagnostic capabilities
- Modern IoT architecture

The **Python daemon remains viable for:**
- Existing Kodi-only setups without Home Assistant
- Users who prefer software-only solutions
- Budget-conscious installations where hardware cost is a concern
- Simple setups that don't require advanced monitoring

Both approaches implement **identical BenQ communication protocols** and provide the same core projector control functionality. The choice depends on your specific requirements, existing infrastructure, and preference for hardware vs. software solutions.
