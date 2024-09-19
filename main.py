# Built-in modules
from pathlib import Path
from re import sub
from subprocess import run, DEVNULL
from sys import exit
from time import sleep

# Third-party modules
from yaml import safe_load


# Defining the variables
settings_path = Path('settings.yaml')
scrcpy_dir = Path('dependencies/scrcpy-win64-v2.7')

# Checks if the settings.yaml file does not exist
if not settings_path.exists():
    default_settings = '''
auto-scrcpy-script:
  max-retries-on-error: 15  # max retries on error [0, 1, 2, 3, *] (default: 15)
  time-between-retries: 5  # time between retries in seconds [0, 1, 2, 3, *] (default: 5)
device:
  stay-awake: true  # keep device awake [true/false] (default: true)
  turn-screen-off-on-start: false  # turn screen off on start [true/false] (default: false)
  show-touches: false  # show touches [true/false] (default: false)
video:
  enabled: true  # true to enable video, false to disable (default: true)
  codec: h264  # video codec [h264 = should provide lower latency, h265 = may provide better quality, av1 = encoders are not common on current Android devices] (default: h264)
  bit-rate: 8m  # video bitrate in m (default: 8m)
  max-fps: 60  # max video fps [5, 10, 15, 20, 25, 30, 60, *] (default: 60)
  max-size: 1280  # max video size [*, 1280 = 1280x720, 1920 = 1920x1080, 2560 = 2560x1440, 3840 = 3840x2160] (default: 1920)
audio:
  enabled: true  # true to enable audio, false to disable (default: true)
  codec: opus  # audio codec [opus, aac, raw] (default: opus)
  bit-rate: 128k  # audio bitrate in k (default: 128k)
    '''.strip()

    with open(settings_path, 'w') as file:
        file.write(default_settings)

    print('\n[WARN] The settings.yaml file does not exist, it has been created with the default settings')
    print('[WARN] To change the settings, edit the settings.yaml file')
    input('[WARN] Restart the script after changing the settings')
    exit()

# Loading the settings.yaml file
with open(settings_path, 'r') as file:
    setting = safe_load(file)

# > -- - Script
option_script_max_retries_on_error = int(setting['auto-scrcpy-script']['max-retries-on-error'])
option_script_time_between_retries = int(setting['auto-scrcpy-script']['time-between-retries'])

# > -- - Device
option_device_stay_awake = bool(setting['device']['stay-awake'])  # --stay-awake
option_device_turn_screen_off_on_start = bool(setting['device']['turn-screen-off-on-start'])  # --turn-screen-off
option_device_show_touches = bool(setting['device']['show-touches'])  # --show-touches

# > -- - Video
option_video_enabled = bool(setting['video']['enabled'])  # --no-video
option_video_codec = str(setting['video']['codec'])  # --video-codec=
option_video_bit_rate = str(setting['video']['bit-rate'])  # --video-bit-rate=
option_video_max_fps = str(setting['video']['max-fps'])  # --max-fps=
option_video_max_size = str(setting['video']['max-size'])  # --max-size=

# > -- - Audio
option_audio_enabled = bool(setting['audio']['enabled'])  # --no-audio
option_audio_codec = str(setting['audio']['codec'])  # --audio-codec=
option_audio_bitrate = str(setting['audio']['bit-rate'])  # --audio-bit-rate=

# Defining the default variables
device_stay_awake = str()
device_turn_screen_off = str()
device_show_touches = str()
video_enabled = str()
audio_enabled = str()

# Organizing the variables
if option_device_stay_awake: device_stay_awake = '--stay-awake'
if option_device_turn_screen_off_on_start: device_turn_screen_off = '--turn-screen-off'
if option_device_show_touches: device_show_touches = '--show-touches'

if not option_video_enabled: video_enabled = '--no-video'
video_codec = '--video-codec=' + option_video_codec
video_bit_rate = '--video-bit-rate=' + option_video_bit_rate
video_max_fps = '--max-fps=' + option_video_max_fps
video_max_size = '--max-size=' + option_video_max_size

if not option_audio_enabled: audio_enabled = '--no-audio'
audio_codec = '--audio-codec=' + option_audio_codec
audio_bitrate = '--audio-bit-rate=' + option_audio_bitrate

# Merging all parameters and creating the command
binary_dir = Path(scrcpy_dir, 'scrcpy.exe')
parameters = sub(r'\s+', ' ', f'{device_stay_awake} {device_turn_screen_off} {device_show_touches} {video_enabled} {video_codec} {video_bit_rate} {video_max_fps} {video_max_size} {audio_enabled} {audio_codec} {audio_bitrate}').lower().strip()
command = f'{binary_dir} {parameters}'

# Printing the information
print('\n[CREDIT] SCRCPY was developed by https://github.com/Genymobile')
print('[CREDIT] The current script facilitates the use of SCRCPY and was developed by https://github.com/Henrique-Coder')

print(f'\n[INFO] SCRCPY Binary: {binary_dir}')
print(f'[INFO] Parameters: {parameters}')
print(f'[INFO] Command:  scrcpy.exe {parameters}')

print('\n[TIP] To change the settings, edit the settings.yaml file')
print('[TIP] To enter fullscreen mode, press Alt + F in the SCRCPY window')

print('\n[RUNNING] Starting SCRCPY...')
command_output = run(command, stdout=DEVNULL, stderr=DEVNULL)
max_retries = option_script_max_retries_on_error
now_try = 0
if command_output.returncode != 0:
    now_try += 1
    max_retries -= 1
    print(f'[ERROR] Trying to connect to the device... [Attempt: {now_try}] [Retries left: {max_retries}] [Time left: 00s]', end='\r')
    while max_retries > 0:
        now_try += 1
        max_retries -= 1
        seconds_left = option_script_time_between_retries
        sleep(1)
        while seconds_left > 0:
            print(f'[ERROR] Trying to connect to the device... [Attempt: {now_try}] [Retries left: {str(max_retries).zfill(2)}] [Time left: {str(seconds_left).zfill(2)}s]', end='\r')
            sleep(1)
            print(f'[ERROR] Trying to connect to the device... [Attempt: {now_try}] [Retries left: {str(max_retries).zfill(2)}] [Time left: {str(seconds_left-1).zfill(2)}s]', end='\r')
            seconds_left -= 1
        command_output = run(command, stdout=DEVNULL, stderr=DEVNULL, shell=True)
        if command_output.returncode == 0:
            break


# Exiting the script
print('\n\n[END] SCRCPY has been closed!')
exit()
