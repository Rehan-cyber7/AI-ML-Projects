"""
GUESS THE TIMER - A Python Game
================================
A fun party game where contestants try to guess how long
a hidden timer ran. Inspired by Scratch game logic!

Requirements : Python 3.x  (no external libraries required for basic play)
Optional     : pip install pygame   (for enhanced sound with custom WAV files)

Run          : python guess_the_timer.py
"""

import time
import random
import sys
import os

# ============================================================
# GAME CONFIGURATION — Tweak these to change difficulty / feel
# ============================================================
TIMER_MIN_SECONDS = 1.0      # Minimum hidden-timer duration (seconds)
TIMER_MAX_SECONDS = 10.0     # Maximum hidden-timer duration (seconds)
GUESS_TOLERANCE   = 0.5      # A guess within ±this many seconds is "correct"

# ============================================================
# SOUND FUNCTIONS
# ============================================================

def play_sound(sound_type="start"):
    """
    Play a system beep / sound to signal timer events.

    Strategy (tried in order):
      1. winsound.Beep()          — Windows built-in
      2. afplay / System sounds   — macOS built-in
      3. aplay / ALSA sounds      — Linux (common)
      4. Print a visual fallback   — Works everywhere

    -------------------------------------------------------
    To use custom WAV files with pygame instead, install it:
        pip install pygame
    Then replace the body of this function with:

        import pygame
        pygame.mixer.init()
        sounds = {
            "start": pygame.mixer.Sound("start.wav"),
            "stop" : pygame.mixer.Sound("stop.wav"),
            "win"  : pygame.mixer.Sound("win.wav"),
            "lose" : pygame.mixer.Sound("lose.wav"),
        }
        sounds[sound_type].play()
    -------------------------------------------------------
    """
    # --- Attempt 1: Windows winsound ----------------------------------
    try:
        if sys.platform == "win32":
            import winsound
            if sound_type == "start":
                winsound.Beep(800, 200)       # high short beep
            elif sound_type == "stop":
                winsound.Beep(400, 400)       # low longer beep
            elif sound_type == "win":
                winsound.Beep(523, 150)       # C5
                winsound.Beep(659, 150)       # E5
                winsound.Beep(784, 300)       # G5  → happy arpeggio
            elif sound_type == "lose":
                winsound.Beep(300, 300)
                winsound.Beep(200, 400)       # descending buzz
            return
    except Exception:
        pass

    # --- Attempt 2: macOS afplay --------------------------------------
    try:
        if sys.platform == "darwin":
            sound_map = {
                "start": "/System/Library/Sounds/Tink.aiff",
                "stop" : "/System/Library/Sounds/Basso.aiff",
                "win"  : "/System/Library/Sounds/Glass.aiff",
                "lose" : "/System/Library/Sounds/Buzz.aiff",
            }
            path = sound_map.get(sound_type)
            if path and os.path.exists(path):
                os.system(f'afplay "{path}" 2>/dev/null')
            return
    except Exception:
        pass

    # --- Attempt 3: Linux aplay ---------------------------------------
    try:
        if sys.platform.startswith("linux"):
            sound_map = {
                "start": "/usr/share/sounds/alsa/Front_Center.wav",
                "stop" : "/usr/share/sounds/alsa/Rear_Center.wav",
            }
            path = sound_map.get(sound_type)
            if path and os.path.exists(path):
                os.system(f'( aplay -q "{path}" 2>/dev/null ) &')
            return
    except Exception:
        pass

    # --- Fallback: visual-only indicator ------------------------------
    labels = {
        "start": "*BEEP*  — Timer Started!",
        "stop" : "*BEEP BEEP*  — Timer Stopped!",
        "win"  : "*FANFARE*  — Winner!",
        "lose" : "*BUZZER*  — Better luck next time!",
    }
    print(f"\n  [SOUND] {labels.get(sound_type, '')}")


# ============================================================
# DISPLAY / ANIMATION HELPERS
# ============================================================

def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    # FIX: Use sys.platform instead of os.platform
    os.system("cls" if sys.platform == "win32" else "clear")


