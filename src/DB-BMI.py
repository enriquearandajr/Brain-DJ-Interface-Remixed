#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2026.1.3),
    on Wed May 13 17:02:38 2026
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import plugins
plugins.activatePlugins()
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (
    NOT_STARTED, STARTED, PLAYING, PAUSED, STOPPED, STOPPING, FINISHED, PRESSED, 
    RELEASED, FOREVER, priority
)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

from psychopy.hardware import keyboard

# Run 'Before Experiment' code from pieegRecord
from pieeg_lsl_helper import PiEEGRecorder, sanitize_filename_component, write_eeg_csv

pieeg_recorder = PiEEGRecorder(timestamp_fn=core.getTime)

def cleanup_hardware():
    """Stop EEG acquisition and release PiEEG/LSL resources."""
    pieeg_recorder.shutdown()

# --- Setup global variables (available in all functions) ---
deviceManager = hardware.DeviceManager()
# _thisDir = os.path.dirname(os.path.abspath(__file__))
# Now organized repo
_srcDir = os.path.dirname(os.path.abspath(__file__))
_rootDir = os.path.abspath(os.path.join(_srcDir, '..'))

_dataDir = os.path.join(_rootDir, 'data', 'raw')
_toolsDir = os.path.join(_rootDir, 'tools')

psychopyVersion = '2026.1.3'
expName = 'DB-BMI'  
expVersion = ''
runAtExit = []
runAtExit.append(cleanup_hardware)

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
    dlg = gui.DlgFromDict(
        dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True
    )
    if dlg.OK == False:
        core.quit() 
    return expInfo


