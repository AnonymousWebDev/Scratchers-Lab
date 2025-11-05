import rtmidi
from rtmidi.midiutil import open_midiinput
import pygame
from collections import deque

# MIDI mappings for RX2
JOGWHEEL_CC = 16
CROSSFADER_CC = 11

# State variables
crossfader_value = 0.0
jogwheel_position = 0.0
jogwheel_speed = 0.0

# Trail history
MAX_HISTORY = 800  # number of frames to show in the trail
history = deque(maxlen=MAX_HISTORY)

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
            jogwheel_position += delta * 5
            jogwheel_speed = delta
        # Crossfader movement
        elif data1 == CROSSFADER_CC:
            crossfader_value = data2 / 127.0

def main():
    list_midi_devices()
    port_index = int(input("Enter the port number of your XDJ-RX2: "))
    midi_in, port_name = open_midiinput(port_index)
    midi_in.set_callback(midi_callback)

    # Pygame setup
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("RX2 Scratch Trainer – Split Trails (Swapped)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)

    running = True
    scroll_speed = 5  # pixels per frame

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        # Record current state
        history.appendleft({
            "crossfader": crossfader_value,
            "jogwheel": jogwheel_position,
        })

        # Clear screen
        screen.fill((10, 10, 10))

        # --- Layout setup ---
        mid_x = WIDTH // 2
        left_area = (50, mid_x - 100)     # Crossfader area
        right_area = (mid_x + 100, WIDTH - 50)  # Jogwheel area
        base_y = HEIGHT - 50

        # --- Crossfader trail (LEFT) ---
        fader_points = []
        for i, frame in enumerate(history):
            y = base_y - i * scroll_speed
            if y < 0:
                break
            fade = max(30, 255 - i * (255 / MAX_HISTORY * 1.5))
            x_range = left_area[1] - left_area[0] - 100
            fader_x = int(left_area[0] + frame["crossfader"] * x_range)
            fader_points.append((fader_x, y))

        if len(fader_points) > 1:
            pygame.draw.lines(screen, (0, 150, 255), False, fader_points, 3)

        # --- Jogwheel trail (RIGHT) ---
        jog_points = []
        for i, frame in enumerate(history):
            y = base_y - i * scroll_speed
            if y < 0:
                break
            fade = max(30, 255 - i * (255 / MAX_HISTORY * 1.5))
            x_range = right_area[1] - right_area[0] - 200
            jog_x = int(right_area[0] + ((frame["jogwheel"] % x_range)))
            jog_points.append((jog_x, y))

        if len(jog_points) > 1:
            pygame.draw.lines(screen, (0, 255, 100), False, jog_points, 3)

        # --- UI labels & dividers ---
        pygame.draw.line(screen, (40, 40, 40), (mid_x, 0), (mid_x, HEIGHT), 2)
        label1 = font.render("Crossfader Trail", True, (0, 150, 255))
        label2 = font.render("Jogwheel Trail", True, (0, 255, 100))
        screen.blit(label1, (left_area[0], 20))
        screen.blit(label2, (right_area[0], 20))
        hint = font.render("ESC to quit", True, (180, 180, 180))
        screen.blit(hint, (WIDTH - 200, 20))

        # Update
        pygame.display.flip()
        clock.tick(60)

    midi_in.close_port()
    pygame.quit()

if __name__ == "__main__":
    main()
