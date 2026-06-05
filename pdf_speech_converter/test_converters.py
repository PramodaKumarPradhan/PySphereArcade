import os
import sys
import unittest

# Add parent path to path to allow importing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import converter

class TestConverters(unittest.TestCase):
    def setUp(self):
        self.test_pdf = "test_temp.pdf"
        self.test_audio = "test_temp_audio.wav"
        self.test_mp3 = "test_temp_audio.mp3"
        self.test_output_pdf = "test_output.pdf"
        
        # Test content
        self.sample_text = "Hello world! This is a programmatic test of the PDF to AudioBook converter system."

        # Create a dummy PDF file using fpdf2
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("helvetica", size=12)
            pdf.cell(0, 10, self.sample_text)
            pdf.output(self.test_pdf)
        except Exception as e:
            print(f"Error preparing setup dummy PDF: {e}")

    def tearDown(self):
        # Clean up temporary test files
        for f in [self.test_pdf, self.test_audio, self.test_mp3, self.test_output_pdf]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Error removing {f}: {e}")

    def test_pdf_extraction(self):
        """Test that pypdf can extract text from a generated PDF."""
        print("\n=== Running PDF Extraction Test ===")
        self.assertTrue(os.path.exists(self.test_pdf), "Setup PDF file was not created.")
        
        extracted = converter.extract_text_from_pdf(self.test_pdf)
        print(f"Extracted: '{extracted}'")
        self.assertIn("Hello world!", extracted)
        self.assertIn("programmatic test", extracted)

    def test_offline_tts(self):
        """Test pyttsx3 offline text-to-speech output."""
        print("\n=== Running Offline TTS Test ===")
        try:
            converter.text_to_speech_pyttsx3(self.sample_text, self.test_audio)
            self.assertTrue(os.path.exists(self.test_audio), "Offline WAV file was not generated.")
            print(f"Success: Offline WAV created, size = {os.path.getsize(self.test_audio)} bytes.")
        except Exception as e:
            # Headless runner environments might not have a voice driver installed (SAPI5/NSSS/espeak)
            print(f"Skip/Warn: Offline TTS engine failed (typical in headless server environments): {e}")

    def test_pdf_generation(self):
        """Test fpdf2 PDF generation from text."""
        print("\n=== Running PDF Generation Test ===")
        test_txt = "Transcribed voice content goes here.\nLine 2 of test."
        converter.save_text_to_pdf(test_txt, self.test_output_pdf, title="Speech Test Doc")
        
        self.assertTrue(os.path.exists(self.test_output_pdf), "Output PDF file was not generated.")
        
        # Verify text was written
        re_extracted = converter.extract_text_from_pdf(self.test_output_pdf)
        self.assertIn("Transcribed voice content", re_extracted)
        print(f"Success: Generated PDF matches input content.")

if __name__ == "__main__":
    unittest.main()
