#### AUTHOR ---->> SARTHAK SHARMA ####
#### ALL THE NECESSARY IMPORTS ###

import speech_recognition as sr
import random
import os
import mysql.connector
from bs4 import BeautifulSoup
import requests
import urllib.request
import pyttsx3
os.add_dll_directory(r'C:\Program Files (x86)\VideoLAN\VLC') # Need this if VLC path is not added in the PATH Variable, so confirms working in both the cases
import vlc
import pafy
import time
from datetime import datetime

class MusiPi:

    # CLASS CONSTRUCTOR #

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init('sapi5',False)
        self.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
        self.mia_connector = mysql.connector.connect(user='root', password='e@Ad(f)12!@', host='127.0.0.1', database='mia')
        self.cursor = self.mia_connector.cursor()

    # METHOD USED TO CONVERT TEXT TO SPEECH USING SAPI(MICROSOFT'S SOUND API ) AND PyTTX3 #

    def talk(self,audio):
        print(audio) #later should be removed
        self.engine.say(audio)
        self.engine.runAndWait()

    # TO PLAY THE YOUTUBE VIDEO IN A VLC INSTANCE #

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
        print(Media.get_duration())

    # FIND ALL THE VIDEOS MATCHED WITH THE SEARCH STRING #

    def find_links(self,song):
        found_videos = []
        youtube_query = urllib.parse.quote(str(song))
        youtube_url = "https://www.youtube.com/results?search_query=" + youtube_query
        youtube_response = urllib.request.urlopen(youtube_url)
        youtube_unformatted_html = youtube_response.read()
        youtube_formatted_html = BeautifulSoup(youtube_unformatted_html,'html.parser')
        for video in youtube_formatted_html.findAll(attrs={'class':'yt-uix-tile-link'}):
            found_videos.append('https://www.youtube.com' + video['href'])
            break
        return found_videos

    def command(self,question_text):
        with sr.Microphone() as source:
            try:
                self.talk(question_text) #later will be removed!!
                self.recognizer.pause_threshold = 1
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source)
                conv_text = self.recognizer.recognize_google(audio)
                print(conv_text)
                return conv_text
            except sr.UnknownValueError:
                self.talk("I was not able to hear that!")
                return self.command(question_text)

    # METHOD USED TO PLAY YOUTUBE SONGS, USES find_links() and play_best_link() #

    def play_music(self):
            self.talk("So what song should I play?")
            song_name = self.command("I am listening!")
            found_links = self.find_links(song_name)
            print(f"Trying to find {song_name}...")
            print("Found Successfully")
            print(f"Link : {found_links}")
            self.play_best_link(found_links)

   # THIS METHOD HANDLES THE GENERAL BEHAVIOUR OF MIA #

    def responses(self,command):
        response_ids = []
        responses = []
        fetch_rows = "SELECT COUNT(*) FROM mia_memory"
        self.cursor.execute(fetch_rows)
        num_rows_tuple = self.cursor.fetchall()
        num_rows_tuple = [[str(x) for x in tup] for tup in num_rows_tuple]
        num_rows = int(num_rows_tuple[0][0])
        elements = num_rows + 2
        subject="SELECT subject FROM mia_memory "
        self.cursor.execute(subject)
        result=self.cursor.fetchall()
        for i in range(2,elements):
            found_question = ''.join(result[i-2])
            if found_question in command:
                response_ids.append(i)
        if(len(response_ids) == 0 ):
            self.talk('I beg your pardon')
        else:
            for id in range(0,len(response_ids)):
                response="SELECT facts FROM mia_memory WHERE id = " + str(id)
                self.cursor.execute(response)
                response_final = ''.join(self.cursor.fetchall()[0])
                self.talk(response_final)

   # MAIN FUNCTION THAT HANDLES THE MEMORY FUNCTION, HOW MIA REMEMBERS, ALL THE BEHAVIOUR IS IN HERE #

    def remember(self):
            subject = self.command("Please name the subject :-")
            user_choice = self.command("Do you want to remember about "+subject+" ?")
            if 'yes' in user_choice:
                facts = self.command("Please state some facts about "+subject)
                insert_subject_query = "INSERT INTO mia_memory(subject,facts)" \
                                       "VALUES(%s,%s)"
                args = (subject,facts)
                try:
                    self.cursor.execute(insert_subject_query,args)
                    self.talk("I am saving the information, so that we can agree on the references later...")
                    self.mia_connector.commit() #FOR COMMITTING THE FINAL CHANGES
                    self.talk("Okay, so now I know about "+subject)
                except Error as error:
                    print(error)
            elif 'no' in user_choice:
                self.talk("OKAY, I AM GONNA REVERT EVERYTHING BACK")

    # MAIN ASSIStANT LOOP, USES COMMAND and RUNS IN AN INFINITE LOOP, HANDLES ALL THE INITIAL CONDITIONS #

    def assistant(self,command):
        if command is None:
            print("I was not able to hear that!")
        elif 'play some music' in command:
            self.talk("Oh! In mood for some music today, Cool!")
            self.play_music()

        elif 'remember this' in command:
            self.remember()
        else:
            self.responses(command)

    # MAIN LOOP #

    def ask(self):
        while(True):
            self.assistant(self.command("I am listening.."))

    # FOR WARM WELCOMES #

    def greet(self):
        greet_selector = random.randint(1,11)
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

# EXECUTION POINT, ALL OBJECT INSTANCES ARE CREATED HERE #
if(__name__ == "__main__"):
    Pi = MusiPi()
    Pi.greet()
