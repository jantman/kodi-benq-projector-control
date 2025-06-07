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
| **Scheduled Power-off** | ✅ Built-in timer | ✅ Via HA automations |
| **Kodi Integration** | ✅ Direct addon | ⚠️ Via HA automations |
| **WiFi Connectivity** | ❌ Depends on host system | ✅ Built-in |
| **Error Handling** | ⚠️ Basic logging | ✅ Comprehensive monitoring |
| **OTA Updates** | ❌ Manual | ✅ ESPHome OTA |
| **Dashboard Control** | ❌ API only | ✅ Home Assistant UI |
| **Cost** | ~$0 (software only) | ~$10-15 (ESP32 + converter) |

## Detailed Analysis

### Python Daemon Approach

**Pros:**
- Zero additional hardware cost
- Direct integration with Kodi screensaver
- Self-contained solution
- Familiar Python environment for modifications

**Cons:**
- Requires computer/RPi to be always running
- Manual Home Assistant integration needed
- Limited monitoring and diagnostics
- Single point of failure (if Kodi system goes down)
- Manual updates and maintenance

**Best for:**
- Kodi-only setups without Home Assistant
- Users who prefer software-only solutions
- Existing Kodi systems with spare USB/serial ports
- Budget-conscious installations

### ESPHome Approach

**Pros:**
- Dedicated hardware - more reliable
- Native Home Assistant integration
- Rich monitoring and diagnostics
- OTA updates
- WiFi connectivity enables remote access
- Can work independently of Kodi system
- Modern IoT architecture

**Cons:**
- Requires additional hardware purchase
- More complex initial setup
- Kodi integration requires Home Assistant automations
- Need to manage ESP32 firmware updates

**Best for:**
- Home Assistant users
- Users wanting dedicated IoT devices
- Setups requiring high reliability
- Modern smart home integrations
- Remote monitoring capabilities

## Migration Path

If you're currently using the Python daemon and want to migrate to ESPHome:

### Step 1: Prepare Hardware
1. Purchase ESP32 development board
2. Purchase RS232-TTL converter module
3. Set up wiring as described in [ESPHome_Setup.md](ESPHome_Setup.md)

### Step 2: Test ESPHome Setup
1. Deploy ESPHome configuration to ESP32
2. Verify projector communication works
3. Test control from Home Assistant

### Step 3: Create Home Assistant Automations
Replace Kodi addon functionality with HA automations:

```yaml
# Replace screensaver detection with media player state
automation:
  - alias: "Projector Auto-off"
    trigger:
      - platform: state
        entity_id: media_player.kodi
        to: 'paused'
        for: "00:05:00"  # 5 minutes
    action:
      - service: switch.turn_off
        entity_id: switch.projector_power
```

### Step 4: Disable Python Daemon
1. Stop and disable benqd service
2. Remove Kodi addon
3. Disconnect old serial connection

## Command Protocol Compatibility

Both approaches use identical BenQ RS232 commands:

| Command | Purpose | Response |
|---------|---------|----------|
| `\r*pow=?#\r` | Query power state | `*POW=ON#` or `*POW=OFF#` |
| `\r*pow=on#\r` | Turn projector on | `*POW=ON#` |
| `\r*pow=off#\r` | Turn projector off | `*POW=OFF#` |

This ensures 100% compatibility between both implementations.

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
```

### ESPHome Home Assistant Integration
```yaml
# In automations.yaml
- service: switch.turn_on
  entity_id: switch.projector_power

- service: switch.turn_off  
  entity_id: switch.projector_power

# Check state
{{ states('binary_sensor.projector_power_state') }}
```

## Troubleshooting Comparison

### Python Daemon Debug
```bash
# Check service status
systemctl status benqd

# View logs
journalctl -u benqd -f

# Test API
curl http://localhost:8080/
```

### ESPHome Debug
```bash
# View real-time logs
esphome logs esp32-projector.yaml

# Check Home Assistant integration
# Go to Settings > Devices & Services > ESPHome
```

## Conclusion

The **ESPHome approach is recommended for new installations**, especially if you already use Home Assistant. It provides better reliability, monitoring, and integration capabilities.

The **Python daemon remains suitable for Kodi-only setups** or users who prefer software-only solutions and don't want to invest in additional hardware.

Both approaches are actively maintained and provide the same core functionality for controlling BenQ projectors.
