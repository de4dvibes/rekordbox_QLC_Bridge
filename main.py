import asyncio
from aalink import Link
from pythonosc import udp_client

# --- KONFIGURATION ---
OSC_IP = "127.0.0.1"  # Localhost (Dieser PC)
OSC_PORT = 7700  # Port, auf dem QLC+ / DMXControl lauscht
OSC_ADDRESS = "/beat"  # Der OSC-Befehl für den Beat


async def main():
    # 1. OSC Client initialisieren
    client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

    # 2. Ableton Link Session via aalink starten (Startwert 120 BPM)
    link = Link(120.0)
    link.enabled = True

    print("========================================")
    print(" 🚀 REKORDBOX -> OSC BRIDGE AKTIV ")
    print("========================================")
    print(f"Sende Trigger an Port {OSC_PORT} via {OSC_ADDRESS}")
    print("Abbruch mit STRG+C\n")

    try:
        while True:
            # aalink wartet hier asynchron genau bis zum nächsten ganzen Beat!
            # Die Zahl '1' bedeutet: Warte auf den nächsten 1/4-Takt (den Kick).
            await link.sync(1)

            # Beat ist da! Sende das OSC-Signal an das Lichtpult
            client.send_message(OSC_ADDRESS, 1.0)

            print(f"[SYNC] Beat Hit!")

    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    try:
        # Starte den asynchronen Loop
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBridge wurde manuell beendet.")