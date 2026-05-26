#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --- Import packages ---
from psychopy import locale_setup, prefs, plugins
plugins.activatePlugins()
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (
    NOT_STARTED, STARTED, PLAYING, PAUSED, STOPPED, STOPPING, FINISHED, PRESSED, 
    RELEASED, FOREVER, priority
)

import numpy as np 
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os 
import sys 

from psychopy.hardware import keyboard

# ==============================================================================
# --- NEW ARCHITECTURE: LSL Helper Imports ---
# ==============================================================================
try:
    from pieeg_lsl_helper import PiEEGRecorder, write_eeg_csv
except ImportError:
    print("\n[!] ERROR: pieeg_lsl_helper.py not found in this directory. LSL will not work.\n")
    core.quit()

# Initialize the LSL Recorder Object (Handles all hardware abstraction)
pieeg_recorder = PiEEGRecorder(stream_name="PiEEG")

# --- Setup global variables ---
deviceManager = hardware.DeviceManager()
_thisDir = os.path.dirname(os.path.abspath(__file__))
psychopyVersion = '2026.1.3'
expName = 'DB-BMI' 
expVersion = ''
runAtExit = []

expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'session': '001',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'expVersion|hid': expVersion,
    'psychopyVersion|hid': psychopyVersion,
}

PILOTING = core.setPilotModeFromArgs()
_fullScr = True
_winSize = (1024, 768)

if PILOTING:
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        _winSize = prefs.piloting['forcedWindowSize']
    if prefs.piloting['replaceParticipantID']:
        expInfo['participant'] = 'pilot'

def showExpInfoDlg(expInfo):
    dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True)
    if dlg.OK == False:
        core.quit()  
    return expInfo

def setupData(expInfo, dataDir=None):
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    if dataDir is None:
        dataDir = _thisDir
    filename = u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])
    
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    thisExp = data.ExperimentHandler(
        name=expName, version=expVersion,
        extraInfo=expInfo, runtimeInfo=None,
        originPath=_thisDir,
        savePickle=True, saveWideText=True,
        dataFileName=dataDir + os.sep + filename, sortColumns='time'
    )
    thisExp.addData('piloting', PILOTING, priority=priority.LOW)
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    return thisExp

def setupLogging(filename):
    if PILOTING:
        logging.console.setLevel(prefs.piloting['pilotConsoleLoggingLevel'])
    else:
        logging.console.setLevel('warning')
    logFile = logging.LogFile(filename+'.log')
    if PILOTING:
        logFile.setLevel(prefs.piloting['pilotLoggingLevel'])
    else:
        logFile.setLevel(logging.getLevel('info'))
    return logFile

def setupWindow(expInfo=None, win=None):
    if PILOTING:
        logging.debug('Fullscreen settings ignored as running in pilot mode.')
    
    if win is None:
        win = visual.Window(
            size=_winSize, fullscr=_fullScr, screen=0,
            winType='pyglet', allowGUI=False, allowStencil=False,
            monitor='testMonitor', color=(-1.0000, -1.0000, -1.0000), colorSpace='rgb',
            backgroundImage='', backgroundFit='none',
            blendMode='avg', useFBO=True,
            units='height',
            checkTiming=False 
        )
    else:
        win.color = (-1.0000, -1.0000, -1.0000)
        win.colorSpace = 'rgb'
        win.backgroundImage = ''
        win.backgroundFit = 'none'
        win.units = 'height'
    if expInfo is not None:
        # ==============================================================================
        # ANTI-HANG FIX: Hardcode 60FPS to prevent PsychoPy from freezing on load
        # ==============================================================================
        win._monitorFrameRate = 60.0  
        expInfo['frameRate'] = 60.0
    win.hideMessage()
    if PILOTING:
        if prefs.piloting['showPilotingIndicator']:
            win.showPilotingIndicator()
        if prefs.piloting['forceMouseVisible']:
            win.mouseVisible = True
    return win

def setupDevices(expInfo, thisExp, win):
    ioConfig = {}
    ioSession = ioServer = eyetracker = None
    deviceManager.ioServer = ioServer
    if deviceManager.getDevice('defaultKeyboard') is None:
        deviceManager.addDevice(deviceClass='keyboard', deviceName='defaultKeyboard', backend='ptb')
    return True

