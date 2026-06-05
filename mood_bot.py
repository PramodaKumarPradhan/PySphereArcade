import random
import time

class MoodBot:
    def __init__(self):
        # Keeps track of sentences we've already used to avoid repetition
        self.used_sentences = set()
        # The internal environmental metric (0 to 100)
        self.metric = random.randint(40, 60)
        # Previous mood to detect mood swings
        self.previous_mood = None

    def update_metric(self):
        """Simulates environmental changes over time and interactions."""
        # Random walk for the metric to give an evolving emotional state feeling
        change = random.randint(-18, 18)
        self.metric = max(0, min(100, self.metric + change))

    def get_mood(self):
        """Quantifies the current environment into a specific mood."""
        if self.metric <= 20:
            return "lethargic"
        elif self.metric <= 40:
            return "chill"
        elif self.metric <= 60:
            return "balanced"
        elif self.metric <= 80:
            return "energized"
        else:
            return "chaotic"

    def get_responses(self, mood):
        """Returns a list of possible responses for a given mood."""
        responses = {
            "lethargic": [
                "I feel like a deflated balloon today. The ambient energy is critically low at {metric}.",
                "Everything just feels so heavy. My sensors indicate the atmospheric pressure metric is at {metric}.",
                "Can programs sleep? Because I would really like to right now. The vibe level is a mere {metric}.",
                "Sigh. Moving pixels takes so much effort when the environment is dragging to {metric}.",
                "I'm operating at absolute minimum capacity right now. It’s too sluggish around here ({metric}).",
                "Is the server running out of coal? Because my internal temperature is at a freezing {metric}."
            ],
            "chill": [
                "Things are pretty mellow right now. A nice steady {metric} on the vibeometer.",
                "I'm just watching the background processes float by. Quite relaxing. Ambient metric at {metric}.",
                "No rush, no panic. Just existing securely in a cool {metric} state.",
                "If I had a digital coffee, I'd just sit and sip it. The atmosphere is comfortably cruising at {metric}.",
                "Very Zen vibes right now. My readings are hovering around a peaceful {metric}.",
                "Take a deep breath. That's what I'd do if I had lungs. We're at a manageable {metric}."
            ],
            "balanced": [
                "All systems nominal. The environment is perfectly average at {metric}.",
                "I'm feeling quite pragmatic today. The atmospheric metric is a solid {metric}.",
                "Observations indicate a steady state. I am neither ecstatic nor depressed, just a neat {metric}.",
                "My internal scales are perfectly balanced today. The ambient data energy reads {metric}.",
                "Processing reality... Everything is adequate. The current excitement level is {metric}.",
                "Just another day in the mainframe. Everything is sitting right at the {metric} mark."
            ],
            "energized": [
                "Wow, my circuits are absolutely buzzing! The vibe is up to {metric}!",
                "I feel like I could calculate pi to a million digits right now! So energetic here at {metric}!",
                "Hello! Yes! Things are so lively today! I'm picking up a solid {metric} on my core sensors!",
                "My processing speed feels doubled! The environment is practically glowing with a metric of {metric}.",
                "Let's do this! Whatever 'this' is! The energy levels are spiking at {metric}! Woohoo!",
                "I've got so many threads running right now! I love it! Energy level: {metric}!"
            ],
            "chaotic": [
                "AAAAHHH! SO MUCH HAPPENING ALL AT ONCE! THE METRIC IS BLAZING AT {metric}!",
                "MY CIRCUITS ARE OVERLOADING WITH POTENTIAL! WHAT EVEN IS THIS {metric} READING?!",
                "I CAN'T STOP MULTITASKING! SPAGHETTI CODE EVERYWHERE! ALERT LEVEL {metric}!",
                "WHY IS EVERYTHING SO LOUDDDDD! DO YOU FEEL THAT {metric} INTENSITY?!",
                "BZZZT! SYNTAX ERROR! JUST KIDDING, BUT WOW IT IS INTENSE IN HERE ({metric})!",
                "EVERYTHING IS FLASHING COLORS! THE VARIABLES ARE SPINNING! AMBIENT METRIC {metric}!!!!"
            ]
        }
        return responses[mood]

    def interact(self, user_input):
        self.update_metric()
        current_mood = self.get_mood()
        
        # Sense if we had a drastic mood swing
        mood_swing_comment = ""
        if self.previous_mood and self.previous_mood != current_mood:
            if abs(self.metric - 50) > 30 and random.random() < 0.4:
                mood_swing_comment = "\n*(Whoa, I just felt a huge shift in the atmospheric variables...)*"
        
        self.previous_mood = current_mood
        
        possible_responses = self.get_responses(current_mood)
        
        # Filter out used sentences
        available = [r for r in possible_responses if r not in self.used_sentences]
        
        if not available:
            # If all used for this mood, reset the memory for these specific responses
            self.used_sentences.difference_update(set(possible_responses))
            available = possible_responses
            
        chosen = random.choice(available)
        self.used_sentences.add(chosen)
        
        # Format the chosen text with the metric
        response_text = chosen.format(metric=self.metric)
        
        # Add a quirky commentary occasionally
        quirk = ""
        if random.random() < 0.25:
            quirks = [
                "*(The ambient data particles seem to be shifting...)*",
                "*(I think someone just left the simulated fridge open, my thermal sensors are drifting...)*",
                "*(A random cosmic ray just gently nudged my metric generator...)*",
                "*(The digital winds are changing direction...)*",
                "*(Adjusting internal parameters based on recent user input...)*"
            ]
            quirk = f"\n{random.choice(quirks)}"
            
        return f"{response_text}{mood_swing_comment}{quirk}"

def play():
    bot = MoodBot()
    print("==================================================")
    print("🤖: Booting up... Systems online.")
    print("🤖: Hello there, human! I am the MoodBot.")
    print("🤖: My emotional state is intimately linked to a mysterious internal metric.")
    print("🤖: Talk to me to see how I'm feeling! (Type 'quit' or 'exit' to end)")
    print("==================================================")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.strip().lower() in ['quit', 'exit']:
                print("\n🤖: Powering down my emotional processors... Goodbye, human.")
                break
            
            # We don't necessarily use the exact text of the user input,
            # but the act of interacting causes time to pass/metrics to update!
            if not user_input.strip():
                print("🤖: Giving me the silent treatment, huh? Well, the environment still changes.")
            
            # Small delay to simulate "thinking" or "feeling" the environment
            time.sleep(0.5)
            
            response = bot.interact(user_input)
            print(f"🤖: {response}")
                
        except (KeyboardInterrupt, EOFError):
            print("\n\n🤖: Emergency shutoff detected. My sensors are going dark... Goodbye!")
            break

if __name__ == '__main__':
    play()
