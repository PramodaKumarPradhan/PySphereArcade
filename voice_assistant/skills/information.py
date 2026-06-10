"""
ARIA — Information Skill
Time, date, jokes, calculations, system info, general Q&A
"""

import datetime
import logging
import random
import math
import re
import psutil

logger = logging.getLogger(__name__)


class Information:
    """General knowledge and information commands"""

    JOKES_EN = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "What do you call a fish without eyes? A fsh.",
        "Why did the math book look sad? Because it had too many problems.",
        "I'm reading a book about anti-gravity. It's impossible to put down!",
        "Why can't Elsa have a balloon? Because she'll let it go.",
        "What do you call cheese that isn't yours? Nacho cheese!",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "What did the ocean say to the beach? Nothing, it just waved!",
    ]

    JOKES_HI = [
        "टीचर: तुम्हें गणित कैसा लगता है?\nछात्र: यह ऐसा है जैसे इंटरनेट बिना WiFi के!",
        "पत्नी: आप सोचते हो मैं पैसा उड़ाती हूँ?\nपति: नहीं, आप तो नोट उड़ाती हो!",
        "डॉक्टर: आपको सब्जियाँ ज़्यादा खानी चाहिए।\nमैं: ठीक है, कल से आलू चिप्स दोगुनी करता हूँ।",
        "बच्चे का पहला शब्द: 'WiFi'\nबाप: ये तो मुझसे भी ज़्यादा होशियार निकला!",
        "टीचर: समझे?\nछात्र: हाँ सर!\nटीचर: क्या समझे?\nछात्र: कि नहीं समझे!",
        "मैं: Siri, मेरा जीवन सुधार दो।\nSiri: उसके लिए Google पर जाइए।",
    ]

    GREETINGS_EN = {
        'morning': "Good morning! Hope you have a wonderful and productive day ahead! ☀️",
        'afternoon': "Good afternoon! Hope your day is going great! 🌤️",
        'evening': "Good evening! Time to relax and wind down. 🌆",
        'night': "Good night! Sweet dreams and rest well! 🌙",
    }

    GREETINGS_HI = {
        'morning': "शुभ प्रभात! आपका दिन शानदार और उत्पादक हो! ☀️",
        'afternoon': "नमस्ते! दोपहर मुबारक! आशा है आपका दिन अच्छा जा रहा है! 🌤️",
        'evening': "शुभ संध्या! आराम करने का समय आ गया है। 🌆",
        'night': "शुभ रात्रि! अच्छे सपने आएँ! 🌙",
    }

    FACTS_EN = [
        "Glaciers and ice sheets hold about 69 percent of all the world's freshwater.",
        "The fastest gust of wind ever recorded on Earth was 253 miles per hour.",
        "Recent research shows that the Earth's inner core might have stopped rotating faster than the surface and could now be rotating slower.",
        "All the ants on Earth weigh about as much as all the humans.",
        "The first computer bug was an actual real moth found trapped in a relay of the Harvard Mark II computer in 1947.",
        "A day on Venus is longer than a year on Venus.",
        "Honey never spoils. You can theoretically eat 3,000-year-old honey.",
        "Bananas are berries, but strawberries aren't.",
        "Octopuses have three hearts and blue blood.",
        "Wombat poop is cube-shaped, which stops it from rolling away!"
    ]

    FACTS_HI = [
        "दुनिया का लगभग 69 प्रतिशत साफ पानी ग्लेशियरों और बर्फ की चादरों में जमा है।",
        "पृथ्वी पर हवा की सबसे तेज गति 253 मील प्रति घंटा दर्ज की गई थी।",
        "पृथ्वी के अंदरूनी कोर की घूर्णन गति सतह से कम हो सकती है।",
        "पृथ्वी पर मौजूद सभी चींटियों का कुल वजन सभी मनुष्यों के बराबर है।",
        "कंप्यूटर का पहला 'बग' एक असली पतंगा (moth) था जो 1947 में हार्वर्ड मार्क II कंप्यूटर में फंसा था।",
        "शुक्र (Venus) ग्रह का एक दिन उसके एक साल से भी बड़ा होता है।",
        "शह़द कभी खराब नहीं होता। आप हजारों साल पुराना शहद भी खा सकते हैं।",
        "केला वास्तव में एक बेरी है, लेकिन स्ट्रॉबेरी बेरी नहीं है।",
        "ऑक्टोपस के तीन दिल होते हैं और उनका खून नीला होता है।",
        "वोम्बैट (Wombat) नाम के जानवर का मल चौकोर (cube) आकार का होता है।"
    ]

    def __init__(self, config: dict):
        self.config = config
        logger.info("Information skill initialized")

    def tell_time(self) -> dict:
        """Tell the current time"""
        now = datetime.datetime.now()
        time_12 = now.strftime('%I:%M %p')
        time_24 = now.strftime('%H:%M')
        hour = now.hour
        minute = now.minute

        # Natural language time in Hindi
        period_hi = "सुबह" if hour < 12 else ("दोपहर" if hour < 17 else ("शाम" if hour < 20 else "रात"))
        hour_12 = hour % 12 or 12
        minute_str_hi = f"बजकर {minute} मिनट" if minute > 0 else "बजे"
        time_hi = f"{period_hi} के {hour_12} {minute_str_hi}"

        return {
            'success': True,
            'response': f"The current time is {time_12}",
            'response_hi': f"अभी {time_hi} हो रहे हैं",
            'data': {'time_12': time_12, 'time_24': time_24}
        }

    def tell_date(self) -> dict:
        """Tell today's date"""
        now = datetime.datetime.now()
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_names_hi = ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार']
        months_en = ['January','February','March','April','May','June',
                     'July','August','September','October','November','December']
        months_hi = ['जनवरी','फरवरी','मार्च','अप्रैल','मई','जून',
                     'जुलाई','अगस्त','सितंबर','अक्टूबर','नवंबर','दिसंबर']

        day_en = day_names[now.weekday()]
        day_hi = day_names_hi[now.weekday()]
        month_en = months_en[now.month - 1]
        month_hi = months_hi[now.month - 1]

        return {
            'success': True,
            'response': f"Today is {day_en}, {now.day} {month_en} {now.year}",
            'response_hi': f"आज {day_hi}, {now.day} {month_hi} {now.year} है",
            'data': {'day': day_en, 'date': now.strftime('%d/%m/%Y')}
        }

    def greet(self, language: str = 'en') -> dict:
        """Time-appropriate greeting"""
        hour = datetime.datetime.now().hour
        if hour < 12:
            period = 'morning'
        elif hour < 17:
            period = 'afternoon'
        elif hour < 20:
            period = 'evening'
        else:
            period = 'night'

        name = self.config.get('assistant', {}).get('name', 'Aria')
        greeting_en = self.GREETINGS_EN[period]
        greeting_hi = self.GREETINGS_HI[period]

        intro_en = f"Hello! I'm {name}, your intelligent voice assistant. {greeting_en} How can I help you today?"
        intro_hi = f"नमस्ते! मैं {name} हूँ, आपका बुद्धिमान आवाज़ सहायक। {greeting_hi} आज मैं आपकी कैसे मदद करूँ?"

        return {
            'success': True,
            'response': intro_en,
            'response_hi': intro_hi
        }

    def tell_joke(self, language: str = 'en') -> dict:
        """Tell a random joke"""
        if language == 'hi':
            joke = random.choice(self.JOKES_HI)
            return {'success': True, 'response': joke, 'response_hi': joke}
        joke = random.choice(self.JOKES_EN)
        return {
            'success': True,
            'response': joke,
            'response_hi': random.choice(self.JOKES_HI)
        }

    def calculate(self, expression: str) -> dict:
        """Evaluate a math expression safely"""
        try:
            # Clean and sanitize
            expr = expression.strip()
            expr = expr.replace('×', '*').replace('÷', '/').replace('^', '**')
            expr = expr.replace('into', '*').replace('by', '/')
            expr = re.sub(r'[^0-9+\-*/().% ]', '', expr)

            if not expr:
                return {'success': False, 'response': "Please provide a math expression to calculate",
                        'response_hi': "कोई गणितीय अभिव्यक्ति बताएं"}

            # Use safe eval with math functions
            safe_globals = {
                '__builtins__': {},
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'pow': pow, 'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e
            }
            result = eval(expr, safe_globals)

            if isinstance(result, float) and result == int(result):
                result = int(result)

            return {
                'success': True,
                'response': f"{expression} = {result}",
                'response_hi': f"{expression} = {result}",
                'data': {'expression': expression, 'result': result}
            }
        except ZeroDivisionError:
            return {'success': False, 'response': "Cannot divide by zero!",
                    'response_hi': "शून्य से भाग नहीं हो सकता!"}
        except Exception as e:
            return {'success': False,
                    'response': f"Could not calculate '{expression}'. Try like: '25 + 37'",
                    'response_hi': f"'{expression}' की गणना नहीं हो सकी। ऐसे बोलें: '25 + 37'"}

    def get_system_info(self) -> dict:
        """Get current system stats"""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')
            battery = psutil.sensors_battery()

            mem_used_gb = round(mem.used / (1024**3), 1)
            mem_total_gb = round(mem.total / (1024**3), 1)
            disk_free_gb = round(disk.free / (1024**3), 1)
            disk_total_gb = round(disk.total / (1024**3), 1)

            battery_str = ""
            battery_str_hi = ""
            if battery:
                status = "charging" if battery.power_plugged else "on battery"
                status_hi = "चार्जिंग" if battery.power_plugged else "बैटरी पर"
                battery_str = f" Battery: {battery.percent:.0f}% ({status})."
                battery_str_hi = f" बैटरी: {battery.percent:.0f}% ({status_hi})।"

            response = (
                f"System status: CPU usage {cpu}%, "
                f"RAM {mem_used_gb}GB / {mem_total_gb}GB ({mem.percent}%), "
                f"Disk {disk_free_gb}GB free of {disk_total_gb}GB.{battery_str}"
            )
            response_hi = (
                f"सिस्टम स्थिति: CPU {cpu}%, "
                f"RAM {mem_used_gb}GB / {mem_total_gb}GB ({mem.percent}%), "
                f"डिस्क {disk_free_gb}GB खाली।{battery_str_hi}"
            )

            return {
                'success': True,
                'response': response,
                'response_hi': response_hi,
                'data': {
                    'cpu': cpu, 'ram_percent': mem.percent,
                    'disk_free_gb': disk_free_gb,
                    'battery': battery.percent if battery else None,
                    'charging': battery.power_plugged if battery else None
                }
            }
        except Exception as e:
            return {'success': False, 'response': f"Could not get system info: {e}"}

    def battery_status(self) -> dict:
        """Get battery status specifically"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return {'success': True,
                        'response': "No battery detected. Running on AC power.",
                        'response_hi': "बैटरी नहीं मिली। AC पावर पर चल रहा है।"}

            pct = int(battery.percent)
            status = "charging 🔌" if battery.power_plugged else "on battery 🔋"
            status_hi = "चार्जिंग 🔌" if battery.power_plugged else "बैटरी पर 🔋"

            if not battery.power_plugged:
                if pct < 20:
                    advice = "Low battery! Please plug in your charger."
                    advice_hi = "बैटरी कम है! कृपया चार्जर लगाएं।"
                elif pct < 50:
                    advice = "Battery is moderate."
                    advice_hi = "बैटरी ठीक है।"
                else:
                    advice = "Battery is good."
                    advice_hi = "बैटरी अच्छी है।"
            else:
                advice = "Fully charged soon!" if pct > 90 else "Charging in progress."
                advice_hi = "जल्द पूरी चार्ज हो जाएगी!" if pct > 90 else "चार्जिंग जारी है।"

            return {
                'success': True,
                'response': f"Battery is at {pct}%, {status}. {advice}",
                'response_hi': f"बैटरी {pct}% है, {status_hi}। {advice_hi}",
                'data': {'percent': pct, 'charging': battery.power_plugged}
            }
        except Exception as e:
            return {'success': False, 'response': f"Battery check failed: {e}"}

    def help_menu(self) -> dict:
        """Return a list of supported commands"""
        commands = """