def pauseExperiment(thisExp, win=None, timers=[], currentRoutine=None):
    if thisExp.status != PAUSED:
        return
    pauseTimer = core.Clock()
    if currentRoutine is not None:
        for comp in currentRoutine.getPlaybackComponents():
            comp.pause()
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        defaultKeyboard = deviceManager.addKeyboard(deviceClass='keyboard', deviceName='defaultKeyboard', backend='PsychToolbox')
    while thisExp.status == PAUSED:
        if defaultKeyboard.getKeys(keyList=['escape']):
            endExperiment(thisExp, win=win)
        if currentRoutine is not None:
            for comp in currentRoutine.getDispatchComponents():
                comp.device.dispatchMessages()
        clock.time.sleep(0.001)
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    if currentRoutine is not None:
        for comp in currentRoutine.getPlaybackComponents():
            comp.play()
    for timer in timers:
        timer.addTime(-pauseTimer.getTime())

def run(expInfo, thisExp, win, globalClock=None, thisSession=None):
    thisExp.status = STARTED
    expInfo['date'] = data.getDateStr()
    expInfo['expName'] = expName
    expInfo['expVersion'] = expVersion
    expInfo['psychopyVersion'] = psychopyVersion
    win.winHandle.activate()
    exec = environmenttools.setExecEnvironment(globals())
    ioServer = deviceManager.ioServer
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        deviceManager.addDevice(deviceClass='keyboard', deviceName='defaultKeyboard', backend='PsychToolbox')
    eyetracker = deviceManager.getDevice('eyetracker')
    os.chdir(_thisDir)
    filename = thisExp.dataFileName
    frameTolerance = 0.001 
    endExpNow = False 
    
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0 
    
    # --- Initialize components for Routine "Welcome" ---
    instructionsText = visual.TextStim(win=win, name='instructionsText',
        text='You will close your eyes first to record a 60-second resting baseline. \n\nA beep will play after 60 seconds signalling to open your eyes.\n\nThen, you will close your eyes and listen to a song\n\nAfter the song, a beep will play signalling to open your eyes.\n\nYou will then answer a few questions\n\n\n',
        font='Arial', pos=(0, 0), draggable=False, height=0.05, color=(1.0, 1.0, 1.0), depth=0.0)
    welcomeText = visual.TextStim(win=win, name='welcomeText',
        text='Welcome to Decoded Brain Brain-Music-Interface\n',
        font='Arial', pos=(0, 0), draggable=False, height=0.05, color='white', depth=-1.0)
    
    counter = 0
    summary_text = "Your Song Ratings:\n\n"
    
    # --- Initialize components for Routine "Baseline_60s" ---
    BaselineText = visual.TextStim(win=win, name='BaselineText',
        text='                    ** IMPORTANT **\n\nWe will now record a 60-second resting baseline.\n\nPlease close your eyes, relax your jaw, and sit as still as possible. \n\nA beep will play signalling to open your eyes.',
        font='Arial', pos=(0, 0), draggable=False, height=0.05, color='white', depth=0.0)
    
    # --- Initialize components for Routine "ReadyForMusic" ---
    ReadyText = visual.TextStim(win=win, name='ReadyText',
        text='You are now ready to start listening to music!',
        font='Arial', pos=(0, 0), draggable=False, height=0.05, color='white', depth=0.0)
    
    sound.Sound.backend = 'ptb'
    baselineBeep = sound.Sound('A', secs=1.0, stereo=True, hamming=True, name='baselineBeep')
    baselineBeep.setVolume(1.0)

    # --- Initialize components for Routine "Baseline_10s" (Pre-Song) ---
    PreSongBaselineText = visual.TextStim(win=win, name='PreSongBaselineText',
        text='Recording 10-second resting baseline...\n\nPlease close your eyes and remain still.',
        font='Arial', pos=(0, 0), height=0.05, color='white', depth=0.0)
    
    # --- Initialize components for Routine "CloseEyes_Song" ---
    CloseEyesText = visual.TextStim(win=win, name='CloseEyesText', text='', font='Arial', pos=(0, 0), height=0.05, color='white', depth=-1.0)
    song_played = sound.Sound('A', secs=-1, stereo=True, hamming=True, name='song_played')
    song_played.setVolume(1.0)
    
    # --- Initialize components for Routine "BeepRoutine" ---
    beep = sound.Sound('A', secs=1.0, stereo=True, hamming=True, name='beep')
    beep.setVolume(1.0)
    
    # --- Initialize Questions ---
    ExcitementText = visual.TextStim(win=win, name='ExcitementText',
        text='Rate your level of agreement with each statement:\n\nI felt excited listening to this song.\n\nStrongly Disagree (1), Disagree (2),\nSomewhat Disagree (3), Neutral (4), \nSomewhat Agree (5), Agree (6), Strongly Agree (7)\n',
        font='Arial', pos=(0, 0), height=0.05, color='white')
    ExcitementInput = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    AbsorptionText = visual.TextStim(win=win, name='AbsorptionText',
        text='Rate your level of agreement with each statement:\n\nI became absorbed listening to this song.\n\nStrongly Disagree (1), Disagree (2),\nSomewhat Disagree (3), Neutral (4), \nSomewhat Agree (5), Agree (6), Strongly Agree (7)\n',
        font='Arial', pos=(0, 0), height=0.05, color='white')
    AbsorptionInput = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    ArousalText = visual.TextStim(win=win, name='ArousalText',
        text='Rate your level of agreement with each statement:\n\nI am currently aroused after listening to this song.\n\nStrongly Disagree (1), Disagree (2),\nSomewhat Disagree (3), Neutral (4), \nSomewhat Agree (5), Agree (6), Strongly Agree (7)\n',
        font='Arial', pos=(0, 0), height=0.05, color='white')
    ArousalInput = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    ValenceText = visual.TextStim(win=win, name='ValenceText',
        text='Rate your level of agreement with each statement:\n\nI am currently in a comfortable state. \n\nStrongly Disagree (1), Disagree (2),\nSomewhat Disagree (3), Neutral (4), \nSomewhat Agree (5), Agree (6), Strongly Agree (7)\n',
        font='Arial', pos=(0, 0), height=0.05, color='white')
    ValenceInput = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    PreferenceText = visual.TextStim(win=win, name='PreferenceText',
        text='Rate your level of agreement with each statement:\n\nI prefer this song.\n\nStrongly Disagree (1), Disagree (2),\nSomewhat Disagree (3), Neutral (4), \nSomewhat Agree (5), Agree (6), Strongly Agree (7)\n',
        font='Arial', pos=(0, 0), height=0.05, color='white')
    PreferenceInput = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    LifePurposeText = visual.TextStim(win=win, name='LifePurposeText',
        text='Rate your level of agreement with each statement:\n\nListening to this song helped me feel more connected to the purpose and meaning of life. \n\nStrongly Disagree (1), Disagree (2),\nSomewhat Disagree (3), Neutral (4), \nSomewhat Agree (5), Agree (6), Strongly Agree (7)\n',
        font='Arial', pos=(0, 0), height=0.05, color='white')
    LifePurposeInput = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    ReducingStressText = visual.TextStim(win=win, name='ReducingStressText',
        text='Rate your level of agreement with each statement:\n\nListening to this song helped me feel less stressed and more relaxed.\n\nStrongly Disagree (1), Disagree (2),\nSomewhat Disagree (3), Neutral (4), \nSomewhat Agree (5), Agree (6), Strongly Agree (7)\n',
        font='Arial', pos=(0, 0), height=0.05, color='white')
    ReducingStressInput = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    PleasureText = visual.TextStim(win=win, name='PleasureText',
        text='Rate your level of agreement with each statement:\n\nI felt pleasure in the whole song.\n\nStrongly Disagree (1), Disagree (2),\nSomewhat Disagree (3), Neutral (4), \nSomewhat Agree (5), Agree (6), Strongly Agree (7)\n',
        font='Arial', pos=(0, 0), height=0.05, color='white')
    PleasureInput = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    # --- Initialize components for Routine "ThankYou" ---
    ThankYouText = visual.TextStim(win=win, name='ThankYouText', text='Thank you for listening\n\nPlease come back soon!', font='Arial', pos=(0, 0), height=0.05, color='white')
    Summary = visual.TextStim(win=win, name='Summary', text='', font='Arial', pos=(0, 0), height=0.05, color='white', depth=-1.0)
    
    if globalClock is None:
        globalClock = core.Clock()
    if isinstance(globalClock, str):
        if globalClock == 'float':
            globalClock = core.Clock(format='float')
        elif globalClock == 'iso':
            globalClock = core.Clock(format='%Y-%m-%d_%H:%M:%S.%f%z')
        else:
            globalClock = core.Clock(format=globalClock)
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    logging.setDefaultClock(globalClock)
    if eyetracker is not None:
        eyetracker.enableEventReporting()
    routineTimer = core.Clock()
    win.flip() 
    expInfo['expStart'] = data.getDateStr(format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6)
    
    # ==========================================================================
    # --- Run Routine "Welcome" ---
    # ==========================================================================
    Welcome = data.Routine(name='Welcome', components=[instructionsText, welcomeText])
    Welcome.status = NOT_STARTED
    continueRoutine = True
    Welcome.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Welcome.tStart = globalClock.getTime(format='float')
    Welcome.status = STARTED
    thisExp.addData('Welcome.started', Welcome.tStart)
    Welcome.maxDuration = None
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    thisExp.currentRoutine = Welcome
    Welcome.forceEnded = routineForceEnded = not continueRoutine
    
    while continueRoutine and routineTimer.getTime() < 13.0:
        t = routineTimer.getTime()
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1 
        
        if instructionsText.status == NOT_STARTED and tThisFlipGlobal >= 3-frameTolerance:
            instructionsText.status = STARTED
            instructionsText.setAutoDraw(True)
        if instructionsText.status == STARTED and tThisFlipGlobal > instructionsText.tStartRefresh + 10.0-frameTolerance:
            instructionsText.status = FINISHED
            instructionsText.setAutoDraw(False)
            
        if welcomeText.status == NOT_STARTED and tThisFlipGlobal >= 0.0-frameTolerance:
            welcomeText.status = STARTED
            welcomeText.setAutoDraw(True)
        if welcomeText.status == STARTED and tThisFlipGlobal > welcomeText.tStartRefresh + 3.0-frameTolerance:
            welcomeText.status = FINISHED
            welcomeText.setAutoDraw(False)
            
        if defaultKeyboard.getKeys(keyList=["escape"]):
            endExperiment(thisExp, win=win)
            return
            
        continueRoutine = False
        for comp in Welcome.components:
            if hasattr(comp, "status") and comp.status != FINISHED:
                continueRoutine = True
                break
        if continueRoutine:
            win.flip()
            
    for comp in Welcome.components:
        if hasattr(comp, "setAutoDraw"):
            comp.setAutoDraw(False)
    routineTimer.addTime(-13.000000)
    thisExp.nextEntry()
    
    # ==========================================================================
    # --- NEW ROUTINE: 60-Second Resting Baseline ---
    # ==========================================================================
    Baseline = data.Routine(name='Baseline', components=[BaselineText])
    Baseline.status = NOT_STARTED
    continueRoutine = True
    
    # 1. Start the LSL Stream Recorder
    pieeg_recorder.start_trial()
    
    Baseline.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Baseline.tStart = globalClock.getTime(format='float')
    Baseline.status = STARTED
    thisExp.addData('Baseline.started', Baseline.tStart)
    t = 0
    frameN = -1
    thisExp.currentRoutine = Baseline
    
    while continueRoutine and routineTimer.getTime() < 60.0:
        t = routineTimer.getTime()
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1 
        
        if BaselineText.status == NOT_STARTED and tThisFlipGlobal >= 0.0-frameTolerance:
            BaselineText.status = STARTED
            BaselineText.setAutoDraw(True)
        if BaselineText.status == STARTED and tThisFlipGlobal > BaselineText.tStartRefresh + 60.0-frameTolerance:
            BaselineText.status = FINISHED
            BaselineText.setAutoDraw(False)
            
        if defaultKeyboard.getKeys(keyList=["escape"]):
            endExperiment(thisExp, win=win)
            return
            
        continueRoutine = False
        for comp in Baseline.components:
            if hasattr(comp, "status") and comp.status != FINISHED:
                continueRoutine = True
                break
        if continueRoutine:
            win.flip()
            
    for comp in Baseline.components:
        if hasattr(comp, "setAutoDraw"):
            comp.setAutoDraw(False)
            
    # 2. Stop Recorder and Save Data
    data_to_save = pieeg_recorder.stop_trial(timeout=2.0)
    if data_to_save:
        os.makedirs('data', exist_ok=True)
        baseline_filename = os.path.join('data', f"{expInfo['participant']}_{expName}_60s_baseline_eeg.csv")
        write_eeg_csv(baseline_filename, data_to_save)
        thisExp.addData('baseline_60s_file', baseline_filename)
        thisExp.addData('baseline_60s_samples', len(data_to_save))
    else:
        thisExp.addData('baseline_60s_file', 'NO_DATA')
        
    routineTimer.addTime(-60.000000)
    thisExp.nextEntry()
    
    # ==========================================================================
    # --- Run Routine "ReadyForMusic" ---
    # ==========================================================================
    ReadyForMusic = data.Routine(name='ReadyForMusic', components=[ReadyText, baselineBeep])
    ReadyForMusic.status = NOT_STARTED
    continueRoutine = True
    baselineBeep.setSound('beep-09.mp3', secs=1.0, hamming=True)
    baselineBeep.setVolume(1.0, log=False)
    baselineBeep.seek(0)
    ReadyForMusic.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    ReadyForMusic.tStart = globalClock.getTime(format='float')
    ReadyForMusic.status = STARTED
    t = 0
    frameN = -1
    thisExp.currentRoutine = ReadyForMusic
    
    while continueRoutine and routineTimer.getTime() < 5.0:
        t = routineTimer.getTime()
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1 
        
        if ReadyText.status == NOT_STARTED and tThisFlipGlobal >= 1.0-frameTolerance:
            ReadyText.status = STARTED
            ReadyText.setAutoDraw(True)
        if ReadyText.status == STARTED and tThisFlipGlobal > ReadyText.tStartRefresh + 4.0-frameTolerance:
            ReadyText.status = FINISHED
            ReadyText.setAutoDraw(False)
            
        if baselineBeep.status == NOT_STARTED and tThisFlipGlobal >= 0-frameTolerance:
            baselineBeep.status = STARTED
            baselineBeep.play(when=win)
        if baselineBeep.status == STARTED and (tThisFlipGlobal > baselineBeep.tStartRefresh + 1.0-frameTolerance or baselineBeep.isFinished):
            baselineBeep.status = FINISHED
            baselineBeep.stop()
            
        if defaultKeyboard.getKeys(keyList=["escape"]):
            endExperiment(thisExp, win=win)
            return
            
        continueRoutine = False
        for comp in ReadyForMusic.components:
            if hasattr(comp, "status") and comp.status != FINISHED:
                continueRoutine = True
                break
        if continueRoutine:
            win.flip()
            
    for comp in ReadyForMusic.components:
        if hasattr(comp, "setAutoDraw"):
            comp.setAutoDraw(False)
    baselineBeep.pause()
    routineTimer.addTime(-5.000000)
    thisExp.nextEntry()
    
    # ==========================================================================
    # --- TRIAL LOOP START (5 Songs) ---
    # ==========================================================================
    trials = data.TrialHandler2(
        name='trials', nReps=1, method='random', extraInfo=expInfo, originPath=-1, 
        trialList=data.importConditions('dur_song_diversity_100.csv - Sheet1.csv', selection=np.random.choice(100, 5, replace=False)), 
        seed=None, isTrials=True,
    )
    thisExp.addLoop(trials)
    
    for thisTrial in trials:
        trials.status = STARTED
        if hasattr(thisTrial, 'status'):
            thisTrial.status = STARTED
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        
        if thisTrial != None:
            for paramName in thisTrial:
                globals()[paramName] = thisTrial[paramName]
                
        # ======================================================================
        # --- NEW ROUTINE: 10-Second Pre-Song Baseline ---
        # ======================================================================
        counter += 1
        PreSongBaselineText.setText(f'Song {counter}/5\n\nRecording 10-second resting baseline...\n\nPlease close your eyes and remain still.')
        Baseline_10s = data.Routine(name='Baseline_10s', components=[PreSongBaselineText])
        Baseline_10s.status = NOT_STARTED
        continueRoutine = True
        
        # 1. Start the LSL Stream Recorder for the 10s chunk
        pieeg_recorder.start_trial()
        
        Baseline_10s.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        Baseline_10s.tStart = globalClock.getTime(format='float')
        Baseline_10s.status = STARTED
        t = 0
        frameN = -1
        thisExp.currentRoutine = Baseline_10s
        
        while continueRoutine and routineTimer.getTime() < 10.0:
            t = routineTimer.getTime()
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1 
            
            if PreSongBaselineText.status == NOT_STARTED and tThisFlipGlobal >= 0.0-frameTolerance:
                PreSongBaselineText.status = STARTED
                PreSongBaselineText.setAutoDraw(True)
            if PreSongBaselineText.status == STARTED and tThisFlipGlobal > PreSongBaselineText.tStartRefresh + 10.0-frameTolerance:
                PreSongBaselineText.status = FINISHED
                PreSongBaselineText.setAutoDraw(False)
                
            if defaultKeyboard.getKeys(keyList=["escape"]):
                endExperiment(thisExp, win=win)
                return
                
            continueRoutine = False
            for comp in Baseline_10s.components:
                if hasattr(comp, "status") and comp.status != FINISHED:
                    continueRoutine = True
                    break
            if continueRoutine:
                win.flip()
                
        for comp in Baseline_10s.components:
            if hasattr(comp, "setAutoDraw"):
                comp.setAutoDraw(False)
                
        # 2. Stop 10s Recorder and Save Data
        data_to_save_10s = pieeg_recorder.stop_trial(timeout=2.0)
        if data_to_save_10s:
            os.makedirs('data', exist_ok=True)
            b10_filename = os.path.join('data', f"{expInfo['participant']}_{expName}_trial{trials.thisN}_10s_baseline.csv")
            write_eeg_csv(b10_filename, data_to_save_10s)
            thisExp.addData('baseline_10s_file', b10_filename)
        else:
            thisExp.addData('baseline_10s_file', 'NO_DATA')
            
        routineTimer.addTime(-10.000000)

        # ======================================================================
        # --- Run Routine "CloseEyes_Song" ---
        # ======================================================================
        CloseEyes_Song = data.Routine(name='CloseEyes_Song', components=[CloseEyesText, song_played])
        CloseEyes_Song.status = NOT_STARTED
        continueRoutine = True
        
        # Start LSL Stream Recorder for the actual song
        pieeg_recorder.start_trial()
        
        CloseEyesText.setText('Please close your eyes\n\nThe song will begin to play shortly\n')
        song_played.setSound(filePath, secs=93, hamming=True)
        song_played.setVolume(1.0, log=False)
        song_played.seek(0)
        
        CloseEyes_Song.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        CloseEyes_Song.tStart = globalClock.getTime(format='float')
        CloseEyes_Song.status = STARTED
        t = 0
        frameN = -1
        thisExp.currentRoutine = CloseEyes_Song
        
        while continueRoutine and routineTimer.getTime() < 96.0:
            t = routineTimer.getTime()
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1 
            
            if CloseEyesText.status == NOT_STARTED and tThisFlipGlobal >= 0.0-frameTolerance:
                CloseEyesText.status = STARTED
                CloseEyesText.setAutoDraw(True)
            if CloseEyesText.status == STARTED and tThisFlipGlobal > CloseEyesText.tStartRefresh + 3.0-frameTolerance:
                CloseEyesText.status = FINISHED
                CloseEyesText.setAutoDraw(False)
                
            if song_played.status == NOT_STARTED and tThisFlipGlobal >= 3-frameTolerance:
                song_played.status = STARTED
                song_played.play(when=win) 
            if song_played.status == STARTED and (tThisFlipGlobal > song_played.tStartRefresh + 93-frameTolerance or song_played.isFinished):
                song_played.status = FINISHED
                song_played.stop()
                
            if defaultKeyboard.getKeys(keyList=["escape"]):
                endExperiment(thisExp, win=win)
                return
                
            continueRoutine = False
            for comp in CloseEyes_Song.components:
                if hasattr(comp, "status") and comp.status != FINISHED:
                    continueRoutine = True
                    break
            if continueRoutine:
                win.flip()
                
        for comp in CloseEyes_Song.components:
            if hasattr(comp, "setAutoDraw"):
                comp.setAutoDraw(False)
        song_played.pause() 
        
        # Stop LSL Stream Recorder and Save Song Data
        song_data = pieeg_recorder.stop_trial(timeout=2.0)
        if song_data:
            os.makedirs('data', exist_ok=True)
            song_basename = os.path.splitext(os.path.basename(filePath))[0]
            eeg_filename = os.path.join('data', f"{expInfo['participant']}_{expName}_trial{trials.thisN}_{song_basename}_eeg.csv")
            write_eeg_csv(eeg_filename, song_data)
            thisExp.addData('eeg_file', eeg_filename)
            thisExp.addData('eeg_samples', len(song_data))
        else:
            thisExp.addData('eeg_file', 'NO_DATA')
            
        routineTimer.addTime(-96.000000)
        
        # ======================================================================
        # --- Run Routine "BeepRoutine" ---
        # ======================================================================
        BeepRoutine = data.Routine(name='BeepRoutine', components=[beep])
        BeepRoutine.status = NOT_STARTED
        continueRoutine = True
        beep.setSound('beep-09.mp3', secs=1.0, hamming=True)
        beep.setVolume(1.0, log=False)
        beep.seek(0)
        BeepRoutine.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        BeepRoutine.tStart = globalClock.getTime(format='float')
        BeepRoutine.status = STARTED
        t = 0
        frameN = -1
        thisExp.currentRoutine = BeepRoutine
        
        while continueRoutine and routineTimer.getTime() < 1.0:
            t = routineTimer.getTime()
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1 
            
            if beep.status == NOT_STARTED and tThisFlipGlobal >= 0.0-frameTolerance:
                beep.status = STARTED
                beep.play(when=win)
            if beep.status == STARTED and (tThisFlipGlobal > beep.tStartRefresh + 1.0-frameTolerance or beep.isFinished):
                beep.status = FINISHED
                beep.stop()
                
            if defaultKeyboard.getKeys(keyList=["escape"]):
                endExperiment(thisExp, win=win)
                return
                
            continueRoutine = False
            for comp in BeepRoutine.components:
                if hasattr(comp, "status") and comp.status != FINISHED:
                    continueRoutine = True
                    break
            if continueRoutine:
                win.flip()
                
        for comp in BeepRoutine.components:
            if hasattr(comp, "setAutoDraw"):
                comp.setAutoDraw(False)
        beep.pause()
        routineTimer.addTime(-1.000000)
        
        # ======================================================================
        # --- QUESTION BLOCK (8 Questions) ---
        # ======================================================================
        questions = [
            ("ExcitementQuestion", ExcitementText, ExcitementInput),
            ("AbsorptionQuestion", AbsorptionText, AbsorptionInput),
            ("ArousalQuestion", ArousalText, ArousalInput),
            ("ValenceQuestion", ValenceText, ValenceInput),
            ("PreferenceQuestion", PreferenceText, PreferenceInput),
            ("LifePurposeQuestion", LifePurposeText, LifePurposeInput),
            ("ReducingStressQuestion", ReducingStressText, ReducingStressInput),
            ("PleasureQuestion", PleasureText, PleasureInput)
        ]
        
        for q_name, q_text, q_input in questions:
            Q_Routine = data.Routine(name=q_name, components=[q_text, q_input])
            Q_Routine.status = NOT_STARTED
            continueRoutine = True
            
            q_input.keys = []
            q_input.rt = []
            _allKeys = []
            
            Q_Routine.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            Q_Routine.tStart = globalClock.getTime(format='float')
            Q_Routine.status = STARTED
            t = 0
            frameN = -1
            thisExp.currentRoutine = Q_Routine
            
            while continueRoutine:
                t = routineTimer.getTime()
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1 
                
                if q_text.status == NOT_STARTED and tThisFlipGlobal >= 0.0-frameTolerance:
                    q_text.status = STARTED
                    q_text.setAutoDraw(True)
                
                waitOnFlip = False
                if q_input.status == NOT_STARTED and tThisFlipGlobal >= 0.0-frameTolerance:
                    q_input.status = STARTED
                    waitOnFlip = True
                    win.callOnFlip(q_input.clock.reset) 
                    win.callOnFlip(q_input.clearEvents, eventType='keyboard')
                
                if q_input.status == STARTED and not waitOnFlip:
                    theseKeys = q_input.getKeys(keyList=['1','2','3','4','5','6','7'], ignoreKeys=["escape"], waitRelease=False)
                    _allKeys.extend(theseKeys)
                    if len(_allKeys):
                        q_input.keys = _allKeys[-1].name  
                        q_input.rt = _allKeys[-1].rt
                        q_input.duration = _allKeys[-1].duration
                        continueRoutine = False
                
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    endExperiment(thisExp, win=win)
                    return
                
                continueRoutine_check = False
                for comp in Q_Routine.components:
                    if hasattr(comp, "status") and comp.status != FINISHED:
                        continueRoutine_check = True
                        break
                if not continueRoutine: 
                    continueRoutine_check = False
                continueRoutine = continueRoutine_check
                
                if continueRoutine:
                    win.flip()
                    
            for comp in Q_Routine.components:
                if hasattr(comp, "setAutoDraw"):
                    comp.setAutoDraw(False)
            
            if q_input.keys in ['', [], None]:  
                q_input.keys = None
            trials.addData(f'{q_input.name}.keys', q_input.keys)
            if q_input.keys != None:  
                trials.addData(f'{q_input.name}.rt', q_input.rt)
                trials.addData(f'{q_input.name}.duration', q_input.duration)
            routineTimer.reset()
            
            # If it is the final question (Pleasure), log it to the summary screen
            if q_name == "PleasureQuestion":
                rating = q_input.keys if q_input.keys else "None"
                summary_text += f"{song} -- Pleasure Rating: {rating}\n"

        if hasattr(thisTrial, 'status'):
            thisTrial.status = FINISHED
        thisExp.nextEntry()
        
    trials.status = FINISHED
    
    # ==========================================================================
    # --- Run Routine "ThankYou" ---
    # ==========================================================================
    ThankYou = data.Routine(name='ThankYou', components=[ThankYouText, Summary])
    ThankYou.status = NOT_STARTED
    continueRoutine = True
    Summary.setText(summary_text)
    ThankYou.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    ThankYou.tStart = globalClock.getTime(format='float')
    ThankYou.status = STARTED
    t = 0
    frameN = -1
    thisExp.currentRoutine = ThankYou
    
    while continueRoutine and routineTimer.getTime() < 13.0:
        t = routineTimer.getTime()
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1 
        
        if ThankYouText.status == NOT_STARTED and tThisFlipGlobal >= 5-frameTolerance:
            ThankYouText.status = STARTED
            ThankYouText.setAutoDraw(True)
        if ThankYouText.status == STARTED and tThisFlipGlobal > ThankYouText.tStartRefresh + 8-frameTolerance:
            ThankYouText.status = FINISHED
            ThankYouText.setAutoDraw(False)
            
        if Summary.status == NOT_STARTED and tThisFlipGlobal >= 0.0-frameTolerance:
            Summary.status = STARTED
            Summary.setAutoDraw(True)
        if Summary.status == STARTED and tThisFlipGlobal > Summary.tStartRefresh + 5-frameTolerance:
            Summary.status = FINISHED
            Summary.setAutoDraw(False)
            
        if defaultKeyboard.getKeys(keyList=["escape"]):
            endExperiment(thisExp, win=win)
            return
            
        continueRoutine = False
        for comp in ThankYou.components:
            if hasattr(comp, "status") and comp.status != FINISHED:
                continueRoutine = True
                break
        if continueRoutine:
            win.flip()
            
    for comp in ThankYou.components:
        if hasattr(comp, "setAutoDraw"):
            comp.setAutoDraw(False)
            
    routineTimer.addTime(-13.000000)
    thisExp.nextEntry()
    endExperiment(thisExp, win=win)

def saveData(thisExp):
    filename = thisExp.dataFileName
    thisExp.saveAsWideText(filename + '.csv', delim='auto')
    thisExp.saveAsPickle(filename)

def endExperiment(thisExp, win=None):
    if thisExp.currentRoutine is not None:
        for comp in thisExp.currentRoutine.getPlaybackComponents():
            comp.stop()
    if win is not None:
        win.clearAutoDraw()
        win.flip()
    logging.console.setLevel(logging.WARNING)
    thisExp.status = FINISHED
    for fcn in runAtExit:
        fcn()
    logging.flush()

def quit(thisExp, win=None, thisSession=None):
    thisExp.abort()  
    if win is not None:
        win.flip()
        win.close()
    logging.flush()
    if thisSession is not None:
        thisSession.stop()
    core.quit()

if __name__ == '__main__':
    expInfo = showExpInfoDlg(expInfo=expInfo)
    thisExp = setupData(expInfo=expInfo)
    logFile = setupLogging(filename=thisExp.dataFileName)
    win = setupWindow(expInfo=expInfo)
    setupDevices(expInfo=expInfo, thisExp=thisExp, win=win)
    run(expInfo=expInfo, thisExp=thisExp, win=win, globalClock='float')
    saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)
