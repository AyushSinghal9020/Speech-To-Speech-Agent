import cohere
import sounddevice as sd
import wavio
from scipy.io.wavfile import write
import numpy as np
import os
from gtts import gTTS
import time
import speech_recognition as sr
import pygame
import time

co = cohere.Client(api_key = 'UJLdgjWaITlOrEB1xkl5DAJ5KGraIl18zAiGA1b0')
recognizer = sr.Recognizer()

def recognize_speech() : 

    print('Listening...') 

    recording = sd.rec(
        int(2 * 44000) , 
        samplerate = 44000 , 
        channels = 1 , 
        dtype = np.int16 , 
        device = 0)
    sd.wait()

    write('input.wav', 44000 , recording)

    with sr.AudioFile('input.wav') as source : audio = recognizer.record(source)
    print('Recognizing...')

    try : text = recognizer.recognize_google(audio)
    except sr.UnknownValueError : text = ''

    print(f'User said: {text}')

    return text

def generate_response(text) : 

    response = ''

    for event in co.chat_stream(message = text) : 

        if event.event_type == 'text-generation' : 

            print(event.text , end = ' ' , flush = True)
            response += event.text + ' '

        elif event.event_type == 'stream-end' : 

            print(f'\nStream ended: {event.finish_reason}')

            break

    return response.strip()

def speak_text(text) : 

    tts = gTTS(text = text , lang = 'en')
    tts.save('response.mp3')

    pygame.mixer.init()
    pygame.mixer.music.load('response.mp3')
    pygame.mixer.music.play()
    # os.system("mpg321 response.mp3")  # You can use any audio player that supports mp3

    while pygame.mixer.music.get_busy() : 

        user_input = recognize_speech()

        if user_input == '' : continue
        else : pygame.mixer.music.stop()

def main() : 

    while True : 

        user_text = ['-' , '-']

        while True : 
            
            user_input = recognize_speech()

            user_text.append(user_input)

            open('conversation.txt' , 'a').write(user_input + '\n') # Test

            if user_text[-2 :] == ['' , ''] : 

                user_input = ' '.join(user_text[: -2])
                user_text = ['-' , '-']

                break

        if user_input.lower() in ['exit' , 'quit' , 'stop'] : 

            print('Ending conversation.')

            break

        if user_input : 

            response = generate_response(user_input)
            if response : speak_text(response)

        time.sleep(1) 

if __name__ == '__main__':
    main()

