# ==========================================
# TO RUN THIS CODE, INSTALL THESE LIBRARIES:
# Open your terminal or command prompt and run:
# pip install requests Pillow pygame
# ==========================================

# --- BUILT-IN MODULES (Come pre-packaged with Python) ---
import tkinter as tk  # The core toolkit used to build the desktop window (GUI)
from tkinter import messagebox  # A specific tool from tkinter to show pop-up error boxes
from io import BytesIO  # Tricks Python into treating raw memory (bytes) like a physical file
import tempfile  # Silently creates temporary files on the hard drive
import os  # Allows Python to interact with the computer's operating system

# --- EXTERNAL LIBRARIES (Require pip install) ---
import requests  # Our messenger to send requests to the web (PokéAPI)
from PIL import Image, ImageTk  # Pillow library: used to open, resize, and display images
import pygame  # A gaming library we are using specifically for its audio engine

# Initialize the audio player engine within pygame so it's ready to play sounds
pygame.mixer.init()

# Create a global variable to track where the current audio file is saved on the computer.
# It starts as 'None' because we haven't searched for a Pokémon yet.
current_cry_path = None


def play_audio():
    # Check if we have a saved audio path AND that the file actually exists on the computer
    if current_cry_path and os.path.exists(current_cry_path):
        # Load the audio file into the pygame mixer
        pygame.mixer.music.load(current_cry_path)
        # Play the loaded audio file
        pygame.mixer.music.play()


def search_pokemon():
    # Tell the function to use the global variable we defined at the top
    global current_cry_path

    # Grab the text from the search bar, remove extra spaces (.strip()), and make it lowercase
    # (The API only accepts lowercase names)
    query = search_entry.get().strip().lower()

    # If the user hit search while the box was empty, just stop and do nothing
    if not query:
        return

    # Construct the exact web address for the requested Pokémon
    url = f"https://pokeapi.co/api/v2/pokemon/{query}"

    # Send a GET request to the URL and store the API's reply in 'response'
    response = requests.get(url)

    # Check if the API found the Pokémon (Status code 200 means "OK / Success")
    if response.status_code == 200:
        # Convert the raw JSON text from the API into a usable Python dictionary
        data = response.json()

        # Extract the name and capitalize the first letter
        name = data['name'].capitalize()
        # Extract the Pokédex ID number
        dex_number = data['id']

        # Loop through the 'types' list, grab the name of each type, capitalize it, and make a new list
        types = [t['type']['name'].capitalize() for t in data['types']]
        # Join the types together with a slash (e.g., "Fire / Flying")
        type_string = " / ".join(types)

        # Loop through the 'abilities' list, grab the name, capitalize it, and make a new list
        abilities = [a['ability']['name'].capitalize() for a in data['abilities']]
        # Join the abilities together with a comma (e.g., "Blaze, Solar-power")
        abilities_string = ", ".join(abilities)

        # Create a clean dictionary of just the stats (e.g., {'hp': 78, 'attack': 84})
        stats = {item['stat']['name']: item['base_stat'] for item in data['stats']}

        # Format all the extracted data into a single, multi-line string for our screen
        info_text = (
            f"{name} (#{dex_number:03d})\n"  # :03d forces the number to have 3 digits (e.g., #006)
            f"Type: {type_string}\n"
            f"Abilities: {abilities_string}\n"
            f"-------------------\n"
            f"HP: {stats.get('hp')} | Speed: {stats.get('speed')}\n"
            f"Atk: {stats.get('attack')} | Def: {stats.get('defense')}"
        )

        # Update the text label on our screen with the new string
        info_label.config(text=info_text)

        # Drill down into the JSON dictionary to find the URL for the high-res artwork
        img_url = data['sprites']['other']['official-artwork']['front_default']

        if img_url:
            # Download the raw image bytes from the URL
            img_response = requests.get(img_url)
            # Use BytesIO to trick Pillow into opening the raw memory bytes as an image
            img_data = Image.open(BytesIO(img_response.content))
            # Resize the image to 300x300 pixels, using LANCZOS to keep it high-quality
            img_data = img_data.resize((300, 300), Image.Resampling.LANCZOS)

            # Convert the Pillow image into a format tkinter can actually display
            photo = ImageTk.PhotoImage(img_data)
            # Update the image label on the screen with the new picture
            image_label.config(image=photo)
            # Keep a reference to the image in memory so Python's "garbage collector" doesn't delete it
            image_label.image = photo

        # Drill down into the JSON dictionary to find the audio cries
        cries = data.get('cries', {})
        # Try to get the classic legacy cry first; if it's missing, get the modern one
        cry_url = cries.get('legacy') or cries.get('latest')

        if cry_url:
            # Download the raw audio bytes from the URL
            cry_response = requests.get(cry_url)
            # Create a temporary file on the hard drive ending in .ogg
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
            # Write the downloaded audio bytes into that temporary file
            temp_audio.write(cry_response.content)
            # Close the file so the OS can use it
            temp_audio.close()

            # Save the file path to our global variable so the play_audio function can find it
            current_cry_path = temp_audio.name

            # Turn the Play Audio button on (make it clickable)
            cry_button.config(state=tk.NORMAL)
        else:
            # If no audio was found, turn the button off (gray it out)
            cry_button.config(state=tk.DISABLED)

    else:
        # If the status code wasn't 200 (e.g., 404 Not Found), show an error pop-up
        messagebox.showerror("Error", f"Could not find '{query}'. Check spelling!")


