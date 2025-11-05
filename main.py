import rtmidi
from rtmidi.midiutil import open_midiinput

# Correct MIDI CC mappings for your RX2
JOGWHEEL_CC = 16        # Jogwheel (deck)
CROSSFADER_CC = 11      # Crossfader

# Keep track of jogwheel position
jogwheel_position = 0.0

def list_midi_devices():
    midi_in = rtmidi.MidiIn()
    ports = midi_in.get_ports()
    print("Available MIDI input ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port}")

def midi_callback(event, data=None):
    global jogwheel_position
    message, delta_time = event
    status, data1, data2 = message

    # Only handle Control Change messages
    if status & 0xF0 == 0xB0:
        if data1 == JOGWHEEL_CC:
            # Jogwheel rotation: 64 = neutral, <64 backward, >64 forward
            delta = (data2 - 64) / 64.0
            jogwheel_position += delta
            print(f"🎧 Jogwheel delta: {delta:+.2f} | Position: {jogwheel_position:.2f}")

        elif data1 == CROSSFADER_CC:
            # Crossfader: 0–127 → 0.0–1.0
            fader = data2 / 127.0
            print(f"🎚️  Crossfader: {fader:.2f}")

def main():
    list_midi_devices()
    port_index = int(input("Enter the port number of your XDJ-RX2: "))
    midi_in, port_name = open_midiinput(port_index)
    print(f"Listening on {port_name}... Press Ctrl+C to exit.\n")

    midi_in.set_callback(midi_callback)

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        midi_in.close_port()

if __name__ == "__main__":
    main()
