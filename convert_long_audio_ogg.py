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


src = '/home/lenovo/Desktop/convert_audio_2/music'
dst_ogg = '/home/lenovo/Desktop/convert_audio_2/convert_to_ogg'
dst_chunk = '/home/lenovo/Desktop/convert_audio_2/split_5_seconds'
chunk_big_length_seconds = 1800 #seconds
chunk_length_seconds = 5 #seconds


class ConvertSplitAudioOGG:
    def __init__(self, src, dst_ogg, dst_chunk, chunk_big_length_seconds, chunk_length_seconds):
        self.src = src
        self.dst_ogg = dst_ogg
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
    
    def get_duration_ogg(self, file_path):
        with audioread.audio_open(file_path) as f:    
            totalsec = f.duration
            hours, mins, seconds = self.convert_to_minutes(int(totalsec))
            return hours*60 + mins

    def convert_file_to_ogg_long_audio(self, src_file_path, dst_file_path):
        command = f'ffmpeg -i {src_file_path} -f segment -segment_time {self.chunk_big_length_seconds} -c copy {dst_file_path}_segment%02d.ogg'
        subprocess.run(command, shell=True)

    def convert_file_to_ogg_short_audio(self, src_file_path, dst_file_path):
        sound = AudioSegment.from_file(src_file_path)
        sound.export(f'{dst_file_path}.ogg', format="ogg")

    def convert_file_folder_to_ogg(self):
        print(colored("Starting convert all format audios to ogg.....", "yellow"))
        try:
            all_file_names = os.listdir(self.src)
            type_audio_format = (".mp3", ".wav", ".wma", ".flac", ".alac", ".ogg", ".aiff")
            for each_file in all_file_names:
                # check file type 
                src_file = f'{self.src}/{each_file}'
                if (any(word in each_file for word in type_audio_format) or 'audio' in magic.from_file(src_file, mime=True)):
                    # rename
                    rename_file = each_file[:each_file.index(".")]
                    dst_file = f'{self.dst_ogg}/{rename_file}'
                    if(self.get_duration_all(src_file) < 30.0):
                        self.convert_file_to_ogg_short_audio(src_file, dst_file)
                    else:
                        self.convert_file_to_ogg_long_audio(src_file, dst_file)
            print(colored("Finish convert all audios format to ogg format", "yellow"))

        except:
            print(colored("Cannot convert all format audios to ogg", "red"))

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
    def process_audio_short_audio(self, file_name, src_path, folder_dst, chunk_length_seconds):
        myaudio = AudioSegment.from_file(src_path, "ogg")
        if(chunk_length_seconds is None or chunk_length_seconds==0):
            chunks = make_chunks(myaudio, self.chunk_length_seconds*1000)
        else:
            chunks = make_chunks(myaudio, chunk_length_seconds*1000)
        file_name_refactor = file_name.replace('.ogg','')
        data = []
        for i, chunk in enumerate(chunks):
            chunk_name = f'{folder_dst}/{file_name_refactor}_split_{i}.ogg'
            chunk.export(chunk_name, format="ogg")
            data_chunk = [f'{file_name_refactor}_{i}.ogg', chunk_name]
            data.append(data_chunk)
        self.create_path_file(f'{folder_dst}/{file_name_refactor}.csv', data)
    
    #Process audio with over chunks
    def process_audio_with_chunks_overlap(self, file_name, src_path, folder_dst, chunk_length_seconds):
        print(colored(f'Processing {file_name}.....', "yellow"))
        try:
            SECOND_OVERLAP = 1
            audio = AudioSegment.from_ogg(src_path)
            n = len(audio)
            counter = 1
            if(chunk_length_seconds is None or chunk_length_seconds==0):
                interval = self.chunk_length_seconds * 1000
            else:
                interval = chunk_length_seconds * 1000

            overlap = SECOND_OVERLAP * 1000
            start = 0
            end = 0
            flag = 0
            file_name_refactor = file_name.replace('.ogg','')
            data = []
            for i in range(0, 2 * n, interval):
                chunk_name = f'{folder_dst}/{file_name_refactor}_split_{counter}.ogg'
                data_chunk = [f'{file_name_refactor}_{counter}.ogg', chunk_name]
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
                chunk.export(chunk_name, format ="ogg")
                counter = counter + 1
                if flag == 1:
                    break

            # self.create_path_file(f'{folder_dst}/{file_name_refactor}.csv', data)
        except:
            print(colored(f'Cannot split {file_name}.....', "red"))

    #Process to audio has long duration
    def process_audio_long_audio(self, file_name, src_path, folder_dst, chunk_length_seconds):
        file_name_refactor = file_name.replace('.ogg','')
        chunk_name = f'{folder_dst}/{file_name_refactor}'
        if(chunk_length_seconds is None or chunk_length_seconds==0):
            command = f'ffmpeg -i {src_path} -f segment -segment_time {self.chunk_length_seconds} -c copy {chunk_name}_split%04d.ogg'
        else:
            command = f'ffmpeg -i {src_path} -f segment -segment_time {chunk_length_seconds} -c copy {chunk_name}_split%04d.ogg'
        subprocess.run(command, shell=True)
        # data = []
        # all_file_names = os.listdir(folder_dst)
        # for name in all_file_names:
        #     data_chunk = [name, f'{folder_dst}/{name}']
        #     data.append(data_chunk)
        # self.create_path_file(f'{folder_dst}/{file_name_refactor}.csv', data)

    def split_all_audio_to_frame(self, chunk_length_seconds):
        print(colored("Starting splitting chunk.....", "yellow"))
        all_file_names = os.listdir(self.dst_ogg)
        for each_file in all_file_names:
            if ('.ogg' in each_file):
                file_name = each_file.replace('.ogg','') + "_split"
                new_dst_folder = self.dst_chunk + '/' + file_name
                if os.path.exists(new_dst_folder) is False:
                    os.makedirs(new_dst_folder)
                # if(self.get_duration_ogg(self.dst_ogg + '/' + each_file)>30.0):
                #     self.process_audio_long_audio(each_file, self.dst_ogg + '/' + each_file, new_dst_folder, chunk_length_seconds)
                # else:
                #     self.process_audio_with_chunks_overlap(each_file, self.dst_ogg + '/' + each_file, new_dst_folder, chunk_length_seconds)
                self.process_audio_long_audio(each_file, self.dst_ogg + '/' + each_file, new_dst_folder, chunk_length_seconds)
                # self.process_audio_with_chunks_overlap(each_file, self.dst_ogg + '/' + each_file, new_dst_folder, chunk_length_seconds)

        print(colored("Finish splitting chunk", "yellow"))
    
    # cut audio from start to end
    def audio_cutter(self, src_path, dest_path, start_seconds, end_seconds):
        # f =  audioread.audio_open(src_path)    
        # totalsec = f.duration
        # hours, mins, seconds = self.convert_to_minutes(int(totalsec))
        # duration = hours*3600 + mins*60+ seconds

        if( start_seconds >= end_seconds):
            print(colored("start_time is greater than end_time, please check again", "red"))
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
            # if(endTime > duration*1000):
            #     endTime = duration - 5 
            song = AudioSegment.from_file(src_path)
            print('startTime: ',startTime)
            print('endTime: ',endTime)
            extract = song[startTime:endTime]
            extract.export(dest_path, format="ogg")

            print(colored("Completed editting audio", "yellow"))

# if __name__ == '__main__':
#     convert_ogg = ConvertSplitAudioOGG(src, dst_ogg, dst_chunk, chunk_big_length_seconds, chunk_length_seconds)
#     source = '/home/lenovo/Desktop/convert_audio_2/convert_to_ogg/23d7606e-84d6-4547-aa10-79604ffd9ec2_split0047.ogg'
#     dst = '/home/lenovo/Desktop/convert_audio_2/split_5_seconds/23d7606e-84d6-4547-aa10-79604ffd9ec2_split0047_split.ogg'
#     convert_ogg.audio_cutter(source, dst, 2, 4)
#     convert_ogg.split_all_audio_to_frame(chunk_length_seconds)
