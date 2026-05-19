import sys
import time
from scapy.all import sniff, UDP
from pythonosc import udp_client

# --- KONFIGURATION ---
OSC_IP = "127.0.0.1"
OSC_PORT = 7700
OSC_ADDRESS = "/beat"

# Pioneer nutzt für Pro DJ Link meistens die Ports 50000 bis 50002
PIONEER_PORT = 50001

client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)
last_beat_time = time.time()
current_bpm = 120.0

sys.stdout.write("\033[2J\033[H")
print("==================================================")
print(" 📡 REKORDBOX NETZWERK-SNIFFER (NO-SYNC BYPASS) ")
print("==================================================")
print(" [OK] Lausche lautlos auf Rekordbox-Netzwerkdaten...")
print("==================================================\n")


def packet_callback(packet):
    global last_beat_time, current_bpm

    if packet.haslayer(UDP) and packet[UDP].dport == PIONEER_PORT:
        raw_data = bytes(packet[UDP].payload)

        # Pioneer-Pakete haben oft den Header 'DsClsd' oder 'PIONEER'
        if b'PIONEER' in raw_data or len(raw_data) > 40:
            try:
                # Hier fischen wir die rohe BPM aus dem Pioneer-Byte-Stream.
                # Bei Pro DJ Link liegt die Master-BPM meistens als 32-Bit Integer
                # an einer festen Position im Paket (z.B. Byte 44-48).
                # Zur Veranschaulichung extrahieren wir hier den Wert:
                raw_bpm = int.from_bytes(raw_data[44:48], byteorder='big')

                # Pioneer speichert z.B. 128 BPM als 12800
                if 5000 < raw_bpm < 30000:
                    current_bpm = raw_bpm / 100.0

                # Beat-Trigger Berechnung basierend auf der extrahierten BPM
                now = time.time()
                beat_interval = 60.0 / current_bpm

                if now - last_beat_time >= beat_interval:
                    client.send_message(OSC_ADDRESS, 1.0)
                    last_beat_time = now

                    status = f"\r \033[K▶ NETZWERK-BPM: [ {current_bpm:.2f} ] | Status: LIVE TRACKING 🟢"
                    sys.stdout.write(status)
                    sys.stdout.flush()

            except Exception:
                pass


# Startet den Sniffer im Hintergrund auf allen Netzwerkkarte
sniff(filter=f"udp port {PIONEER_PORT}", prn=packet_callback, store=0)