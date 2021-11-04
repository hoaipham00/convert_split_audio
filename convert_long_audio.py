from os import path
from pydub import AudioSegment
from pydub.utils import make_chunks
import subprocess
import os
import csv
import magic
from termcolor import colored
import mutagen
import audioread


# src = '/home/lenovo/Desktop/convert_audio_2/music'
# dst_wav = '/home/lenovo/Desktop/convert_audio_2/convert_to_wav'
# dst_chunk = '/home/lenovo/Desktop/convert_audio_2/split_5_seconds'
# chunk_length_seconds = 5 #seconds
# chunk_big_length_seconds = 1800 #seconds


class ConvertSplitAudio:
    def __init__(self, src, dst_wav, dst_chunk, chunk_big_length_seconds, chunk_length_seconds):
        self.src = src
        self.dst_wav = dst_wav
        self.dst_chunk = dst_chunk
        self.chunk_big_length_seconds = chunk_big_length_seconds
        self.chunk_length_seconds = chunk_length_seconds

    def convert_to_minutes(self, length):
        hours = length // 3600  # calculate in hours
        length %= 3600
        mins = length // 60  # calculate in minutes
        length %= 60
        seconds = length  # calculate in seconds
        return hours, mins, seconds 

    def get_duration_all(self, file_path):
        audio = mutagen.File(file_path)
        totalsec = int(audio.info.length)
        hours, mins, seconds = self.convert_to_minutes(int(totalsec))
        return hours*60 + mins
    
    def get_duration_wav(self, file_path):
        with audioread.audio_open(file_path) as f:    
            totalsec = f.duration
            hours, mins, seconds = self.convert_to_minutes(int(totalsec))
            return hours*60 + mins

    def convert_file_to_wav_long_audio(self, src_file_path, dst_file_path):
        command = f'ffmpeg -i {src_file_path} -f segment -segment_time {self.chunk_big_length_seconds} -c copy {dst_file_path}_segment%02d.wav'
        subprocess.run(command, shell=True)

    def convert_file_to_wav_short_audio(self, src_file_path, dst_file_path):
        sound = AudioSegment.from_file(src_file_path)
        sound.export(f'{dst_file_path}.wav', format="wav")

    def convert_file_folder_to_wav(self):
        print(colored("Starting convert all format audios to wave.....", "yellow"))
        try:
            all_file_names = os.listdir(self.src)
            type_audio_format = (".mp3", ".wav", ".wma", ".flac", ".alac", ".ogg", ".aiff")
            for each_file in all_file_names:
                # check file type 
                src_file = f'{self.src}/{each_file}'
                if (any(word in each_file for word in type_audio_format) or 'audio' in magic.from_file(src_file, mime=True)):
                    # rename
                    rename_file = each_file[:each_file.index(".")]
                    dst_file = f'{self.dst_wav}/{rename_file}'
                    if(self.get_duration_all(src_file) < 20.0):
                        self.convert_file_to_wav_short_audio(src_file, dst_file)
                    else:
                        self.convert_file_to_wav_long_audio(src_file, dst_file)
            print(colored("Finish convert all audios format to wave format", "yellow"))

        except:
            print(colored("Cannot convert all format audios to wave", "red"))

    def create_path_file(self, file_name, data):
        try:
            header = ['chunk_name', 'path']
            with open(file_name, 'w', encoding='UTF8') as f:
                f.truncate()
                writer = csv.writer(f)
                writer.writerow(header)
                for a in data:
                    writer.writerow(a)
        except:
            print(colored('Cannot write path file, please check and try again', 'red'))

    #Process for audio has duration <= 20 minutes 
    def process_audio_short_audio(self, file_name, src_path, folder_dst):
        myaudio = AudioSegment.from_file(src_path, "wav")
        chunks = make_chunks(myaudio, self.chunk_length_seconds*1000)
        file_name_refactor = file_name.replace('.wav','')
        data = []
        for i, chunk in enumerate(chunks):
            chunk_name = f'{folder_dst}/{file_name_refactor}_split_{i}.wav'
            chunk.export(chunk_name, format="wav")
            data_chunk = [f'{file_name_refactor}_{i}.wav', chunk_name]
            data.append(data_chunk)
        self.create_path_file(f'{folder_dst}/{file_name_refactor}.csv', data)
    
    #Process audio with over chunks
    def process_audio_with_chunks_overlap(self, file_name, src_path, folder_dst):
        print(colored(f'Processing {file_name}.....', "yellow"))
        try:
            SECOND_OVERLAP = 1
            audio = AudioSegment.from_wav(src_path)
            n = len(audio)
            counter = 1
            interval = 5 * 1000
            overlap = SECOND_OVERLAP * 1000
            start = 0
            end = 0
            flag = 0
            file_name_refactor = file_name.replace('.wav','')
            data = []
            for i in range(0, 2 * n, interval):
                chunk_name = f'{folder_dst}/{file_name_refactor}_split_{counter}.wav'
                data_chunk = [f'{file_name_refactor}_{counter}.wav', chunk_name]
                data.append(data_chunk)
                if i == 0:
                    start = 0
                    end = interval
                else:
                    start = end - overlap
                    end = start + interval
                if end >= n:
                    end = n
                    flag = 1
                chunk = audio[start:end]
                chunk.export(chunk_name, format ="wav")
                counter = counter + 1
                if flag == 1:
                    break

            self.create_path_file(f'{folder_dst}/{file_name_refactor}.csv', data)
        except:
            print(colored(f'Cannot split {file_name}.....', "red"))

    #Process to audio has long duration
    def process_audio_long_audio(self, file_name, src_path, folder_dst):
        file_name_refactor = file_name.replace('.wav','')
        chunk_name = f'{folder_dst}/{file_name_refactor}'
        command = f'ffmpeg -i {src_path} -f segment -segment_time {self.chunk_length_seconds} -c copy {chunk_name}_split%04d.wav'
        subprocess.run(command, shell=True)
        data = []
        all_file_names = os.listdir(folder_dst)
        for name in all_file_names:
            data_chunk = [name, f'{folder_dst}/{name}']
            data.append(data_chunk)
        self.create_path_file(f'{folder_dst}/{file_name_refactor}.csv', data)

    def split_all_audio_to_frame(self):
        print(colored("Starting splitting chunk.....", "yellow"))
        all_file_names = os.listdir(self.dst_wav)
        for each_file in all_file_names:
            if ('.wav' in each_file):
                file_name = each_file.replace('.wav','') + "_split"
                new_dst_folder = self.dst_chunk + '/' + file_name
                if os.path.exists(new_dst_folder) is False:
                    os.makedirs(new_dst_folder)
                if(self.get_duration_wav(self.dst_wav + '/' + each_file)>30.0):
                    self.process_audio_long_audio(each_file, self.dst_wav + '/' + each_file, new_dst_folder)
                else:
                    self.process_audio_with_chunks_overlap(each_file, self.dst_wav + '/' + each_file, new_dst_folder)

        print(colored("Finish splitting chunk", "yellow"))
    
    def audio_cutter(self, src_path, dest_path, start_seconds, end_seconds):
        duration = self.get_duration_wav(src_path)
        if( duration < end_seconds):
            print(colored("end_time is greater than duration of audio, please check again", "red"))
        elif(start_seconds < 0):
            print('Invalid params, please check again')
            print(colored("Working in processing.....", "red"))
            return
        else:
            print(colored("Working in processing.....", "yellow"))
            #to miliseconds
            startTime = start_seconds*1000 - 500
            if (startTime <= 0):
                startTime = 0
            endTime = end_seconds*1000 + 500
            if(endTime > duration*1000):
                endTime = duration
            song = AudioSegment.from_wav(src_path)
            extract = song[startTime:endTime]
            extract.export(dest_path, format="wav")
            print(colored("Completed editting audio", "yellow"))
