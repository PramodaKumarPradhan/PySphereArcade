"""
ARIA — Web Tasks Skill
Google search, YouTube, Wikipedia, news, weather, open websites
"""

import webbrowser
import urllib.parse
import logging
import requests
import datetime

logger = logging.getLogger(__name__)

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class WebTasks:
    """Web browsing and information retrieval commands"""

    QUICK_SITES = {
        'google': 'https://www.google.com',
        'youtube': 'https://www.youtube.com',
        'gmail': 'https://mail.google.com',
        'facebook': 'https://www.facebook.com',
        'twitter': 'https://www.twitter.com',
        'x': 'https://www.x.com',
        'instagram': 'https://www.instagram.com',
        'linkedin': 'https://www.linkedin.com',
        'github': 'https://www.github.com',
        'stackoverflow': 'https://stackoverflow.com',
        'wikipedia': 'https://www.wikipedia.org',
        'amazon': 'https://www.amazon.in',
        'flipkart': 'https://www.flipkart.com',
        'netflix': 'https://www.netflix.com',
        'spotify': 'https://open.spotify.com',
        'news': 'https://news.google.com',
        'maps': 'https://maps.google.com',
        'translate': 'https://translate.google.com',
        'drive': 'https://drive.google.com',
        'meet': 'https://meet.google.com',
        'teams': 'https://teams.microsoft.com',
        'outlook': 'https://outlook.live.com',
        'onedrive': 'https://onedrive.live.com',
        'chatgpt': 'https://chat.openai.com',
        'whatsapp': 'https://web.whatsapp.com',
        'rediff': 'https://www.rediff.com',
        'ndtv': 'https://www.ndtv.com',
        'times of india': 'https://timesofindia.indiatimes.com',
        'bbc': 'https://www.bbc.com',
        'cricket': 'https://www.cricbuzz.com',
        'cricbuzz': 'https://www.cricbuzz.com',
    }

    def __init__(self, config: dict):
        self.config = config
        logger.info("WebTasks initialized")

    def google_search(self, query: str) -> dict:
        """Open Google search for a query"""
        encoded = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded}"
        webbrowser.open(url)
        return {
            'success': True,
            'response': f"Searching Google for '{query}'",
            'response_hi': f"'{query}' के लिए Google पर खोज रहा हूँ",
            'url': url
        }

    def youtube_search(self, query: str) -> dict:
        """Open YouTube search for a query"""
        encoded = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return {
            'success': True,
            'response': f"Searching YouTube for '{query}'",
            'response_hi': f"YouTube पर '{query}' खोज रहा हूँ",
            'url': url
        }

    def open_website(self, site: str) -> dict:
        """Open a website by name or URL"""
        site_lower = site.strip().lower()

        # Check quick sites map
        if site_lower in self.QUICK_SITES:
            url = self.QUICK_SITES[site_lower]
            webbrowser.open(url)
            return {
                'success': True,
                'response': f"Opening {site}",
                'response_hi': f"{site} खोल रहा हूँ",
                'url': url
            }

        # Try as URL directly
        if '.' in site:
            url = site if site.startswith('http') else f'https://{site}'
            webbrowser.open(url)
            return {'success': True, 'response': f"Opening {url}",
                    'response_hi': f"{url} खोल रहा हूँ", 'url': url}

        # Fallback: Google search
        return self.google_search(site)

    def wikipedia_search(self, query: str, language: str = 'en') -> dict:
        """Search Wikipedia and return a summary"""
        if WIKIPEDIA_AVAILABLE:
            try:
                wiki_lang = 'hi' if language == 'hi' else 'en'
                wikipedia.set_lang(wiki_lang)
                summary = wikipedia.summary(query, sentences=3, auto_suggest=True)
                return {
                    'success': True,
                    'response': summary,
                    'response_hi': summary,
                    'source': 'Wikipedia'
                }
            except wikipedia.exceptions.DisambiguationError as e:
                # Use the first option
                try:
                    summary = wikipedia.summary(e.options[0], sentences=3)
                    return {'success': True, 'response': summary, 'response_hi': summary}
                except Exception:
                    pass
            except Exception as e:
                logger.warning(f"Wikipedia error: {e}")

        # Fallback: open Wikipedia
        encoded = urllib.parse.quote(query)
        lang_code = 'hi' if language == 'hi' else 'en'
        url = f"https://{lang_code}.wikipedia.org/wiki/Special:Search/{encoded}"
        webbrowser.open(url)
        return {
            'success': True,
            'response': f"Opening Wikipedia for '{query}'",
            'response_hi': f"'{query}' के लिए Wikipedia खोल रहा हूँ"
        }

    def get_weather(self, city: str = 'Delhi') -> dict:
        """Get current weather using Open-Meteo (free, no API key)"""
        try:
            # Geocoding
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1"
            geo_resp = requests.get(geo_url, timeout=5)
            geo_data = geo_resp.json()

            if not geo_data.get('results'):
                return {'success': False, 'response': f"City '{city}' not found",
                        'response_hi': f"'{city}' शहर नहीं मिला"}

            result = geo_data['results'][0]
            lat, lon = result['latitude'], result['longitude']
            city_name = result.get('name', city)

            # Weather
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,"
                f"weathercode,apparent_temperature"
                f"&timezone=Asia%2FKolkata"
            )
            w_resp = requests.get(weather_url, timeout=5)
            w_data = w_resp.json()

            current = w_data.get('current', {})
            temp = current.get('temperature_2m', 'N/A')
            feels_like = current.get('apparent_temperature', 'N/A')
            humidity = current.get('relative_humidity_2m', 'N/A')
            wind = current.get('wind_speed_10m', 'N/A')
            wcode = current.get('weathercode', 0)

            condition = self._weather_code_to_text(wcode)

            response = (
                f"Weather in {city_name}: {condition}. "
                f"Temperature: {temp}°C, feels like {feels_like}°C. "
                f"Humidity: {humidity}%, Wind: {wind} km/h."
            )
            response_hi = (
                f"{city_name} में मौसम: {condition}। "
                f"तापमान: {temp}°C, महसूस: {feels_like}°C। "
                f"आर्द्रता: {humidity}%, हवा: {wind} km/h।"
            )

            return {
                'success': True,
                'response': response,
                'response_hi': response_hi,
                'data': {
                    'city': city_name, 'temp': temp,
                    'feels_like': feels_like, 'humidity': humidity,
                    'wind': wind, 'condition': condition
                }
            }

        except requests.exceptions.ConnectionError:
            return {'success': False,
                    'response': "No internet connection for weather data",
                    'response_hi': "मौसम के लिए इंटरनेट कनेक्शन नहीं है"}
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return {'success': False, 'response': f"Weather unavailable: {e}"}

    def _weather_code_to_text(self, code: int) -> str:
        """Convert WMO weather code to human-readable text"""
        codes = {
            0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
            45: 'Foggy', 48: 'Depositing rime fog',
            51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
            61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
            71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
            80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
            95: 'Thunderstorm', 96: 'Thunderstorm with hail', 99: 'Thunderstorm with heavy hail',
        }
        return codes.get(code, 'Unknown conditions')

    def open_maps(self, location: str = '') -> dict:
        """Open Google Maps for a location"""
        if location:
            encoded = urllib.parse.quote(location)
            url = f"https://maps.google.com/maps?q={encoded}"
        else:
            url = "https://maps.google.com"
        webbrowser.open(url)
        return {'success': True,
                'response': f"Opening Maps{f' for {location}' if location else ''}",
                'response_hi': f"Maps खोल रहा हूँ{f' {location} के लिए' if location else ''}"}

    def translate_text(self, text: str = '', from_lang: str = '', to_lang: str = '') -> dict:
        """Open Google Translate"""
        if text:
            encoded_text = urllib.parse.quote(text)
            sl = from_lang or 'auto'
            tl = to_lang or 'en'
            url = f"https://translate.google.com/?sl={sl}&tl={tl}&text={encoded_text}&op=translate"
        else:
            url = "https://translate.google.com"
        webbrowser.open(url)
        return {'success': True, 'response': "Opening Google Translate",
                'response_hi': "Google Translate खोल रहा हूँ"}

    def check_rain_advice(self, city: str = 'Delhi') -> dict:
        """Provide advice on whether the user needs an umbrella today based on forecast"""
        weather_res = self.get_weather(city)
        if not weather_res.get('success'):
            return weather_res

        data = weather_res.get('data', {})
        condition = data.get('condition', '').lower()
        city_name = data.get('city', city)

        is_raining = any(word in condition for word in ['rain', 'drizzle', 'shower', 'thunderstorm', 'storm'])

        if is_raining:
            response = f"Yes, you should take an umbrella today. The forecast in {city_name} shows {condition}."
            response_hi = f"हाँ, आज आपको छाता ले जाना चाहिए। {city_name} में {condition} का अनुमान है।"
        else:
            response = f"No, you probably don't need an umbrella. The forecast in {city_name} is {condition}."
            response_hi = f"नहीं, आपको छाते की आवश्यकता नहीं है। {city_name} में मौसम {condition} है।"

        return {
            'success': True,
            'response': response,
            'response_hi': response_hi,
            'data': {'city': city_name, 'need_umbrella': is_raining, 'condition': condition}
        }

    def get_stock_price(self, symbol: str) -> dict:
        """Fetch real-time stock price from Yahoo Finance API"""
        sym = symbol.strip().upper()
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                chart = data.get('chart', {})
                result = chart.get('result', [])
                if result:
                    meta = result[0].get('meta', {})
                    price = meta.get('regularMarketPrice')
                    currency = meta.get('currency', 'USD')
                    symbol_name = meta.get('symbol', sym)

                    if price is not None:
                        response = f"The stock price of {symbol_name} is {price} {currency}."
                        response_hi = f"{symbol_name} का शेयर मूल्य {price} {currency} है।"
                        return {
                            'success': True,
                            'response': response,
                            'response_hi': response_hi,
                            'data': {'symbol': symbol_name, 'price': price, 'currency': currency}
                        }

            return {
                'success': False,
                'response': f"Could not find stock information for '{symbol}'",
                'response_hi': f"'{symbol}' के लिए शेयर की जानकारी नहीं मिली।"
            }
        except Exception as e:
            logger.error(f"Stock check error: {e}")
            return {'success': False, 'response': f"Stock check unavailable: {e}"}

