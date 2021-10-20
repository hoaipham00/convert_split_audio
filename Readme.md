Requiriment: please install lib packages on pip3 

    ffmpeg
    
    termcolor
    
    magic
    
    AudioSegment
    
    csv
    
    audioread
    
    mutagen
    
    gsutil command line
    
    flask
    
    google.cloud 
    
    tinydb

To run: python3 audio_crud.py

Overview:

Purpose: Convert all type audio to audio.wav and split all file.wav into chunk, which has duration 5 seconds

Problem: 
    
    + When handling to convert all audios which have long durations, it means you cannot read it and process them like normal cause of limitation of RAM, CPU...
    
    + When I test, I realise almost libs processing good with audios which have shorter than 20 minutes.
    
    + Cannot manipulate data directly on gcs like update or edit audio

Solutions:
    
    - 1. Read streaming: ffmge.
    
        + Pros: Fast
        
        + Cons: only use with basic features, cannot use some advanced parameters to control expect output.
    
    - 2. To fix cons of method (1): use AudioSegment or Librosa
    
=> So, when processing with audios which have duration shorter than 20m, I use libs like: AudioSegment. 

On other hand, I use method (1) for large audio and split them into segments which have duration=20m and continue to handle follow (2)
    
