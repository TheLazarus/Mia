import speech_recognition as sr
import random
import os
import mysql.connector
from bs4 import BeautifulSoup
import requests
import urllib.request
import pyttsx3
os.add_dll_directory(r'C:\Program Files (x86)\VideoLAN\VLC') # Need this if VLC path is not added in the PATH Variable
import vlc
import pafy
import time
from datetime import datetime

class MusiPi:

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init('sapi5',False)
        self.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
        self.mia_connector = mysql.connector.connect(user='root', password='e@Ad(f)12!@', host='127.0.0.1', database='mia')
        self.cursor = self.mia_connector.cursor()


    def listen(self):
        with sr.Microphone() as source:
            print("## SPEAK TO ME ##") #later will be removed!!
            self.recognizer.pause_threshold = 1
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source)
        return audio

    def talk(self,audio):
        print(audio) #later should be removed
        self.engine.say(audio)
        self.engine.runAndWait()

    def play_best_link(self,links):
        best_youtube_url = links[0]
        video = pafy.new(best_youtube_url)
        optimal_video = video.getbest()
        playurl = optimal_video.url
        Instance = vlc.Instance()
        player = Instance.media_player_new()
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        player.set_media(Media)
        player.play()
        print(player.get_state())

    def find_links(self,song):
        found_videos = []
        youtube_query = urllib.parse.quote(song)
        youtube_url = "https://www.youtube.com/results?search_query=" + youtube_query
        youtube_response = urllib.request.urlopen(youtube_url)
        youtube_unformatted_html = youtube_response.read()
        youtube_formatted_html = BeautifulSoup(youtube_unformatted_html,'html.parser')
        for video in youtube_formatted_html.findAll(attrs={'class':'yt-uix-tile-link'}):
            found_videos.append('https://www.youtube.com' + video['href'])
            break
        return found_videos

    def command(self):
        try:
            command_ = self.recognizer.recognize_google(self.listen())
            print('You said: '+ command_ + '/n')
            return command_

        except sr.UnknownValueError:
            self.assistant(self.command())

    def play_music(self):
        self.talk("So what song should I play?")
        try:
            song_name = self.recognizer.recognize_google(self.listen())
            found_links = self.find_links(song_name)
            print(f"Trying to find {song_name}...")
            print("Found Successfully")
            print(f"Link : {found_links}")
            self.play_best_link(found_links)

        except sr.UnknownValueError:
            self.talk("I was not able to understand what you just said!")
            self.play_music()

    def general_responses(self,command):
        id = 0
        question="SELECT question FROM mia_general_responses "
        self.cursor.execute(question)
        result=self.cursor.fetchall()
        for i in range(0,5):
            found_question = ''.join(result[i])
            if found_question in command:
                id = i+1
                break
        if(id == 0 ):
            self.talk('I beg your pardon')
        else:
            response="SELECT response FROM mia_general_responses WHERE id = " + str(id)
            self.cursor.execute(response)
            response_1 = ''.join(self.cursor.fetchall()[0])
            self.talk(response_1)

    def remember_subject_ask(self):
            with sr.Microphone() as source:
                try:
                    self.talk("PLEASE NAME THE SUBJECT") #later will be removed!!
                    self.recognizer.pause_threshold = 1
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = self.recognizer.listen(source)
                    return self.recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    self.talk("I didn't hear the subject properly, Sorry!")
                    self.remember_subject_ask()

    def choice(self,subject):
        subject_ = subject
        with sr.Microphone() as source:
                try:
                    self.talk("Do you want to remember about "+ subject_ + " ?")
                    self.recognizer.pause_threshold = 1
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = self.recognizer.listen(source)
                    return self.recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    self.talk("Say that again please?")
                    self.choice(subject_)

    def remember(self):
            subject = self.remember_subject_ask()
            user_choice = self.choice(subject)
            if 'yes' in user_choice:
                self.talk("SURE SURE MAHHHHH BROHH")
            elif 'no' in user_choice:
                self.talk("OKAY, I AM GONNA REVERT EVERYTHING BACK")

    def assistant(self,command):
        if 'play some music' in command:
            self.talk("Oh! In mood for some music today, Cool!")
            self.play_music()

        elif 'remember this' in command:
            self.remember()
        else:
            self.general_responses(command)


    def ask(self):
        while(True):
            self.assistant(self.command())

    def greet(self):
        greet_selector = random.randint(1,9)
        greet_user_query = "SELECT greetings FROM mia_greetings_and_goodbyes WHERE id = "+ str(greet_selector)
        self.cursor.execute(greet_user_query)
        greeting = ''.join(self.cursor.fetchall()[0])
        now = datetime.now()
        curr_hour = int(now.hour)
        print(curr_hour)
        if(curr_hour < 12):
            self.talk(greeting + ' Good Morning, I am Mia!')
        elif(curr_hour >= 12 and curr_hour < 17 ):
            self.talk(greeting + ' Good Afternoon, I am Mia')
        elif(curr_hour >= 17 and curr_hour < 20 ):
            self.talk(greeting + ' Good Evening, I am Mia')
        else:
            self.talk('For the night is dark and full of terrors!')
        self.talk("So what's in your mind today ?")
        self.ask()

if(__name__ == "__main__"):
    Pi = MusiPi()
    Pi.greet()
