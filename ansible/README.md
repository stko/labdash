

# Setup

## Flashen
Raspian Image flashen (getestet mit Trixie) mit dem Raspberry Installer
  * OS: Trixie 64B Lite (No desktop)
  * hostname: rpi-z-labdash
  * kein WLAN
  * ssh enabled

## Ansible ausführen

## Developer Notes

https://www.raspberrypi.com/tutorials/host-a-hotel-wifi-hotspot/

sudo nmcli radio wifi on 

sudo nmcli radio wifi on

sudo nmcli device wifi hotspot ssid LabDash password labdashlabdash ifname wlan0



manuelles Gebastel (von Gemini)

1. Neue Verbindung erstellen

    nmcli con add type wifi ifname wlan0 con-name Hotspot autoconnect yes ssid Hotspot

 2. Hotspot-Modus und IP-Sharing aktivieren

    nmcli con modify Hotspot 802-11-wireless.mode ap ipv4.method shared

3. Sicherheitseinstellungen (WPA2)

   nmcli con modify Hotspot wifi-sec.key-mgmt wpa-psk wifi-sec.psk "MeinSuperPasswort123"

4. Verbindung aktivieren

   nmcli con up Hotspot

HS_ID=$(nmcli connection | grep Hotspot | sed -r "s/\s+/\t/g" | cut -f 2 -s)

sudo nmcli connection modify $HS_ID connection.autoconnect yes connection.autoconnect-priority 100