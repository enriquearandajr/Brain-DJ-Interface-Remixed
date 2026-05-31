# src :
Main folder containing DB-BMI.py, pieeg_lsl_helper.py, and pieeg_lsl_streamer.py

## DB-BMI.py : 
Python script built by PscyhoPy Builder that runs the stimulus we want to present to the participants
- Will run on laptop
- Changes made:
  - Global 60 second baseline
  - 10 second pre song baseline
  - Uses helper functions from pieeg_lsl_helper.py to facilitate EEG recording
  
## pieeg_lsl_streamer.py :
Python script that reads 16-channel EEG data from a PiEEG board using SPI and broadcasting it as an LSL stream.
- Will run on Raspberry Pi
- Uploaded on Raspberry Pi server

## pieeg_lsl_helper.py :
Python script that provides helper functions for both DB-BMI.py and pieeg_lsl_streamer.py to facilitate communication
- Also uploaded on Raspberry Pi server
- Allows DB-BMI.py to present stimulus while letting pieeg_lsl_streamer.py to record EEG data
- Accessed by DB-BMI.py and pieeg_lsl_streamer.py

