# ======================================= ИМПОРТ БИБЛИОТЕК =============================================================

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
from voiceAssistent import assistant

# ======================================= НАСТРОЙКИ ====================================================================

app = QtWidgets.QApplication([])
ui = uic.loadUi("design.ui")
ui.setWindowTitle("Serial GUI")

serial = QSerialPort()
serial.setBaudRate(9600)

cnt = 0
flagBtnLed = False
flagRelay = False
flagBuzzer = False

portList = []

onLeft = 0
onRight = 0
onClick = 0

strON = "🟢 Включено"
strOFF = "🔴 Выключено"


# ======================================= ФУНКЦИИ ======================================================================


def reloadComPortsCB():
    ui.comPortsCB.clear()
    ports = QSerialPortInfo().availablePorts()

    global portList
    portList = []
    for port in ports:
        portList.append(port.portName())
        # portList.append(port.systemLocation())
        # portList.append(port.description())

    ui.comPortsCB.addItems(portList)


def serialSend(data):
    txs = ""
    for val in data:
        txs += str(val) + ','
    txs = txs[:-1]
    txs += ';'
    serial.write(txs.encode())


def OnRead():
    # if not serial.canReadLine(): return  # выходим если нечего читать
    rx = serial.readLine()
    rx = str(rx, 'utf-8').strip()
    data = rx.split(',')
    # print(data)

    if data[0] == '100':  # ПОДКЛЮЧЕНИЕ
        if data[1] == '1':
            openSuccess()

    if data[0] == '0':
        if data[1] == '0':
            ui.labelLed.setText(strOFF)
        elif data[1] == '1':
            ui.labelLed.setText(strON)

    if data[0] == '1':  # ЭНКОДЕР
        if data[1] == '0':
            global onClick
            onClick += 1
            ui.encLcdNumClick.display(onClick)
        if data[1] == '1':
            global onRight
            onRight += 1
            ui.encLcdNumR.display(onRight)
            ui.encoderProgressBar.setValue(ui.encoderProgressBar.value() + 5)
        if data[1] == '2':
            global onLeft
            onLeft += 1
            ui.encLcdNumL.display(onLeft)
            ui.encoderProgressBar.setValue(ui.encoderProgressBar.value() - 5)

    if data[0] == '2':  # ДАТЧИК ХОЛЛА
        if data[1] == '0':
            ui.hallProgressBar.setValue(0)
        if data[1] == '1':
            ui.hallProgressBar.setValue(10)


def onOpen():
    serial.setPortName(ui.comPortsCB.currentText())
    serial.open(QIODevice.ReadWrite)


def openSuccess():
    info = QMessageBox()
    info.setWindowTitle("Информация")
    info.setText("COM-порт был успешно открыт! \n")
    info.setInformativeText("Arduino устройство готово к работе")
    info.setIcon(QMessageBox.Information)
    info.setStandardButtons(QMessageBox.Ok)
    ui.connectBtn.setText(strON)
    info.exec_()


def OnClose():
    serial.close()
    ui.connectBtn.setText(strOFF)


def RGB_LED():
    # serialSend([{key}, ui.RS.value(), ui.GS.value(), ui.BS.value()])
    # print([{key}, ui.Slider_red.value(), ui.Slider_green.value(), ui.Slider_blue.value()])
    ui.label_red.setText(str(ui.Slider_red.value()))
    ui.label_green.setText(str(ui.Slider_green.value()))
    ui.label_blue.setText(str(ui.Slider_blue.value()))


def btnLed():
    global flagBtnLed

    if flagBtnLed:
        flagBtnLed = False
        serialSend([0, 0])
    else:
        flagBtnLed = True
        serialSend([0, 1])


def pwmSlider():
    serialSend([3, ui.pwmSlider.value()])
    ui.pwmLcd.display(ui.pwmSlider.value())


def btnRelay():
    global flagRelay

    if flagRelay:
        ui.labelRelay.setText(strOFF)
        flagRelay = False
        serialSend([1, 0])
    else:
        ui.labelRelay.setText(strON)
        flagRelay = True
        serialSend([1, 1])


def btnBuzzer():
    global flagBuzzer

    if flagBuzzer:
        ui.labelBuzzer.setText(strOFF)
        flagBuzzer = False
        serialSend([2, 0])
    else:
        ui.labelBuzzer.setText(strON)
        flagBuzzer = True
        serialSend([2, 1])


def sendText():
    txs = '4,' + ui.serialText.displayText() + ';'
    serial.write(txs.encode())
    ui.serialText.setText('')


def voiceBtn(value):
    ui.voiceIndicator.setValue(value)


def voiceSwitch():
    print(ui.voiceSwitch.value())
    if ui.voiceSwitch.value() == 1:
        assistant.listen()
    elif ui.voiceSwitch.value() == 0:
        print("assistant stop")


# ======================================= ИНТЕРФЕЙС ====================================================================

# ui.comPortsCB.addItems(portList)
reloadComPortsCB()
ui.reloadBtn.clicked.connect(reloadComPortsCB)

serial.readyRead.connect(OnRead)
ui.openBtn.clicked.connect(onOpen)
ui.closeBtn.clicked.connect(OnClose)
ui.serialTextBtn.clicked.connect(sendText)

ui.Slider_red.valueChanged.connect(RGB_LED)
ui.Slider_green.valueChanged.connect(RGB_LED)
ui.Slider_blue.valueChanged.connect(RGB_LED)

ui.btnRelay.clicked.connect(btnRelay)
ui.btnLed.clicked.connect(btnLed)
ui.btnBuzzer.clicked.connect(btnBuzzer)
ui.pwmSlider.valueChanged.connect(pwmSlider)

ui.voiceBtn.pressed.connect(lambda: voiceBtn(1))
ui.voiceBtn.released.connect(lambda: voiceBtn(0))

ui.voiceSwitch.valueChanged.connect(voiceSwitch)

ui.show()
app.exec()
