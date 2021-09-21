from os import path
from pydub import AudioSegment
from pydub.utils import make_chunks
import shutil
import os
import glob
import math
import wave
import csv 

src = '/home/lenovo/Desktop/convert_audio/music/'
dst_wav = '/home/lenovo/Desktop/result'
dst_chunk = '/home/lenovo/Desktop/result'


class ConvertSplitAudio:

    def __init__(self, src, dst_wav, dst_chunk, chunk_length_ms):
        self.src = src
        self.dst_wav = dst_wav
        self.dst_chunk = dst_chunk
        self.chunk_length_ms = chunk_length_ms

    def convert_file_to_wav(self, src_file_path, dst_file_path):
        sound = AudioSegment.from_file(src_file_path)
        sound.export(f'{dst_file_path}.wav', format="wav")

    def conver_file_folder_to_wav(self):
        all_file_names = os.listdir(self.src)
        for each_file in all_file_names:
            if (any(word in each_file for word in (".mp3", "wav"))):
                src_file = f'{self.src}/{each_file}'
                rename_file = each_file.replace('.mp3','')
                dst_file = f'{self.dst_wav}/{rename_file}'
                self.convert_file_to_wav(src_file, dst_file)

    def create_path_file(self, file_name, data):
        header = ['chunk_name', 'path']
        with open(file_name, 'w', encoding='UTF8') as f:
            f.truncate()
            writer = csv.writer(f)
            writer.writerow(header)
            for a in data:
                writer.writerow(a)

    def process_audio(self, file_name, src_path, folder_dst):
        myaudio = AudioSegment.from_file(src_path, "wav") 
        chunks = make_chunks(myaudio, self.chunk_length_ms)
        file_name_refactor = file_name.replace('.wav','')
        data = []
        for i, chunk in enumerate(chunks):
            chunk_name = f'{folder_dst}/{file_name_refactor}_{i}.wav'
            chunk.export(chunk_name, format="wav")
            data_chunk = [f'{file_name_refactor}_{i}.wav', chunk_name]
            data.append(data_chunk)
        self.create_path_file(f'{folder_dst}/{file_name_refactor}.csv', data)

    def split_all_audio_to_frame(self):
        all_file_names = os.listdir(self.dst_wav)
        for each_file in all_file_names:
            if ('.wav' in each_file):
                file_name = each_file.replace('.wav','') + "_split"
                chunk_length_ms = 5000
                new_dst_folder = self.dst_chunk + '/' + file_name
                if os.path.exists(new_dst_folder) is False:
                    os.makedirs(new_dst_folder)
                self.process_audio(each_file, self.dst_wav + '/' + each_file, new_dst_folder)


if __name__ == '__main__':

    convert_split = ConvertSplitAudio(src,dst_wav, dst_chunk, 5000)
    print("Please wait.....")
    convert_split.conver_file_folder_to_wav()
    convert_split.split_all_audio_to_frame()
    print("Completed")

