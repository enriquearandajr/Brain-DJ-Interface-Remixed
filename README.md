# BDJI Directory

## Open Labs Page:

https://www.notion.so/decoded-brain/Brain-DJ-Interface-BDJI-32be37a75f4180ffaac9fbb3034954ab?source=copy_link

## Demo: 

Instructions:

https://github.com/user-attachments/assets/de8a0860-95b7-4a5b-928a-16add1a49089

Summary:

<img width="521" height="259" alt="Screenshot 2026-05-13 at 10 37 40 PM" src="https://github.com/user-attachments/assets/aa5c89f6-03d1-4b76-8fa5-864f38743b85" />


## DB-BMI.py: 
Python script built by PscyhoPy Builder that runs the stimulus we want to present to the participants

## pieeg_lsl_streamer.py:
Python script that reads 16-channel EEG data from a PiEEG board using SPI and broadcasting it as an LSL stream.

## pieeg_lsl_helper.py:
Python script that provides helper functions for both DB-BMI.py and pieeg_lsl_streamer.py

## data_filtering.ipynb:
Python notebook with current filtering methods using test data from our unofficial EEG data

To-Do: review filtering/preprocessing methods

## diversify_playlist.ipynb:
Abe's VGGish model that takes the top 100 songs from the last 10 years and makes a playlist of the most diverse 100 songs

To-Do: review how it works and what it's doing

## dur_song_diversity_100.csv
Spreadsheet of song names, relative file path of mp3 songs in my (Enrique's) computer, and the duration of each songs (currently not in use)

## data (folder)
Contains the unofficial recording sessions. 

To-Do: Test our filtering/preprocessing methods and test the quality of EEG data we get from the dry electrode piEEG caps.

# References:

[1] Blood, A. J., & Zatorre, R. J. (2001). Intensely pleasurable responses to music correlate with activity in brain regions implicated in reward and emotion. Proceedings of the National Academy of Sciences of the United States of America, 98(20), 11818–11823. https://doi.org/10.1073/pnas.191355898

[2] Hadjidimitriou, Stelios K., and Leontios J. Hadjileontiadis. “Toward an EEG-Based Recognition of Music Liking Using Time-Frequency Analysis.” IEEE Transactions on Biomedical Engineering 59, no. 12 (2012): 3498–510. https://doi.org/10.1109/TBME.2012.2217495.

[3] Kondoh, S., Etani, T., Sakakibara, Y., Naruse, Y., Imamura, Y., Ibaraki, T., & Fujii, S. (2024). A chill brain-music interface for enhancing music chills with personalized playlists. Neuroscience. https://doi.org/10.1101/2024.11.07.621657

[4] Mendivil Sauceda, Jesus Arturo, Bogart Yail Marquez, and José Jaime Esqueda Elizondo. “Emotion Classification from Electroencephalographic Signals Using Machine Learning.” Brain Sciences 14, no. 12 (2024): 1211. https://doi.org/10.3390/brainsci14121211.

