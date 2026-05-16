#Adventure Game

import queue
import threading


def timed_input(prompt, timeout=10):
    """Collect user input with a timeout. Returns None if time expires."""
    result_queue = queue.Queue()

    def read_input():
        result_queue.put(input(prompt))

    input_thread = threading.Thread(target=read_input, daemon=True)
    input_thread.start()

    try:
        return result_queue.get(timeout=timeout)
    except queue.Empty:
        return None

# This function begins the game and asks the player to choose a path
def intro():
    print("Welcome to My Adventure Game!")
    play = input("Do you wish to play? (yes/no): ").strip().lower()
    if play == "no":
        print("Are you sure? (yes/no):")
        choice = input().strip().lower()
        if choice == "yes":
            print("Goodbye!")
        else:
            intro() 
        return
    if play == "yes":
        print( "Your adventure begins now!")
    print("You wake up in a dark forest. Your vision clears and you see two paths that lie ahead. \n . . .\n")
    print("Do you go left into the dark mist or right toward the sounds of a raging river?  \n. . .\n")
    choice = timed_input("Type 'mist' or 'river' (10 seconds):\n ", timeout=10)

    if choice is None:
        print("Time's up. You took too long to choose and the forest consumes you. Game over.")
        return

    choice = choice.strip().lower()

    # Route the player to the appropriate path
    if choice == "mist":
        mist_path()
    elif choice == 'river':
        river_path()
    else:
        print("You hesitate too long and a wolf finds you. Game over.")

# One of the game paths: fairy ring in the mist
def mist_path():
    print("You enter the icy mist and stumble into an open field. In the center is a glowing circle of mushrooms. You can feel your skin tingle with the magic \n")
    print("Do you step inside or walk around it and continue on?")
    choice = input("Type 'inside' or 'around':\n ").strip().lower()

    if choice == "inside":
        print("The mushrooms glow brighter and you vanish into another world.")
    if choice == "inside":
        fairy_ring()
    else:
        print("You walk for hours and get lost in the mist forever. Game over.")

# Another game path: cross a dangerous river
def river_path():
    print("The river is fast and deep. You can see the sharp rocks beneath the surface. In the distance, there’s an old bridge. Do you try to cross the bridge or swim across the river?")
    choice = input("Type 'bridge' or 'swim': \n").strip().lower()

    if choice == "bridge":
        print("You make it across and find a glowing treasure. You win!")
    else:
        print("You decide to swim in the river. Unfortunately, you are swept away by the current and drown. Game over.")

#Fairy ring path
def fairy_ring():
    print("You take a deep breath and step into the fairy ring. The world around you shimmers and shifts. You find yourself in a magical realm filled with vibrant colors and strange creatures. A fairy approaches you and offers you a choice: do you chose a golden key that can unlock any door, or a silver potion that grants you one wish?")
    choice = input("Type 'key' or 'potion':\n ").strip().lower()
    if choice == "key":
        print("You choose the golden key and it unlocks a door to a hidden treasure. You win!")
    elif choice == "potion":
        print("You choose the silver potion and it grants you a wish. You wish for endless adventure and live happily ever after. Congratulations! Time to start a new adventure!")
    else:
        print("You hesitate too long and the fairy disappears. Game over.")

# Start the game
intro()