def show_welcome():
    """Print the game title and rules."""
    clear_screen()
    print("=" * 58)
    print()
    print("          G U E S S   T H E   T I M E R")
    print()
    print("=" * 58)
    print()
    print("  HOW TO PLAY:")
    print("  ------------")
    print(f"  1. A hidden timer starts and stops automatically.")
    print(f"  2. You'll HEAR a sound when it starts and stops.")
    print(f"  3. The timer runs for {TIMER_MIN_SECONDS}-{TIMER_MAX_SECONDS} seconds.")
    print(f"  4. After it stops, each contestant guesses the duration.")
    print(f"  5. Guesses within +/-{GUESS_TOLERANCE}s of the real time WIN!")
    print()
    print("=" * 58)
    print()


def countdown():
    """Display a 3-2-1-GO countdown before the timer starts."""
    for word in ["3", "2", "1", "GO!"]:
        # \r returns cursor to start of line; end="" prevents newline
        print(f"\r    Get ready... {word} ", end="", flush=True)
        time.sleep(0.8)
    print("\r" + " " * 25 + "\r", end="", flush=True)  # wipe the line


def run_hidden_timer(duration):
    """
    Run the hidden timer for *duration* seconds.

    While running, a spinning animation is shown so the player
    knows something is happening — but the actual seconds are
    never revealed.

    Returns:
        float — the real elapsed time (rounded to 2 decimals),
                which may differ very slightly from *duration*
                due to OS scheduling.
    """
    # ---- Play START sound, THEN begin measuring time ----
    play_sound("start")
    start_time = time.time()

    # Spinning animation frames (Unicode braille dots)
    spinner  = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    # Simple fallback if the terminal can't render braille
    fallback = ["|", "/", "-", "\\"]

    frame_idx = 0
    print("  Timer RUNNING  ", end="", flush=True)

    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break
        # Pick a frame character
        try:
            ch = spinner[frame_idx % len(spinner)]
        except UnicodeEncodeError:
            ch = fallback[frame_idx % len(fallback)]
        print(f"\r  Timer RUNNING  {ch} ", end="", flush=True)
        frame_idx += 1
        time.sleep(0.07)                         # ~14 fps

    # Wipe the running line
    print("\r" + " " * 35 + "\r", end="", flush=True)

    actual_elapsed = round(time.time() - start_time, 2)

    # ---- Play STOP sound AFTER measurement ends ----
    play_sound("stop")

    return actual_elapsed


def show_win_animation(contestant_num):
    """
    Celebratory multi-frame text animation for a correct guess.
    Simulates a 'fireworks / trophy' reveal in the terminal.
    """
    play_sound("win")

    frames = [
        "         *          ",
        "      *  *  *       ",
        "    *  WINNER  *    ",
        "  *  *  *  *  *  *  ",
        "   ★  CONTESTANT {:>2} ★  ".format(contestant_num),
        "  *  *  *  *  *  *  ",
        "    *  GUESSED  *   ",
        "      *  IT  *      ",
        "      * !! *        ",
    ]

    print()
    for i, frame in enumerate(frames):
        # Each frame overwrites the previous (carriage-return trick)
        if i == 0:
            print(f"  Contestant {contestant_num}: {frame}")
        else:
            print(f"  {frame}")
        time.sleep(0.25)

    time.sleep(0.3)
    print()
    print(f"  {'#' * 5} Contestant {contestant_num} GUESSED CORRECTLY! {'#' * 5}")
    print()


def show_loss_animation(contestant_num, guess, actual, difference):
    """Display a loss indicator for an incorrect guess."""
    play_sound("lose")
    print()
    print(f"  X  Contestant {contestant_num}: WRONG!")
    print(f"     Guessed: {guess:.1f}s  |  Actual: {actual:.1f}s  |  Off by: {difference:.1f}s")
    print()


def show_results(actual_time, contestants):
    """
    Print a summary table of all contestants' results.

    Args:
        actual_time  (float): The real timer duration.
        contestants  (list) : List of dicts with keys
                              'number', 'guess', 'correct'.
    """
    print()
    print("=" * 58)
    print(f"  RESULTS  —  Actual Time: {actual_time:.1f} seconds")
    print("=" * 58)
    print()

    winners = [c for c in contestants if c["correct"]]
    losers  = [c for c in contestants if not c["correct"]]

    if winners:
        print("  WINNERS:")
        for w in winners:
            diff = abs(w["guess"] - actual_time)
            print(f"    Contestant {w['number']}: "
                  f"Guessed {w['guess']:.1f}s  (off by {diff:.1f}s)  OK")
        print()

    if losers:
        print("  BETTER LUCK NEXT TIME:")
        for lo in losers:
            diff = abs(lo["guess"] - actual_time)
            print(f"    Contestant {lo['number']}: "
                  f"Guessed {lo['guess']:.1f}s  (off by {diff:.1f}s)  X")
        print()

    if not winners:
        print("  No one guessed correctly this round!\n")

    print("=" * 58)


