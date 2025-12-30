"""
Example usage of AudioService

This file demonstrates how to use the text-to-speech audio service.
"""

from app.services.audio_service import audio_service


def example_basic_audio():
    """Generate a basic audio file."""
    print("\n=== Example 1: Basic Audio Generation ===")
    
    text = "Welcome to the magical world of AI story generation. This is a test of the text to speech system."
    output_path = "output/test_audio.mp3"
    
    try:
        result = audio_service.generate_audio(
            text=text,
            output_path=output_path,
            lang='en'
        )
        print(f"Success! Audio saved to: {result}")
        
        # Validate the file
        file_info = audio_service.validate_audio_file(result)
        print(f"File size: {file_info['size_kb']:.2f} KB")
        print(f"Estimated duration: {file_info['estimated_duration']:.1f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")


def example_estimate_duration():
    """Estimate audio duration without generating."""
    print("\n=== Example 2: Estimate Duration ===")
    
    texts = [
        "A short sentence.",
        "This is a medium length sentence that contains a few more words than the previous one.",
        "This is a much longer sentence that goes on and on, describing many things in great detail, using lots of words to paint a vivid picture in the reader's mind about what is happening in the story."
    ]
    
    for text in texts:
        try:
            duration = audio_service.estimate_duration(text)
            word_count = len(text.split())
            print(f"Text: {text[:60]}...")
            print(f"  Words: {word_count} | Est. Duration: {duration:.1f}s")
        except Exception as e:
            print(f"Error: {e}")


def example_split_long_text():
    """Split long text into chunks."""
    print("\n=== Example 3: Split Long Text ===")
    
    long_text = """
    Once upon a time, in a land far away, there lived a brave knight named Sir Alexander.
    He was known throughout the kingdom for his courage and honor.
    One day, the king summoned him to the castle with urgent news.
    A fearsome dragon had been spotted near the village, terrorizing the peaceful inhabitants.
    Sir Alexander knew he had to act quickly to protect the innocent people.
    He gathered his sword, shield, and armor, preparing for the dangerous journey ahead.
    As he rode through the dark forest, he could hear the dragon's roar in the distance.
    The ground trembled with each step the mighty beast took.
    But Sir Alexander's determination never wavered, for he knew the safety of the kingdom depended on his bravery.
    """
    
    try:
        # Split into 30-second chunks
        chunks = audio_service.split_text_by_duration(
            text=long_text,
            max_duration=30
        )
        
        print(f"Split text into {len(chunks)} chunks:")
        for idx, chunk in enumerate(chunks, 1):
            duration = audio_service.estimate_duration(chunk)
            print(f"\nChunk {idx} (~{duration:.1f}s):")
            print(f"  {chunk[:80]}...")
            
    except Exception as e:
        print(f"Error: {e}")


def example_multiple_languages():
    """Generate audio in different languages."""
    print("\n=== Example 4: Multiple Languages ===")
    
    texts_languages = [
        ("Hello, welcome to our story!", "en", "english"),
        ("¡Hola, bienvenido a nuestra historia!", "es", "spanish"),
        ("Bonjour, bienvenue dans notre histoire!", "fr", "french"),
        ("Hallo, willkommen zu unserer Geschichte!", "de", "german"),
    ]
    
    for text, lang, lang_name in texts_languages:
        try:
            output_path = f"output/audio_{lang}.mp3"
            result = audio_service.generate_audio(
                text=text,
                output_path=output_path,
                lang=lang
            )
            print(f"✓ Generated {lang_name} audio: {output_path}")
        except Exception as e:
            print(f"✗ Failed {lang_name}: {e}")


def example_multiple_audios():
    """Generate multiple audio files from a list."""
    print("\n=== Example 5: Generate Multiple Audio Files ===")
    
    story_scenes = [
        "Chapter one: The journey begins in a small village.",
        "Chapter two: Our hero meets a mysterious stranger.",
        "Chapter three: A dangerous quest is revealed.",
        "Chapter four: The adventure through the dark forest.",
        "Chapter five: The final confrontation with the dragon."
    ]
    
    try:
        results = audio_service.generate_multiple_audios(
            texts=story_scenes,
            output_dir="output/story_audio",
            lang='en',
            prefix="chapter"
        )
        
        print(f"\nSuccess! Generated {len(results)} audio files:")
        for path in results:
            print(f"  - {path}")
            
    except Exception as e:
        print(f"Error: {e}")


def example_error_handling():
    """Demonstrate error handling."""
    print("\n=== Example 6: Error Handling ===")
    
    # Test with empty text
    try:
        audio_service.generate_audio(
            text="",
            output_path="output/empty.mp3"
        )
    except ValueError as e:
        print(f"✓ Caught expected error (empty text): {e}")
    
    # Test with unsupported language
    try:
        audio_service.generate_audio(
            text="Test",
            output_path="output/test.mp3",
            lang="invalid"
        )
    except ValueError as e:
        print(f"✓ Caught expected error (invalid language): {e}")
    
    # Test with very long text
    try:
        long_text = "word " * 2000  # 2000 words
        audio_service.generate_audio(
            text=long_text,
            output_path="output/toolong.mp3"
        )
    except ValueError as e:
        print(f"✓ Caught expected error (text too long): {e}")


def example_validate_audio():
    """Validate an existing audio file."""
    print("\n=== Example 7: Validate Audio File ===")
    
    # First generate an audio file
    text = "This is a test audio file for validation."
    output_path = "output/validation_test.mp3"
    
    try:
        audio_service.generate_audio(text, output_path)
        
        # Now validate it
        info = audio_service.validate_audio_file(output_path)
        
        print(f"Audio file validation:")
        print(f"  Path: {info['path']}")
        print(f"  Size: {info['size_kb']:.2f} KB ({info['size_bytes']} bytes)")
        print(f"  Format: {info['format']}")
        print(f"  Estimated duration: {info['estimated_duration']:.1f}s")
        print(f"  Exists: {info['exists']}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("AudioService Examples")
    print("=" * 60)
    
    try:
        example_basic_audio()
        example_estimate_duration()
        example_split_long_text()
        example_multiple_languages()
        example_multiple_audios()
        example_error_handling()
        example_validate_audio()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