🎙️ ARIA Voice Commands Guide

📅 TIME & DATE
  • "What time is it?" / "समय बताओ"
  • "What's today's date?" / "आज की तारीख"

🖥️ SYSTEM
  • "Open [app name]" / "[app] खोलो"
  • "Volume up/down/mute" / "आवाज़ बढ़ाओ/घटाओ/म्यूट"
  • "Take a screenshot" / "स्क्रीनशॉट लो"
  • "Shutdown/Restart/Sleep/Lock screen"

🌐 WEB
  • "Search [query] on Google" / "Google पर [query] खोजो"
  • "Play [song] on YouTube" / "YouTube पर [song] लगाओ"
  • "What is [topic] on Wikipedia?"
  • "What's the weather in [city]?" / "मौसम बताओ"
  • "Open [website]"

⏰ PRODUCTIVITY
  • "Set a timer for 10 minutes" / "10 मिनट का टाइमर"
  • "Remind me to [task] in [time]" / "याद दिलाओ"
  • "Take a note: [message]"
  • "Open Word/Excel/PowerPoint"

📁 FILES
  • "Open Downloads/Documents/Desktop"
  • "Open File Explorer"

🏠 HOME/OFFICE
  • "Night mode on/off"
  • "Battery status" / "बैटरी बताओ"
  • "System info"