# ============================================================
# INPUT HELPERS (with error handling)
# ============================================================

def get_contestant_count():
    """Ask how many people are playing.  Accepts 1-10 only."""
    while True:
        try:
            raw = input("  Enter number of contestants (1-10): ").strip()
            count = int(raw)
            if 1 <= count <= 10:
                return count
            print("  Please enter a number between 1 and 10.")
        except ValueError:
            print("  Invalid input — please type a whole number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Game cancelled. Goodbye!")
            sys.exit(0)


def get_guess(contestant_num):
    """
    Ask one contestant for their time guess.
    Accepts any number from 0 to 15 (a little buffer above max).
    """
    while True:
        try:
            raw = input(
                f"  Contestant {contestant_num}, your guess (seconds): "
            ).strip()
            guess = float(raw)
            if 0 <= guess <= 15:
                return guess
            print("  Please enter a number between 0 and 15.")
        except ValueError:
            print("  Invalid input — please type a number (e.g. 3.5).")
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Game cancelled. Goodbye!")
            sys.exit(0)


def ask_play_again():
    """Return True if players want another round."""
    while True:
        try:
            choice = input("  Play again? (y/n): ").strip().lower()
            if choice in ("y", "yes"):
                return True
            if choice in ("n", "no"):
                return False
            print("  Please type 'y' or 'n'.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye!")
            sys.exit(0)


# ============================================================
# MAIN GAME LOOP
# ============================================================

def main():
    """Entry point — runs the complete game."""

    show_welcome()
    playing = True

    while playing:
        # ---- Step 1: How many players? --------------------------------
        num_contestants = get_contestant_count()
        print(f"\n  {num_contestants} contestant(s) ready!\n")
        input("  Press ENTER to start the timer... ")

        # ---- Step 2: Pick a random duration ----------------------------
        #   (The players never see this number!)
        secret_duration = round(
            random.uniform(TIMER_MIN_SECONDS, TIMER_MAX_SECONDS), 2
        )

        # ---- Step 3: Countdown ----------------------------------------
        print()
        countdown()

        # ---- Step 4: Run the hidden timer ------------------------------
        #   Returns the *real* measured elapsed time.
        actual_time = run_hidden_timer(secret_duration)

        # ---- Step 5: Timer stopped — collect guesses -------------------
        print("  TIMER STOPPED!\n")
        print(f"  How long did it run? "
              f"(Range {TIMER_MIN_SECONDS}-{TIMER_MAX_SECONDS}s, "
              f"tolerance +/-{GUESS_TOLERANCE}s)\n")

        contestants = []
        for i in range(1, num_contestants + 1):
            guess = get_guess(i)
            difference  = abs(guess - actual_time)
            is_correct  = difference <= GUESS_TOLERANCE
            contestants.append({
                "number":  i,
                "guess":   guess,
                "correct": is_correct,
            })

        # ---- Step 6: Dramatic reveal ----------------------------------
        print("\n  Revealing the actual time...")
        time.sleep(1.0)
        print(f"  The timer ran for: {actual_time:.1f} seconds!\n")
        time.sleep(0.5)

        # ---- Step 7: Individual win / loss animations ------------------
        print("-" * 58)
        for c in contestants:
            if c["correct"]:
                show_win_animation(c["number"])
            else:
                diff = abs(c["guess"] - actual_time)
                show_loss_animation(c["number"], c["guess"], actual_time, diff)

        # ---- Step 8: Summary table ------------------------------------
        show_results(actual_time, contestants)

        # ---- Step 9: Play again? --------------------------------------
        playing = ask_play_again()
        if playing:
            show_welcome()

    print("\n  Thanks for playing GUESS THE TIMER!  Bye!\n")


# ============================================================
if __name__ == "__main__":
    main()