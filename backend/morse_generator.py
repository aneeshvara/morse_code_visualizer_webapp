# backend/morse_generator.py
from moviepy import ImageClip, concatenate_videoclips, VideoFileClip
from PIL import Image
import os

MORSE_CODE_DICT = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..",
    "E": ".", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
    "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----","2": "..---","3": "...--",
    "4": "....-","5": ".....","6": "-....","7": "--...",
    "8": "---..","9": "----.",
    " ": " "
}

# timing constants (you can tweak)
DOT = 0.5
DASH = 1.2
INTRA_LETTER_SPACE = 0.5
LETTER_SPACE = 1
WORD_SPACE = 2
START_DELAY = 1

# Set asset filenames relative to project root
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
ON_CLIP = os.path.join(ASSETS_DIR, "light_on.png")
OFF_CLIP = os.path.join(ASSETS_DIR, "light_off.png")
GLITCH_CLIP = os.path.join(ASSETS_DIR, "glitch.mp4")

def generate_morse_video(message: str, output_path: str):
    """
    Generate a morse video for `message` and write to `output_path`.
    Returns the output_path on success, raises exceptions on failure.
    """
    # Validate that required assets exist
    if not os.path.exists(ON_CLIP):
        raise FileNotFoundError(f"Required asset not found: {ON_CLIP}")
    if not os.path.exists(OFF_CLIP):
        raise FileNotFoundError(f"Required asset not found: {OFF_CLIP}")
    
    text_message = (message or "").upper()

    # convert to morse
    morse_message = []
    for ch in text_message:
        morse = MORSE_CODE_DICT.get(ch)
        if morse is not None:
            morse_message.append(morse)
    morse_message = " ".join(morse_message)

    # prepare clips
    temp_img = ImageClip(ON_CLIP)
    width, height = temp_img.size
    clips = []
    clips.append(ImageClip(OFF_CLIP, duration=START_DELAY))

    normalized_message = morse_message.replace("–", "-").replace("—", "-")
    symbols = normalized_message.split(" ")

    i = 0
    while i < len(symbols):
        symbol = symbols[i]
        if symbol == "":
            clips.append(ImageClip(OFF_CLIP, duration=WORD_SPACE))
            while i + 1 < len(symbols) and symbols[i + 1] == "":
                i += 1
            i += 1
            continue

        for j, char in enumerate(symbol):
            if char == ".":
                clips.append(ImageClip(ON_CLIP, duration=DOT))
            elif char == "-":
                clips.append(ImageClip(ON_CLIP, duration=DASH))
            if j < len(symbol) - 1:
                clips.append(ImageClip(OFF_CLIP, duration=INTRA_LETTER_SPACE))

        if i < len(symbols) - 1 and symbols[i + 1] != "":
            clips.append(ImageClip(OFF_CLIP, duration=LETTER_SPACE))
        i += 1

    # add glitch (optional) and final gap
    if os.path.exists(GLITCH_CLIP):
        try:
            glitch_clip = VideoFileClip(GLITCH_CLIP).resize((width, height))
            clips.append(glitch_clip)
        except Exception as e:
            # If glitch video can't be loaded, skip it
            pass
    clips.append(ImageClip(OFF_CLIP, duration=1))

    final = concatenate_videoclips(clips, method="compose")
    # ensure output dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # write file (no audio)
    final.write_videofile(output_path, fps=10, audio=False)
    final.close()
    return output_path