😄 FUN
  • "Tell me a joke" / "चुटकुला सुनाओ"
  • "Calculate [expression]"
  • "Switch to Hindi/English"
        """.strip()

        return {
            'success': True,
            'response': commands,
            'response_hi': commands,
            'is_long': True
        }

    def flip_coin(self) -> dict:
        """Simulate flipping a coin"""
        result = random.choice(['Heads', 'Tails'])
        result_hi = 'चित (Heads)' if result == 'Heads' else 'पट (Tails)'
        return {
            'success': True,
            'response': f"🪙 Tossed the coin... It's {result}!",
            'response_hi': f"🪙 सिक्का उछाला... {result_hi} आया है!"
        }

    def roll_die(self) -> dict:
        """Simulate rolling a 6-sided die"""
        val = random.randint(1, 6)
        return {
            'success': True,
            'response': f"🎲 Rolled the die... You got a {val}!",
            'response_hi': f"🎲 पासा फेंका... आपको {val} मिला है!"
        }

    def tell_fact(self, language: str = 'en') -> dict:
        """Tell a random interesting fact"""
        if language == 'hi':
            fact = random.choice(self.FACTS_HI)
            return {'success': True, 'response': fact, 'response_hi': fact}
        fact = random.choice(self.FACTS_EN)
        try:
            idx = self.FACTS_EN.index(fact)
            fact_hi = self.FACTS_HI[idx]
        except ValueError:
            fact_hi = random.choice(self.FACTS_HI)
        return {
            'success': True,
            'response': fact,
            'response_hi': fact_hi
        }

