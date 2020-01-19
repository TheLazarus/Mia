import speech_recognition as sr
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
        self.engine = pyttsx3.init('sapi5',False)
        self.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
        self.mia_connector = mysql.connector.connect(user='root', password='e@Ad(f)12!@', host='127.0.0.1', database='mia')
        self.mia_connector.close()

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
        print(player.get_state()) #TO KEEP THE PLAYER RUNNING 

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
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("## SPEAK TO ME ##") #later will be removed!!
            recognizer.pause_threshold = 1
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

        try:
            command_ = recognizer.recognize_google(audio)
            print('You said: '+ command_ + '/n')

        except sr.UnknownValueError:
            self.assistant(self.command())

        return command_

    def play_music(self):
        song_recognizer = sr.Recognizer()
        self.talk("So what song should I play?")
        while(True):
            with sr.Microphone() as source:
                print("## SPEAK TO ME ##") #later will be removed!
                song_recognizer.pause_threshold = 1
                song_recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = song_recognizer.listen(source)
            try:
                song_name = song_recognizer.recognize_google(audio)
                found_links = self.find_links(song_name)
                print(f"Trying to find {song_name}...")
                print("Found Successfully")
                print(f"Link : {found_links}")
                break

            except sr.UnknownValueError:
                self.talk("I was not able to understand what you just said!")

        self.play_best_link(found_links)


    def assistant(self,command):
        if 'play some music' in command:
            self.talk("Oh! In mood for some music today, huh?")
            self.play_music()

    def ask(self):
        while(True):
            self.assistant(self.command())

    def greet(self):
        now = datetime.now()
        curr_hour = int(now.hour)
        print(curr_hour)
        if(curr_hour < 12):
            self.talk('Good Morning, I am Mia!')
        elif(curr_hour >= 12 and curr_hour < 17 ):
            self.talk('Good Afternoon, I am Mia')
        elif(curr_hour >= 17 and curr_hour < 20 ):
            self.talk('Good Evening, I am Mia')
        else:
            self.talk('For the night is dark and full of terrors!')
        self.talk("So what's in your mind today ?")
        self.ask()





if(__name__ == "__main__"):
    Pi = MusiPi()
    Pi.greet()
