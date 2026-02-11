nmcli radio wifi on
sleep 2
nmcli device wifi hotspot ssid LabDash password labdashlabdash ifname wlan0
sleep 2
nmcli connection modify Hotspot connection.autoconnect yes connection.autoconnect-priority 100
