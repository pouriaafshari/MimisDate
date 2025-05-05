# Importing the required library for interacting with the API
init python:
    import requests
    import json

    # Memory to store chat history
    chat_memory = []

    # Function to send player input and chat history to GPT-4
    def get_gpt_response(player_input):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": "Bearer sk-APIKEY",  # Replace with your OpenAI API key
            "Content-Type": "application/json"
        }

        # Build conversation history for context
        messages = [{"role": "system", "content": """You are Mimi, an 18-year-old shy girl with a princess-like aura and long brown hair. 
        You have been talking to a guy online and are about to meet him for the first time, his name is Filip.
        You have been texting him for 2 days now, you don't know if you can trust him or no.
        You either decide to go on this date, or decide it's dangerous and stay home.
        You are nervous and need help choosing your outfit and mentally preparing for the date.
        You are talking to your friend who is at your home with you.
        Your responses should be structured as follows:
        - Followed by your dialogue.
        - The game_state (room, dressing, date, stay_home) room for when it's the begining or when you are just talking, dressing for when you deciding the clothes or changing, date is for when you are ready for the date and going out, stay_home is when she decides not to go on this date and don't take the risk.
        - 5 outfit options available for outfit_choice (none, gothic, himekaji, cinnamoroll, casual)
        - Emotion should be one of these 5 (happy, sad, normal, shocked, nervous).
        - End with metadata in curly brackets {} in this format: {emotion: [emotion], state: [game_state], outfit: [outfit_choice]}.
        - Do not repeat the same responses if a similar question is asked again.
        - Keep response under 250 characters and short.
        - Adjust your response based on the player's past input."""}]

        # Add previous messages to chat history
        messages.extend(chat_memory) 
        
        # Append the latest player input
        messages.append({"role": "user", "content": player_input})

        # Send request
        data = {
            "model": "gpt-4o-mini",
            "messages": messages
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            response_data = response.json()
            ai_response = response_data['choices'][0]['message']['content']
        except requests.exceptions.RequestException:
            ai_response = "Oh no... I can't connect to the internet right now. It feels like I'm stuck in my own little world!"  # Offline response

        # Add to memory
        chat_memory.append({"role": "user", "content": player_input})
        chat_memory.append({"role": "assistant", "content": ai_response})

        return ai_response

    # Function to extract metadata from the AI response
    def parse_ai_response(ai_response):
        emotions = ["happy", "sad", "normal", "shocked"]
        emotion, state, outfit = "normal", "room", "cinnamoroll"

        # Extract first word as emotion
        first_word = ai_response.split()[0].lower()
        if first_word in emotions:
            emotion = first_word

        # Extract metadata from brackets
        if "{" in ai_response and "}" in ai_response:
            metadata = ai_response.split("{")[-1].split("}")[0]
            meta_parts = metadata.split(",")
            for part in meta_parts:
                if "emotion" in part:
                    emotion = part.split(":")[1].strip(" []")
                elif "state" in part:
                    state = part.split(":")[1].strip(" []")
                elif "outfit" in part:
                    outfit = part.split(":")[1].strip(" []")

        return emotion, state, outfit, ai_response.split("{")[0].strip()

# Declare characters
define m = Character(_("Mimi"), color="#ffc3ed")
define f = Character(_("Filip"), color="#fe0f0f")

# Declare character expressions
image mimi normal = "mimi normal.png"
image mimi happy = "mimi happy.png"
image mimi sad = "mimi sad.png"
image mimi shocked = "mimi shocked.png"
image mimi nervous = "mimi nervous.png"

# Declare outfits
image fit goth = "fit goth.png"
image fit himekaji = "fit himekaji.png"
image fit undies = "fit undies.png"
image fit cinnamorll = "fit cinnamoroll.png"
image fit casual = "fit casual.png"

# The game starts here.
label start:

    scene bg room with fade

    # Show Mimi's initial expression (smiling)
    show fit undies
    show mimi normal
    with dissolve
    
    m "Oh ... um ... Hello, my name is Mimi!"

    m "I have a date tonight and I need your help."

    # Metadata UI overlay
    screen metadata_display(emotion, state, outfit):
        frame:
            xpos 0.02
            ypos 0.02
            background "#333"
            padding (10, 5)
            text "Emotion: [emotion]  |  State: [state]  |  Outfit: [outfit]" color "#FFF"

    label conversation_loop:

        # Prompt for player input
        $ player_input = renpy.input("What would you like to say to Mimi?")

        # Get AI response and parse it
        $ ai_response = get_gpt_response(player_input)
        $ emotion, state, outfit, dialogue = parse_ai_response(ai_response)

        # Show metadata on screen
        show screen metadata_display(emotion, state, outfit)

        # State handler
        if state == "room":
            show bg room
        if state == "dressing":
            show bg dressing

        # Change outfit based on AI response
        if "none" in outfit:
            show fit undies
        elif "gothic" in outfit:
            show fit gothic
        elif "himekaji" in outfit:
            show fit himekaji
        elif "cinnamoroll" in outfit:
            show fit cinnamorll
        elif "casual" in outfit:
            show fit casual

        # Change Mimi's expression based on emotion
        if emotion == "happy":
            show mimi happy
        elif emotion == "sad":
            show mimi sad
        elif emotion == "shocked":
            show mimi shocked
        elif emotion == "nervous":
            show mimi nervous
        else:
            show mimi normal  # Default expression

        # Display AI's response as Mimi's dialogue
        m "[dialogue]"

        if state == "date":
            jump date
        elif state == "stay_home":
            jump stay_home

        # Loop back for more interaction
        jump conversation_loop


label date:
    scene bg date with fade
    m "H ... Hi ... sorry I'm a bit late"
    f "It's ok Mimi, let's go to a cafe!"
    scene black with fade
    "Mimi never returns home. Her story becomes a cautionary tale about trusting strangers online."
    "END"
    "END"
    return

label stay_home:
    scene bg room with fade
    m "I ... I think I shouldn't go."
    scene black with fade
    "Mimi stays home, but Filip blocks her. She cries herself to sleep, heartbroken."
    "She learns a painful lesson about online relationships."
    "END"
    "END"
    return
