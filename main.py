import asyncio
import sys
from aalink import Link
from pythonosc import udp_client

# --- KONFIGURATION ---
OSC_IP = "127.0.0.1"
OSC_PORT = 7700
OSC_ADDRESS = "/beat"


async def main():
    # OSC Client und Ableton Link initialisieren
    client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)
    link = Link(120.0)
    link.enabled = True

    # --- CLI HEADER (Statisch) ---
    sys.stdout.write("\033[2J\033[H")
    print("==================================================")
    print(" 🎛️  REKORDBOX -> OSC BRIDGE ")
    print("==================================================")
    print(f" 📡 Ziel-IP:   {OSC_IP}")
    print(f" 🔌 OSC-Port:  {OSC_PORT}")
    print(f" 🎯 Adresse:   {OSC_ADDRESS}")
    print("==================================================")
    print(" [STRG+C] drücken zum Beenden.\n")

    beat_counter = 0

    try:
        while True:
            # Warten auf den nächsten Kick-Drum (Ganzen Beat)
            await link.sync(1)

            # OSC-Signal feuern
            client.send_message(OSC_ADDRESS, 1.0)

            # --- DER FIX: aalink macht es viel simpler ---
            # Statt kompliziertem Session-State reicht hier einfach:
            bpm = link.tempo

            # Beat-Zähler (1, 2, 3, 4) rotieren lassen
            beat_counter = (beat_counter % 4) + 1

            # Dynamische Statuszeile überschreibt sich selbst
            status_line = f"\r \033[K▶ Aktuelle BPM: [ {bpm:>6.2f} ]  |  Takt: {beat_counter}/4  |  Status: SYNCED 🟢"

            sys.stdout.write(status_line)
            sys.stdout.flush()

    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n 🛑 Bridge wurde erfolgreich beendet.")