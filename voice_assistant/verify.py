"""
ARIA -- Quick Verification Script
Run this to check all imports are working correctly.
"""
# Force UTF-8 output on Windows
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print(f"Python: {sys.version}")
print()

checks = []

def check(name, fn):
    try:
        fn()
        print(f"  [OK] {name}")
        checks.append((name, True, None))
    except Exception as e:
        print(f"  [FAIL] {name} -- {e}")
        checks.append((name, False, str(e)))

print("=== Checking Core Dependencies ===")
check("Flask", lambda: __import__('flask'))
check("Flask-SocketIO", lambda: __import__('flask_socketio'))
check("Flask-CORS", lambda: __import__('flask_cors'))

print("\n=== Checking Language ===")
check("SpeechRecognition", lambda: __import__('speech_recognition'))
check("pyttsx3", lambda: __import__('pyttsx3'))
check("gTTS", lambda: __import__('gtts'))
check("pygame", lambda: __import__('pygame'))
check("googletrans", lambda: __import__('googletrans'))
check("langdetect", lambda: __import__('langdetect'))

print("\n=== Checking System Control ===")
check("psutil", lambda: __import__('psutil'))
check("pyautogui", lambda: __import__('pyautogui'))
check("requests", lambda: __import__('requests'))
check("wikipedia", lambda: __import__('wikipedia'))

print("\n=== Checking Optional (Windows) ===")
check("pycaw (volume)", lambda: __import__('pycaw'))
check("screen-brightness-control", lambda: __import__('screen_brightness_control'))
check("pywin32", lambda: __import__('win32api'))
check("Gemini AI", lambda: __import__('google.generativeai'))

print("\n=== Checking ARIA Modules ===")
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
check("language.recognizer", lambda: __import__('language.recognizer'))
check("language.synthesizer", lambda: __import__('language.synthesizer'))
check("language.translator", lambda: __import__('language.translator'))
check("skills.system_control", lambda: __import__('skills.system_control'))
check("skills.information", lambda: __import__('skills.information'))
check("assistant_core", lambda: __import__('assistant_core'))

passed = sum(1 for _, ok, _ in checks if ok)
failed = len(checks) - passed

print(f"\n{'='*40}")
print(f"Results: {passed}/{len(checks)} passed | {failed} failed")
if failed > 0:
    print("\nFailed items (non-critical issues are OK):")
    for name, ok, err in checks:
        if not ok:
            print(f"  • {name}: {err}")
print("="*40)
if failed == 0:
    print("🎉 All checks passed! Run: python app.py")
elif passed >= len(checks) * 0.7:
    print("✅ Core features ready. Some optional features may not work.")
    print("   Run: python app.py")
else:
    print("⚠️  Some required packages missing. Run: pip install -r requirements.txt")
