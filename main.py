import rtmidi
from rtmidi.midiutil import open_midiinput
import pygame
import time

# MIDI mappings for your RX2
JOGWHEEL_CC = 16       # confirmed correct
CROSSFADER_CC = 11     # confirmed correct

# State variables
crossfader_value = 0.0   # 0.0 → 1.0
jogwheel_position = 0.0  # continuous scroll
jogwheel_speed = 0.0     # to animate smoothly

def list_midi_devices():
    midi_in = rtmidi.MidiIn()
    ports = midi_in.get_ports()
    print("Available MIDI input ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port}")

def midi_callback(event, data=None):
    global crossfader_value, jogwheel_position, jogwheel_speed
    message, delta_time = event
    status, data1, data2 = message

    if status & 0xF0 == 0xB0:
        # Jogwheel movement
        if data1 == JOGWHEEL_CC:
            delta = (data2 - 64) / 64.0
            jogwheel_position += delta * 5  # scale for visibility
            jogwheel_speed = delta
        # Crossfader movement
        elif data1 == CROSSFADER_CC:
            crossfader_value = data2 / 127.0

def main():
    # MIDI setup
    list_midi_devices()
    port_index = int(input("Enter the port number of your XDJ-RX2: "))
    midi_in, port_name = open_midiinput(port_index)
    midi_in.set_callback(midi_callback)

    # Pygame setup
    pygame.init()
    WIDTH, HEIGHT = 1000, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("RX2 Scratch Visualizer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)

    running = True
    while running:
        # Handle quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw background
        screen.fill((10, 10, 10))

        # --- Crossfader bar ---
        bar_width = 120
        fader_x = int(crossfader_value * (WIDTH - bar_width))
        pygame.draw.rect(screen, (0, 200, 255), (fader_x, HEIGHT - 100, bar_width, 40))
        fader_text = font.render(f"Crossfader: {crossfader_value:.2f}", True, (255, 255, 255))
        screen.blit(fader_text, (10, HEIGHT - 150))

        # --- Jogwheel line and dot ---
        center_y = HEIGHT // 2
        pygame.draw.line(screen, (60, 60, 60), (50, center_y), (WIDTH - 50, center_y), 2)

        # Wrap jogwheel position within screen bounds
        dot_x = int((jogwheel_position % (WIDTH - 100)) + 50)
        dot_color = (0, 255, 100) if abs(jogwheel_speed) > 0.1 else (120, 120, 120)
        pygame.draw.circle(screen, dot_color, (dot_x, center_y), 15)

        # Text feedback
        jog_text = font.render(f"Jogwheel pos: {jogwheel_position:.1f}", True, (255, 255, 255))
        screen.blit(jog_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    midi_in.close_port()
    pygame.quit()

if __name__ == "__main__":
    main()