# ==========================================
# --- BUILD THE THEMED DESKTOP WINDOW ---
# ==========================================

# Create the main application window
root = tk.Tk()
root.title("Python Pokédex")  # Set the window title
root.geometry("500x820")  # Set the window size (width x height)
root.configure(bg="#CC0000")  # Set the background color to Pokédex Red

# --- Top Decorative Lights ---
# Create a canvas area at the top to draw our decorative circles
lights_canvas = tk.Canvas(root, bg="#CC0000", height=80, highlightthickness=0)
lights_canvas.pack(fill=tk.X, padx=10, pady=5)  # Place the canvas at the top of the window

# Draw the big blue lens and the three small colored lights
lights_canvas.create_oval(15, 10, 75, 70, fill="#23AEE1", outline="white", width=4)
lights_canvas.create_oval(95, 15, 115, 35, fill="#8B0000", outline="#4A0000", width=2)
lights_canvas.create_oval(125, 15, 145, 35, fill="#F2EE5E", outline="#A8A41E", width=2)
lights_canvas.create_oval(155, 15, 175, 35, fill="#42B05C", outline="#1F6932", width=2)

# --- The "Screen" Bezel ---
# Create a dark grey frame to act as the plastic border around the screen
screen_bezel = tk.Frame(root, bg="#222222", bd=10, relief=tk.RAISED)
screen_bezel.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)

# --- The Actual Screen ---
# Create the light blue interior screen inside the bezel
screen_bg = tk.Frame(screen_bezel, bg="#F0F8FF")
screen_bg.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Create an empty label on the screen where our Pokémon image will go
image_label = tk.Label(screen_bg, bg="#F0F8FF")
image_label.pack(pady=10)

# Create the Audio Play Button, set it to DISABLED initially, and link it to our play_audio function
cry_button = tk.Button(screen_bg, text="🔊 PLAY CRY", font=("Courier", 12, "bold"), bg="#a9a9a9", state=tk.DISABLED,
                       command=play_audio)
cry_button.pack(pady=5)

# Create the text area that will show stats. 'wraplength' ensures long text wraps to the next line
info_label = tk.Label(screen_bg, text="Enter a Pokémon to begin!", font=("Courier", 14, "bold"), bg="#F0F8FF",
                      fg="#333333", justify=tk.CENTER, wraplength=380)
info_label.pack(pady=10)

# --- Search Bar Area ---
# Create a container frame at the bottom for the search box and button
search_frame = tk.Frame(root, bg="#CC0000")
search_frame.pack(pady=20)

# Create the text input box where the user types the name
search_entry = tk.Entry(search_frame, font=("Courier", 16), width=15, justify=tk.CENTER)
search_entry.pack(side=tk.LEFT, padx=10)

# Create the search button and link it to our search_pokemon function
search_button = tk.Button(search_frame, text="SEARCH", font=("Courier", 14, "bold"), bg="#F2EE5E", fg="black",
                          relief=tk.RAISED, bd=4, command=search_pokemon)
search_button.pack(side=tk.LEFT)

# Start the infinite loop that keeps the window open and listening for clicks
root.mainloop()