from voiceAssistent import config
from voiceAssistent import stt
from voiceAssistent import tts
from fuzzywuzzy import fuzz

print(f"{config.NAME[0].upper()} (v{config.VER[0]}) начала свою работу ...")


def respond(voice: str):
    print(voice)

    if voice.startswith(config.NAME):
        # обращаются к ассистенту
        cmd = recognize_cmd(filter_cmd(voice))
        # cmd = recognize_cmd(voice)

        if cmd['cmd'] not in config.CMD_LIST.keys():
            tts.speak("Что, мой повелитель")
        else:
            execute_cmd(cmd['cmd'])

        # execute_cmd(cmd['cmd'])


def filter_cmd(raw_voice: str):
    cmd = raw_voice

    for x in config.NAME:
        cmd = cmd.replace(x, "").strip()

    for x in config.TBR:
        cmd = cmd.replace(x, "").strip()

    return cmd


def recognize_cmd(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in config.CMD_LIST.items():

        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc


def execute_cmd(cmd: str):
    if cmd == 'cmd1':
        print("COMMAND 1")
        tts.speak("Выполняю команду один")

    elif cmd == 'cmd2':
        print("COMMAND 2")
        tts.speak("Выполняю команду два")

    elif cmd == 'cmd3':
        print("COMMAND 3")
        tts.speak("Выполняю команду три")

    else:
        print("Команда не распознана")
        tts.speak("Команда не распознана")


# начать прослушивание команд
def listen():
    tts.speak("Здравствуйте, я вас слушаю")
    stt.listen(respond)