def setupData(expInfo, dataDir=None):
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    if dataDir is None:
        dataDir = _dataDir
    filename = u'%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    thisExp = data.ExperimentHandler(
        name=expName, version=expVersion,
        extraInfo=expInfo, runtimeInfo=None,

        #originPath='/Users/earanda/DB-BDJI-PSYCHOPY/DB-BMI.py',
        originPath = os.path.abspath(__file__),
        savePickle=True, saveWideText=True,
        dataFileName=os.path.join(dataDir, filename), sortColumns='time'
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
        # Bypass the measurement hang and force standard 60 FPS
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
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='ptb'
        )
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
        defaultKeyboard = deviceManager.addKeyboard(
            deviceClass='keyboard',
            deviceName='defaultKeyboard',
            backend='PsychToolbox',
        )
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
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='PsychToolbox'
        )
    eyetracker = deviceManager.getDevice('eyetracker')
    os.chdir(_rootDir)
    filename = thisExp.dataFileName
    frameTolerance = 0.001 
    endExpNow = False 
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  
    
    instructionsText = visual.TextStim(win=win, name='instructionsText',
        text='You will close your eyes first to record a 60-second resting baseline. \n\nA beep will play after 60 seconds signalling to open your eyes.\n\nThen, you will close your eyes and listen to a song\n\nAfter the song, a beep will play signalling to open your eyes.\n\nYou will rate the song from 1-7.\n\n\n',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color=(1.0000, 1.0000, 1.0000), colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    welcomeText = visual.TextStim(win=win, name='welcomeText',
        text='Welcome to Decoded Brain Brain-Music-Interface\n',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    counter = 0
    summary_text = "Your Song Ratings:\n\n"

    BaselineText = visual.TextStim(win=win, name='BaselineText',
        text='** IMPORTANT **\n\nWe are recording a 60-second resting baseline.\n\nPlease close your eyes, relax your jaw, and sit as still as possible. \n\nA beep will play signalling to open your eyes.',
        font='Arial', pos=(0, 0), draggable=False, height=0.05, color='white', depth=0.0)

    ReadyText = visual.TextStim(win=win, name='ReadyText',
        text='You are now ready to start listening to music!',
        font='Arial', pos=(0, 0), draggable=False, height=0.05, color='white', depth=0.0)

    sound.Sound.backend = 'ptb'
    baselineBeep = sound.Sound('A', secs=1.0, stereo=True, hamming=True, name='baselineBeep')
    baselineBeep.setVolume(1.0)

    PreSongBaselineText = visual.TextStim(win=win, name='PreSongBaselineText',
        text='Recording 10-second resting baseline...\n\nPlease close your eyes and remain still.',
        font='Arial', pos=(0, 0), height=0.05, color='white', depth=0.0)

    CloseEyesText = visual.TextStim(win=win, name='CloseEyesText',
        text='',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    song_played = sound.Sound(
        'A', 
        secs=-1, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='song_played'
    )
    song_played.setVolume(1.0)
    counter += 1
    
    beep = sound.Sound(
        'A', 
        secs=1.0, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='beep'
    )
    beep.setVolume(1.0)
    RateSongText = visual.TextStim(win=win, name='RateSongText',
        text='Rate the song from 1 (Strongly Dislike) - 7 (Strongly Like)\n\nPress [1-7]',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    song_rating = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    FamiliarityText = visual.TextStim(win=win, name='FamiliarityText',
        text='Were you already familiar with this song? \n\nPress [y] for yes, [n] for no',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    familiarity_rating = keyboard.Keyboard(deviceName='defaultKeyboard')
    
    ThankYouText = visual.TextStim(win=win, name='ThankYouText',
        text='Thank you for listening\n\nPlease come back soon!',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    Summary = visual.TextStim(win=win, name='Summary',
        text='',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    
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
    expInfo['expStart'] = data.getDateStr(
        format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6
    )
    
    Welcome = data.Routine(
        name='Welcome',
        components=[instructionsText, welcomeText],
    )
    Welcome.status = NOT_STARTED
    continueRoutine = True
    Welcome.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Welcome.tStart = globalClock.getTime(format='float')
    Welcome.status = STARTED
    thisExp.addData('Welcome.started', Welcome.tStart)
    Welcome.maxDuration = None
    WelcomeComponents = Welcome.components
    for thisComponent in Welcome.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    thisExp.currentRoutine = Welcome
    Welcome.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 12.0:
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  
        
        if instructionsText.status == NOT_STARTED and tThisFlip >= 3-frameTolerance:
            instructionsText.frameNStart = frameN  
            instructionsText.tStart = t  
            instructionsText.tStartRefresh = tThisFlipGlobal  
            win.timeOnFlip(instructionsText, 'tStartRefresh')  
            thisExp.timestampOnFlip(win, 'instructionsText.started')
            instructionsText.status = STARTED
            instructionsText.setAutoDraw(True)
        
        if instructionsText.status == STARTED:
            pass
        
        if instructionsText.status == STARTED:
            if tThisFlipGlobal > instructionsText.tStartRefresh + 9.0-frameTolerance:
                instructionsText.tStop = t  
                instructionsText.tStopRefresh = tThisFlipGlobal  
                instructionsText.frameNStop = frameN  
                thisExp.timestampOnFlip(win, 'instructionsText.stopped')
                instructionsText.status = FINISHED
                instructionsText.setAutoDraw(False)
        
        if welcomeText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            welcomeText.frameNStart = frameN  
            welcomeText.tStart = t  
            welcomeText.tStartRefresh = tThisFlipGlobal  
            win.timeOnFlip(welcomeText, 'tStartRefresh')  
            thisExp.timestampOnFlip(win, 'welcomeText.started')
            welcomeText.status = STARTED
            welcomeText.setAutoDraw(True)
        
        if welcomeText.status == STARTED:
            pass
        
        if welcomeText.status == STARTED:
            if tThisFlipGlobal > welcomeText.tStartRefresh + 3.0-frameTolerance:
                welcomeText.tStop = t  
                welcomeText.tStopRefresh = tThisFlipGlobal  
                welcomeText.frameNStop = frameN  
                thisExp.timestampOnFlip(win, 'welcomeText.stopped')
                welcomeText.status = FINISHED
                welcomeText.setAutoDraw(False)
        
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=Welcome,
            )
            continue
        
        if not continueRoutine:
            Welcome.forceEnded = routineForceEnded = True
        if Welcome.forceEnded or routineForceEnded:
            break
        continueRoutine = False
        for thisComponent in Welcome.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  
        
        if continueRoutine:  
            win.flip()
    
    for thisComponent in Welcome.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    Welcome.tStop = globalClock.getTime(format='float')
    Welcome.tStopRefresh = tThisFlipGlobal
    thisExp.addData('Welcome.stopped', Welcome.tStop)
    if Welcome.maxDurationReached:
        routineTimer.addTime(-Welcome.maxDuration)
    elif Welcome.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-12.000000)
    thisExp.nextEntry()

    # ======================================================================
    # --- 60-Second Resting Baseline ---
    # ======================================================================
    Baseline = data.Routine(name='Baseline', components=[BaselineText])
    Baseline.status = NOT_STARTED
    continueRoutine = True

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
            BaselineText.tStartRefresh = tThisFlipGlobal
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

    data_to_save = pieeg_recorder.stop_trial(timeout=2.0)
    if data_to_save:
        os.makedirs(_dataDir, exist_ok=True)
        baseline_filename = os.path.join(_dataDir, f"{expInfo['participant']}_{expName}_60s_baseline_eeg.csv")
        write_eeg_csv(baseline_filename, data_to_save)
        thisExp.addData('baseline_60s_file', baseline_filename)
        thisExp.addData('baseline_60s_samples', len(data_to_save))
    else:
        thisExp.addData('baseline_60s_file', 'NO_DATA')
        thisExp.addData('baseline_60s_samples', 0)

    routineTimer.addTime(-60.000000)
    thisExp.nextEntry()

    # ======================================================================
    # --- Ready For Music (Beep) ---
    # ======================================================================
    ReadyForMusic = data.Routine(name='ReadyForMusic', components=[ReadyText, baselineBeep])
    ReadyForMusic.status = NOT_STARTED
    continueRoutine = True
    baselineBeep.setSound(os.path.join(_toolsDir, 'beep-09.mp3'), secs=1.0, hamming=True)
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
            ReadyText.tStartRefresh = tThisFlipGlobal
        if ReadyText.status == STARTED and tThisFlipGlobal > ReadyText.tStartRefresh + 4.0-frameTolerance:
            ReadyText.status = FINISHED
            ReadyText.setAutoDraw(False)

        if baselineBeep.status == NOT_STARTED and tThisFlipGlobal >= 0-frameTolerance:
            baselineBeep.status = STARTED
            baselineBeep.tStartRefresh = tThisFlipGlobal
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

    conditions_path = os.path.join(_toolsDir, 'dur_song_diversity_100.csv - Sheet1.csv')
    trials = data.TrialHandler2(
        name='trials',
        nReps=1, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=data.importConditions(
        conditions_path, 
        selection=np.random.choice(100, 5, replace=False)
    )
    , 
        seed=None, 
        isTrials=True, 
    )
    thisExp.addLoop(trials)  
    thisTrial = trials.trialList[0]  
    if thisTrial != None:
        for paramName in thisTrial:
            globals()[paramName] = thisTrial[paramName]
    if thisSession is not None:
        thisSession.sendExperimentData()
    
    for thisTrial in trials:
        trials.status = STARTED
        if hasattr(thisTrial, 'status'):
            thisTrial.status = STARTED
        currentLoop = trials
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            thisSession.sendExperimentData()
        if thisTrial != None:
            for paramName in thisTrial:
                globals()[paramName] = thisTrial[paramName]

        # ==================================================================
        # --- 10-Second Pre-Song Baseline ---
        # ==================================================================
        counter += 1
        PreSongBaselineText.setText(
            f'Song {counter}/5\n\nRecording 10-second resting baseline...\n\nPlease close your eyes and remain still.'
        )
        Baseline_10s = data.Routine(name='Baseline_10s', components=[PreSongBaselineText])
        Baseline_10s.status = NOT_STARTED
        continueRoutine = True

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
                PreSongBaselineText.tStartRefresh = tThisFlipGlobal
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

        data_to_save_10s = pieeg_recorder.stop_trial(timeout=2.0)
        if data_to_save_10s:
            # os.makedirs('data', exist_ok=True)
            os.makedirs(_dataDir, exist_ok=True)
            b10_filename = os.path.join(_dataDir, f"{expInfo['participant']}_{expName}_trial{trials.thisN}_10s_baseline.csv")
            write_eeg_csv(b10_filename, data_to_save_10s)
            thisExp.addData('baseline_10s_file', b10_filename)
            thisExp.addData('baseline_10s_samples', len(data_to_save_10s))
        else:
            thisExp.addData('baseline_10s_file', 'NO_DATA')
            thisExp.addData('baseline_10s_samples', 0)

        routineTimer.addTime(-10.000000)

        CloseEyes_Song = data.Routine(
            name='CloseEyes_Song',
            components=[CloseEyesText, song_played],
        )
        CloseEyes_Song.status = NOT_STARTED
        continueRoutine = True

        # Start a fresh PiEEG buffer for this song trial.
        pieeg_recorder.start_trial()

        CloseEyesText.setText('Please close your eyes\n\nThe song will begin to play shortly\n')
        full_audio_path = os.path.join(_toolsDir, filePath) # filePath is defined in the conditions CSV
        song_played.setSound(full_audio_path, secs=90, hamming=True) # filePath is defined in the conditions CSV
        song_played.setVolume(1.0, log=False)
        song_played.seek(0)
        CloseEyes_Song.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        CloseEyes_Song.tStart = globalClock.getTime(format='float')
        CloseEyes_Song.status = STARTED
        thisExp.addData('CloseEyes_Song.started', CloseEyes_Song.tStart)
        CloseEyes_Song.maxDuration = None
        CloseEyes_SongComponents = CloseEyes_Song.components
        for thisComponent in CloseEyes_Song.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        thisExp.currentRoutine = CloseEyes_Song
        CloseEyes_Song.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 93.0:
            if hasattr(thisTrial, 'status') and thisTrial.status == STOPPING:
                continueRoutine = False
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  
            
            if CloseEyesText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                CloseEyesText.frameNStart = frameN  
                CloseEyesText.tStart = t  
                CloseEyesText.tStartRefresh = tThisFlipGlobal  
                win.timeOnFlip(CloseEyesText, 'tStartRefresh')  
                thisExp.timestampOnFlip(win, 'CloseEyesText.started')
                CloseEyesText.status = STARTED
                CloseEyesText.setAutoDraw(True)
            
            if CloseEyesText.status == STARTED:
                pass
            
            if CloseEyesText.status == STARTED:
                if tThisFlipGlobal > CloseEyesText.tStartRefresh + 3.0-frameTolerance:
                    CloseEyesText.tStop = t  
                    CloseEyesText.tStopRefresh = tThisFlipGlobal  
                    CloseEyesText.frameNStop = frameN  
                    thisExp.timestampOnFlip(win, 'CloseEyesText.stopped')
                    CloseEyesText.status = FINISHED
                    CloseEyesText.setAutoDraw(False)
            
            if song_played.status == NOT_STARTED and tThisFlip >= 3-frameTolerance:
                song_played.frameNStart = frameN  
                song_played.tStart = t  
                song_played.tStartRefresh = tThisFlipGlobal  
                thisExp.addData('song_played.started', tThisFlipGlobal)
                song_played.status = STARTED
                song_played.play(when=win)  
            
            if song_played.status == STARTED:
                if tThisFlipGlobal > song_played.tStartRefresh + 90-frameTolerance or song_played.isFinished:
                    song_played.tStop = t  
                    song_played.tStopRefresh = tThisFlipGlobal  
                    song_played.frameNStop = frameN  
                    thisExp.timestampOnFlip(win, 'song_played.stopped')
                    song_played.status = FINISHED
                    song_played.stop()
            
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=CloseEyes_Song,
                )
                continue
            
            if not continueRoutine:
                CloseEyes_Song.forceEnded = routineForceEnded = True
            if CloseEyes_Song.forceEnded or routineForceEnded:
                break
            continueRoutine = False
            for thisComponent in CloseEyes_Song.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  
            
            if continueRoutine:  
                win.flip()
        
        for thisComponent in CloseEyes_Song.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        CloseEyes_Song.tStop = globalClock.getTime(format='float')
        CloseEyes_Song.tStopRefresh = tThisFlipGlobal
        thisExp.addData('CloseEyes_Song.stopped', CloseEyes_Song.tStop)
        
        # Stop PiEEG acquisition and save one CSV for this song trial.
        data_to_save = pieeg_recorder.stop_trial(timeout=2.0)

        if data_to_save:
            song_basename = sanitize_filename_component(os.path.splitext(os.path.basename(filePath))[0]) # filePath is defined in the conditions CSV
            eeg_filename = os.path.join(
                _dataDir,
                f"{expInfo['participant']}_{expName}_trial{trials.thisN}_{song_basename}_eeg.csv"
            )
            write_eeg_csv(eeg_filename, data_to_save)

            thisExp.addData('eeg_file', eeg_filename)
            thisExp.addData('eeg_samples', len(data_to_save))
        else:
            thisExp.addData('eeg_file', 'NO_DATA')
            thisExp.addData('eeg_samples', 0)
        thisExp.addData('pieeg_mode', pieeg_recorder.mode)
        thisExp.addData('drdy_timeouts', pieeg_recorder.missed_samples)
        thisExp.addData('pieeg_zero_frames', pieeg_recorder.zero_frames)
        
        song_played.pause()  
        if CloseEyes_Song.maxDurationReached:
            routineTimer.addTime(-CloseEyes_Song.maxDuration)
        elif CloseEyes_Song.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-93.000000)
        
        RateSong = data.Routine(
            name='RateSong',
            components=[beep, RateSongText, song_rating],
        )
        RateSong.status = NOT_STARTED
        continueRoutine = True
        beep.setSound(os.path.join(_toolsDir, 'beep-09.mp3'), secs=1.0, hamming=True)
        beep.setVolume(1.0, log=False)
        beep.seek(0)
        song_rating.keys = []
        song_rating.rt = []
        _song_rating_allKeys = []
        RateSong.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        RateSong.tStart = globalClock.getTime(format='float')
        RateSong.status = STARTED
        thisExp.addData('RateSong.started', RateSong.tStart)
        RateSong.maxDuration = None
        RateSongComponents = RateSong.components
        for thisComponent in RateSong.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        thisExp.currentRoutine = RateSong
        RateSong.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            if hasattr(thisTrial, 'status') and thisTrial.status == STOPPING:
                continueRoutine = False
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  
            
            if beep.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                beep.frameNStart = frameN  
                beep.tStart = t  
                beep.tStartRefresh = tThisFlipGlobal  
                thisExp.addData('beep.started', tThisFlipGlobal)
                beep.status = STARTED
                beep.play(when=win)  
            
            if beep.status == STARTED:
                if tThisFlipGlobal > beep.tStartRefresh + 1.0-frameTolerance or beep.isFinished:
                    beep.tStop = t  
                    beep.tStopRefresh = tThisFlipGlobal  
                    beep.frameNStop = frameN  
                    thisExp.timestampOnFlip(win, 'beep.stopped')
                    beep.status = FINISHED
                    beep.stop()
            
            if RateSongText.status == NOT_STARTED and tThisFlip >= 1.0-frameTolerance:
                RateSongText.frameNStart = frameN  
                RateSongText.tStart = t  
                RateSongText.tStartRefresh = tThisFlipGlobal  
                win.timeOnFlip(RateSongText, 'tStartRefresh')  
                thisExp.timestampOnFlip(win, 'RateSongText.started')
                RateSongText.status = STARTED
                RateSongText.setAutoDraw(True)
            
            if RateSongText.status == STARTED:
                pass
            
            waitOnFlip = False
            
            if song_rating.status == NOT_STARTED and tThisFlip >= 1.0-frameTolerance:
                song_rating.frameNStart = frameN  
                song_rating.tStart = t  
                song_rating.tStartRefresh = tThisFlipGlobal  
                win.timeOnFlip(song_rating, 'tStartRefresh')  
                thisExp.timestampOnFlip(win, 'song_rating.started')
                song_rating.status = STARTED
                waitOnFlip = True
                win.callOnFlip(song_rating.clock.reset)  
                win.callOnFlip(song_rating.clearEvents, eventType='keyboard')  
            if song_rating.status == STARTED and not waitOnFlip:
                theseKeys = song_rating.getKeys(keyList=['1','2','3','4','5', '6','7'], ignoreKeys=["escape"], waitRelease=False)
                _song_rating_allKeys.extend(theseKeys)
                if len(_song_rating_allKeys):
                    song_rating.keys = _song_rating_allKeys[-1].name  
                    song_rating.rt = _song_rating_allKeys[-1].rt
                    song_rating.duration = _song_rating_allKeys[-1].duration
                    continueRoutine = False
            
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=RateSong,
                )
                continue
            
            if not continueRoutine:
                RateSong.forceEnded = routineForceEnded = True
            if RateSong.forceEnded or routineForceEnded:
                break
            continueRoutine = False
            for thisComponent in RateSong.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  
            
            if continueRoutine:  
                win.flip()
        
        for thisComponent in RateSong.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        RateSong.tStop = globalClock.getTime(format='float')
        RateSong.tStopRefresh = tThisFlipGlobal
        thisExp.addData('RateSong.stopped', RateSong.tStop)
        beep.pause()  
        if song_rating.keys in ['', [], None]:  
            song_rating.keys = None
        trials.addData('song_rating.keys',song_rating.keys)
        if song_rating.keys != None:  
            trials.addData('song_rating.rt', song_rating.rt)
            trials.addData('song_rating.duration', song_rating.duration)
        
        rating = song_rating.keys if song_rating.keys else "None"
        summary_text += f"{song} - Rating: {rating}\n" # song is defined in the conditions CSV
        routineTimer.reset()
        
        Familiarity = data.Routine(
            name='Familiarity',
            components=[FamiliarityText, familiarity_rating],
        )
        Familiarity.status = NOT_STARTED
        continueRoutine = True
        familiarity_rating.keys = []
        familiarity_rating.rt = []
        _familiarity_rating_allKeys = []
        Familiarity.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        Familiarity.tStart = globalClock.getTime(format='float')
        Familiarity.status = STARTED
        thisExp.addData('Familiarity.started', Familiarity.tStart)
        Familiarity.maxDuration = None
        FamiliarityComponents = Familiarity.components
        for thisComponent in Familiarity.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        thisExp.currentRoutine = Familiarity
        Familiarity.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            if hasattr(thisTrial, 'status') and thisTrial.status == STOPPING:
                continueRoutine = False
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  
            
            if FamiliarityText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                FamiliarityText.frameNStart = frameN  
                FamiliarityText.tStart = t  
                FamiliarityText.tStartRefresh = tThisFlipGlobal  
                win.timeOnFlip(FamiliarityText, 'tStartRefresh')  
                thisExp.timestampOnFlip(win, 'FamiliarityText.started')
                FamiliarityText.status = STARTED
                FamiliarityText.setAutoDraw(True)
            
            if FamiliarityText.status == STARTED:
                pass
            
            waitOnFlip = False
            
            if familiarity_rating.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                familiarity_rating.frameNStart = frameN  
                familiarity_rating.tStart = t  
                familiarity_rating.tStartRefresh = tThisFlipGlobal  
                win.timeOnFlip(familiarity_rating, 'tStartRefresh')  
                thisExp.timestampOnFlip(win, 'familiarity_rating.started')
                familiarity_rating.status = STARTED
                waitOnFlip = True
                win.callOnFlip(familiarity_rating.clock.reset)  
                win.callOnFlip(familiarity_rating.clearEvents, eventType='keyboard')  
            if familiarity_rating.status == STARTED and not waitOnFlip:
                theseKeys = familiarity_rating.getKeys(keyList=['y','n'], ignoreKeys=["escape"], waitRelease=False)
                _familiarity_rating_allKeys.extend(theseKeys)
                if len(_familiarity_rating_allKeys):
                    familiarity_rating.keys = _familiarity_rating_allKeys[-1].name  
                    familiarity_rating.rt = _familiarity_rating_allKeys[-1].rt
                    familiarity_rating.duration = _familiarity_rating_allKeys[-1].duration
                    continueRoutine = False
            
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=Familiarity,
                )
                continue
            
            if not continueRoutine:
                Familiarity.forceEnded = routineForceEnded = True
            if Familiarity.forceEnded or routineForceEnded:
                break
            continueRoutine = False
            for thisComponent in Familiarity.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  
            
            if continueRoutine:  
                win.flip()
        
        for thisComponent in Familiarity.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        Familiarity.tStop = globalClock.getTime(format='float')
        Familiarity.tStopRefresh = tThisFlipGlobal
        thisExp.addData('Familiarity.stopped', Familiarity.tStop)
        if familiarity_rating.keys in ['', [], None]:  
            familiarity_rating.keys = None
        trials.addData('familiarity_rating.keys',familiarity_rating.keys)
        if familiarity_rating.keys != None:  
            trials.addData('familiarity_rating.rt', familiarity_rating.rt)
            trials.addData('familiarity_rating.duration', familiarity_rating.duration)
        routineTimer.reset()
        if hasattr(thisTrial, 'status'):
            thisTrial.status = FINISHED
        if trials.status == PAUSED:
            thisExp.status = PAUSED
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[globalClock], 
            )
            trials.status = STARTED
        thisExp.nextEntry()
        
    trials.status = FINISHED
    
    if thisSession is not None:
        thisSession.sendExperimentData()
    
    ThankYou = data.Routine(
        name='ThankYou',
        components=[ThankYouText, Summary],
    )
    ThankYou.status = NOT_STARTED
    continueRoutine = True
    Summary.setText(summary_text)
    ThankYou.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    ThankYou.tStart = globalClock.getTime(format='float')
    ThankYou.status = STARTED
    thisExp.addData('ThankYou.started', ThankYou.tStart)
    ThankYou.maxDuration = None
    ThankYouComponents = ThankYou.components
    for thisComponent in ThankYou.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    thisExp.currentRoutine = ThankYou
    ThankYou.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 13.0:
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  
        
        if ThankYouText.status == NOT_STARTED and tThisFlip >= 5-frameTolerance:
            ThankYouText.frameNStart = frameN  
            ThankYouText.tStart = t  
            ThankYouText.tStartRefresh = tThisFlipGlobal  
            win.timeOnFlip(ThankYouText, 'tStartRefresh')  
            thisExp.timestampOnFlip(win, 'ThankYouText.started')
            ThankYouText.status = STARTED
            ThankYouText.setAutoDraw(True)
        
        if ThankYouText.status == STARTED:
            pass
        
        if ThankYouText.status == STARTED:
            if tThisFlipGlobal > ThankYouText.tStartRefresh + 8-frameTolerance:
                ThankYouText.tStop = t  
                ThankYouText.tStopRefresh = tThisFlipGlobal  
                ThankYouText.frameNStop = frameN  
                thisExp.timestampOnFlip(win, 'ThankYouText.stopped')
                ThankYouText.status = FINISHED
                ThankYouText.setAutoDraw(False)
        
        if Summary.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            Summary.frameNStart = frameN  
            Summary.tStart = t  
            Summary.tStartRefresh = tThisFlipGlobal  
            win.timeOnFlip(Summary, 'tStartRefresh')  
            thisExp.timestampOnFlip(win, 'Summary.started')
            Summary.status = STARTED
            Summary.setAutoDraw(True)
        
        if Summary.status == STARTED:
            pass
        
        if Summary.status == STARTED:
            if tThisFlipGlobal > Summary.tStartRefresh + 5-frameTolerance:
                Summary.tStop = t  
                Summary.tStopRefresh = tThisFlipGlobal  
                Summary.frameNStop = frameN  
                thisExp.timestampOnFlip(win, 'Summary.stopped')
                Summary.status = FINISHED
                Summary.setAutoDraw(False)
        
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=ThankYou,
            )
            continue
        
        if not continueRoutine:
            ThankYou.forceEnded = routineForceEnded = True
        if ThankYou.forceEnded or routineForceEnded:
            break
        continueRoutine = False
        for thisComponent in ThankYou.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  
        
        if continueRoutine:  
            win.flip()
    
    for thisComponent in ThankYou.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    ThankYou.tStop = globalClock.getTime(format='float')
    ThankYou.tStopRefresh = tThisFlipGlobal
    thisExp.addData('ThankYou.stopped', ThankYou.tStop)
    if ThankYou.maxDurationReached:
        routineTimer.addTime(-ThankYou.maxDuration)
    elif ThankYou.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-13.000000)
    thisExp.nextEntry()
    
    # mark experiment as finished
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
    run(
        expInfo=expInfo, 
        thisExp=thisExp, 
        win=win,
        globalClock='float'
    )
    saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)
