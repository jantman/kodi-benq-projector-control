#!/bin/bash
# BenQ Projector ESPHome Test Script
# This script helps test and validate your ESPHome projector control setup

set -e

ESP32_IP="${1:-esp32-projector.local}"
HA_URL="${2:-http://homeassistant.local:8123}"
HA_TOKEN="${3}"

echo "=== BenQ Projector ESPHome Test Script ==="
echo "ESP32 IP/Hostname: $ESP32_IP"
echo "Home Assistant URL: $HA_URL"
echo

# Test 1: Ping ESP32
echo "1. Testing ESP32 connectivity..."
if ping -c 1 "$ESP32_IP" >/dev/null 2>&1; then
    echo "   ✅ ESP32 is reachable at $ESP32_IP"
else
    echo "   ❌ ESP32 is not reachable at $ESP32_IP"
    echo "   Please check:"
    echo "   - ESP32 is powered on and connected to WiFi"
    echo "   - IP address/hostname is correct"
    echo "   - WiFi network connectivity"
    exit 1
fi

# Test 2: Check if ESPHome API is responding
echo
echo "2. Testing ESPHome API..."
if timeout 5 nc -z "$ESP32_IP" 6053 2>/dev/null; then
    echo "   ✅ ESPHome API port (6053) is open"
else
    echo "   ❌ ESPHome API port (6053) is not accessible"
    echo "   Please check ESPHome configuration and firewall settings"
fi

# Test 3: Check Home Assistant integration (if HA token provided)
if [ -n "$HA_TOKEN" ]; then
    echo
    echo "3. Testing Home Assistant integration..."
    
    # Check if projector entities exist in HA
    ENTITIES_RESPONSE=$(curl -s -H "Authorization: Bearer $HA_TOKEN" \
        -H "Content-Type: application/json" \
        "$HA_URL/api/states" | grep -o '"entity_id":"[^"]*projector[^"]*"' || true)
    
    if [ -n "$ENTITIES_RESPONSE" ]; then
        echo "   ✅ Projector entities found in Home Assistant:"
        echo "$ENTITIES_RESPONSE" | sed 's/.*"entity_id":"\([^"]*\)".*/     - \1/'
    else
        echo "   ❌ No projector entities found in Home Assistant"
        echo "   Please check:"
        echo "   - ESPHome integration is installed and configured"
        echo "   - ESP32 is discovered in HA (Settings > Devices & Services)"
        echo "   - API encryption key matches between ESP32 and HA"
    fi
else
    echo
    echo "3. Skipping Home Assistant test (no token provided)"
    echo "   To test HA integration, run:"
    echo "   $0 $ESP32_IP $HA_URL YOUR_HA_LONG_LIVED_TOKEN"
fi

# Test 4: Serial connection guidance
echo
echo "4. Serial Connection Checklist:"
echo "   📋 Hardware connections:"
echo "   - ESP32 GPIO17 (TX) → RS232 Module TX"
echo "   - ESP32 GPIO16 (RX) → RS232 Module RX"
echo "   - ESP32 3.3V → RS232 Module VCC"
echo "   - ESP32 GND → RS232 Module GND"
echo "   - RS232 Module → Projector RS232 port"
echo
echo "   📋 Projector settings:"
echo "   - Projector RS232 control must be enabled"
echo "   - Baud rate should be 115200"
echo "   - Some projectors require 'Service Mode' for RS232 control"

# Test 5: Provide ESPHome logs command
echo
echo "5. For real-time debugging, run:"
echo "   esphome logs esp32-projector.yaml --device $ESP32_IP"
echo
echo "6. To manually test projector commands via Home Assistant:"
echo "   - Go to Developer Tools > Services"
echo "   - Call service: ESPHome: esp32_projector_send_projector_command"
echo "   - Use command: *pow=?# (to query power state)"

echo
echo "=== Test Complete ==="
