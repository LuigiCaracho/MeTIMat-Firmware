import logging
import os
import socket
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Network settings
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Sound settings
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_PATH = os.path.join(SCRIPT_DIR, "assets/sounds/beep.mp3")


def play_beep():
    """Plays the sound using ffplay."""
    if not os.path.exists(SOUND_PATH):
        logging.error(f"Sound file not found: {SOUND_PATH}")
        return

    try:
        logging.info("🔊 Playing beep...")
        logging.info(" ".join(["ffplay", "-nodisp", "-autoexit", SOUND_PATH]))
        # -nodisp: no video, -autoexit: exit when done, -loglevel quiet: no logs
        subprocess.Popen(["ffplay", "-nodisp", "-autoexit", SOUND_PATH])
    except Exception as e:
        logging.error(f"Failed to play sound: {e}")


def main():
    # Start a persistent silent stream to keep Bluetooth speakers awake
    logging.info("🔇 Starting silent background stream to keep speaker active...")
    silence_proc = subprocess.Popen(
        ["ffplay", "-f", "lavfi", "-i", "anullsrc", "-nodisp", "-loglevel", "quiet"]
    )

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    logging.info(f"👂 Beep listener started on {UDP_IP}:{UDP_PORT}")
    logging.info(f"📂 Sound path: {SOUND_PATH}")

    try:
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            message = data.decode("utf-8").strip()

            if message == "BEEP":
                play_beep()
            else:
                logging.warning(f"Received unknown message: {message}")
    except KeyboardInterrupt:
        logging.info("Stopping beep listener...")
    finally:
        sock.close()
        silence_proc.terminate()


if __name__ == "__main__":
    main()
