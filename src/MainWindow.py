# -*- coding: utf-8 -*-
import sys
import subprocess
import MainUi
import platform
import socket
import threading
import psutil
from hexconvert import HexConvert as hexConv
from TcpAgent import TcpAgent as tcpAgent
from TcpAgent import UdpAgent as udpAgent
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore

''' BACKUP SLOT FUNCTIONS ON MainUi.py to avoid MainUi.py is re-write when converted to MainUi.py automatilly.

        self.comboBoxProtocal.currentIndexChanged['int'].connect(MainWindow.on_comboBoxProtocal_currentIndexChanged)
        self.comboBoxMode.currentIndexChanged['int'].connect(MainWindow.on_comboBoxMode_currentIndexChanged)
        self.checkBoxWordWrap.clicked['bool'].connect(MainWindow.on_checkBoxWordWrap_clicked)
        self.checkBoxDisplayTime.clicked['bool'].connect(MainWindow.on_checkBoxDisplayTime_clicked)
        self.checkBoxDisplayRecTime.clicked['bool'].connect(MainWindow.on_checkBoxDisplayRecTime_clicked)
        self.checkBoxRepeatSend.clicked['bool'].connect(MainWindow.on_checkBoxRepeatSend_clicked)
        self.radioButtonSendASCII.clicked.connect(MainWindow.on_radioButtonSendASCII_clicked)
        self.radioButtonSendHex.clicked.connect(MainWindow.on_radioButtonSendHex_clicked)
        self.radioButtonRecASCII.clicked.connect(MainWindow.on_radioButtonRecASCII_clicked)
        self.radioButtonRecHex.clicked.connect(MainWindow.on_radioButtonRecHex_clicked)
        self.spinBox.valueChanged['int'].connect(MainWindow.on_spinBoxTime_valueChanged)
        self.pushButtonConnect.clicked.connect(MainWindow.on_pushButtonConnect_click)
        self.pushButtonPing.clicked.connect(MainWindow.on_pushButtonPing_click)
        self.pushButtonDisconnect.clicked.connect(MainWindow.on_pushButtonDisconnect_click)
        self.pushButtonSend.clicked.connect(MainWindow.on_pushButtonSend_clicked)
        self.pushButtonClear.clicked.connect(MainWindow.on_pushButtonClear_clicked)
        self.pushButtonWriteIp.clicked.connect(MainWindow.on_pushButtonWriteIp_clicked)
        self.pushButtonAppIp.clicked.connect(MainWindow.on_pushButtonAppIp_clicked)
        
'''

class MainWindow(QMainWindow):

    ui = MainUi.Ui_MainWindow()
    # UI MACROS
    MODE_SERVER = 0
    MODE_CLIENT = 1
    tcp_mode = MODE_CLIENT
    PROTOCAL_TCP = 0
    PROTOCAL_UDP = 1
    protocal_mode = PROTOCAL_TCP
    tcpAgent = tcpAgent()
    eth_device_list = []

    ASCII_FLAG = 0
    HEX_FLAG = 1
    recv_disp_mode = ASCII_FLAG
    send_disp_mode = ASCII_FLAG

    is_disp_send_time = False
    is_disp_recv_time = False
    is_word_wrap = False
    is_repeat_send_mode = False

    repeat_send_time_ms = 0


    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui.setupUi(self)
        self.setWindowTitle("Tiny Network Tool v1.0")
        self.init_ui_logic()

    def on_btn_click_signal(self):
        k = 1
        #self.ui.label.setText("hello")

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def init_ui_logic(self):
        self.ui.lineEditAimIp.setText("192.168.31.1")
        self.ui.lineEditLocalPort.setText( "8388" )
        self.ui.lineEditLocalIp.setText( self.get_local_ip() )
        self.ui.comboBoxMode.setCurrentIndex( self.tcp_mode )
        self.ui.comboBoxProtocal.setCurrentIndex( self.protocal_mode )
        self.ui.pushButtonDisconnect.setEnabled(False)
        self.ui.radioButtonRecASCII.setChecked(True)
        self.ui.radioButtonSendASCII.setChecked(True)
        self.refresh_devices_list()

    def refresh_devices_list(self):
        for i in range( self.ui.comboBoxEthList.count() ):
            self.ui.comboBoxEthList.removeItem(i)
        net_devices_list = self.scan_net_devices()
        for item in net_devices_list:
            self.ui.comboBoxEthList.addItem( item )

    def scan_net_devices(self):
        net_devices_info = []
        temp_info = psutil.net_if_addrs()
        for k, v in temp_info.items():
             net_devices_info.append( (k, v) )
        device_name = []
        device_address = []
        item_str_list = []
        k = 0
        for device in net_devices_info:
            print( device )
            device_name.append( device[0] )
            dev = device[1]
            i = 0
            for item in dev[0]:
                if i == 1:
                    if item.find(".") >= 0:
                        device_address.append(item)
                    else:
                        device_address.append("-")
                else:
                    pass
                i = i + 1
            item_str_list.append( str(device_name[k]) + ", (" + str(device_address[k]) + ")" )
            k = k + 1
        return item_str_list

    def pop_error_window(self, content):
        error_win = QMessageBox()
        error_win.setModal( True )
        error_win.setWindowTitle( "Error" )
        error_win.setIcon(QMessageBox.Critical)
        error_win.setText( content )
        error_win.exec()

    def pop_info_window(self, content):
        info_win = QMessageBox()
        info_win.setModal( True )
        info_win.setWindowTitle( "Info" )
        info_win.setIcon(QMessageBox.Information)
        info_win.setText( content )
        info_win.exec()

    def repeat_send(self):
        self.on_pushButtonSend_clicked()

    timer = threading.Timer(5, repeat_send)
    @QtCore.pyqtSlot("int", name="on_comboboxprotocal_currentindexchanged")
    def on_comboBoxProtocal_currentIndexChanged(self, int_index):
        print("ui: protocal index change to " + str( int_index ) )
        self.protocal_mode = int_index
        if int_index == self.PROTOCAL_UDP:
            self.ui.comboBoxMode.setEnabled( False )
            self.ui.pushButtonConnect.setEnabled( False )
            self.ui.pushButtonDisconnect.setEnabled( False )
        else:
            self.ui.comboBoxMode.setEnabled( True )
            self.ui.pushButtonConnect.setEnabled( True )
            self.ui.pushButtonDisconnect.setEnabled( True )

    @QtCore.pyqtSlot("int", name="on_comboboxmode_currentindexchanged")
    def on_comboBoxMode_currentIndexChanged(self, int_index):
        self.tcp_mode = int_index
        if self.tcp_mode == self.MODE_SERVER:
            self.ui.pushButtonConnect.setText("Listen")
        elif self.tcp_mode == self.MODE_CLIENT:
            self.ui.pushButtonConnect.setText("Connect")

    @QtCore.pyqtSlot(name="on_pushbuttonping_click")
    def on_pushButtonPing_click(self):

        aim_ip = self.ui.lineEditAimIp.text()
        if len( aim_ip ) == 0:
            self.pop_error_window("Aim ip is Empty.")
            return
        if "." not in aim_ip or ":" not in aim_ip:
            self.pop_error_window("IP format illegal")
            return
        self.ui.statusbar.showMessage("ping " + aim_ip + "| waitting...")
        ret = subprocess.call(["ping", aim_ip ,"-c", "2"])
        if ret == 0:
            self.ui.statusbar.showMessage("system: ping " + aim_ip + " network normal.", 3000)
            self.pop_info_window("system: ping " + aim_ip + " network normal." )
        else:
            self.ui.statusbar.showMessage("system: ping " + aim_ip + " network failed.", 3000)
            self.pop_error_window("system: ping " + aim_ip + " network failed.")

    @QtCore.pyqtSlot(name="on_pushbuttonconnect_click")
    def on_pushButtonConnect_click(self):
        if len( self.ui.lineEditLocalIp.text() ) == 0:
            self.pop_error_window("Local IP is Empty!")
            self.ui.lineEditLocalIp.setFocus()
            return
        if len( self.ui.lineEditLocalPort.text() ) == 0:
            self.pop_error_window("Listen Port is Empty!")
            self.ui.lineEditLocalPort.setFocus()
            return
        local_ip = self.ui.lineEditLocalIp.text()
        local_port = int( self.ui.lineEditLocalPort.text() )
        mode = self.ui.comboBoxMode.currentIndex()
        self.tcpAgent.set_mode( mode )
        if  bool( 1 - self.tcpAgent.connect( local_ip, local_port ) ):
            # tcpAgent error information via the msg sginal-slot mechanism
            pass
        else:
            self.pop_info_window( local_ip + "  " + str(local_port)  + " has been set up.")
            self.ui.pushButtonConnect.setEnabled(False)
            self.ui.pushButtonDisconnect.setEnabled( True )
            self.ui.pushButtonAppIp.setEnabled( False )
            self.ui.pushButtonWriteIp.setEnabled( False )
            self.ui.comboBoxEthList.setEnabled( False )
            self.ui.comboBoxMode.setEnabled( False )
            self.ui.comboBoxProtocal.setEnabled( False )

    @QtCore.pyqtSlot(name="on_pushbuttondisconnect_click")
    def on_pushButtonDisconnect_click(self):
        self.tcpAgent.disconnect()
        self.ui.pushButtonConnect.setEnabled( True )
        self.ui.pushButtonDisconnect.setEnabled( False )
        self.ui.pushButtonAppIp.setEnabled( True )
        self.ui.pushButtonWriteIp.setEnabled( True )
        self.ui.comboBoxEthList.setEnabled( True )
        self.ui.comboBoxMode.setEnabled( True )
        self.ui.comboBoxProtocal.setEnabled( True )

    @QtCore.pyqtSlot(name="on_radiobuttonrecascii_clicked")
    def on_radioButtonRecASCII_clicked(self):
        print("radioButtonRecASCII")
        self.recv_disp_mode = self.ASCII_FLAG

    @QtCore.pyqtSlot(name="on_radiobuttonrechex_clicked")
    def on_radioButtonRecHex_clicked(self):
        print("radioButtonRecHex")
        self.recv_disp_mode = self.HEX_FLAG

    @QtCore.pyqtSlot(name="on_radiobuttonsendascii_clicked")
    def on_radioButtonSendASCII_clicked(self):
        print("radioButtonSendASCII ")
        self.send_disp_mode = self.ASCII_FLAG

    @QtCore.pyqtSlot(name="on_radiobuttonsendhex_clicked")
    def on_radioButtonSendHex_clicked(self):
        print("radioButtonSendHex ")
        self.send_disp_mode = self.HEX_FLAG

    @QtCore.pyqtSlot("bool", name="on_checkboxwordwrap_clicked")
    def on_checkBoxWordWrap_clicked(self, checked):
        print("checkBoxWordWrap: " + str(checked))
        self.is_word_wrap = checked

    @QtCore.pyqtSlot("bool", name="on_checkboxwordwrap_clicked")
    def on_checkBoxDisplayTime_clicked(self, checked):
        print("checkBoxDisplayTime: " + str(checked))
        self.is_disp_send_time = checked

    @QtCore.pyqtSlot("bool", name="on_checkboxdisplayrectime_clicked")
    def on_checkBoxDisplayRecTime_clicked(self, checked):
        print("checkBoxDisplayRecTime : " + str(checked))
        self.is_disp_recv_time = checked

    @QtCore.pyqtSlot("bool", name="on_checkboxrepeatsend_clicked")
    def on_checkBoxRepeatSend_clicked(self, checked):
        print( "checkBoxRepeatSend : " + str(checked) )
        self.is_repeat_send_mode = checked

    @QtCore.pyqtSlot("int", name="on_spinboxtime_valuechanged")
    def on_spinBoxTime_valueChanged(self, time):
        print( "ms value change:" + str(time) )
        self.repeat_send_time_ms = time

    @QtCore.pyqtSlot(name="on_pushbuttonsend_clicked")
    def on_pushButtonSend_clicked(self):
        if len(self.ui.textEditSend.toPlainText()) == 0:
            if self.timer.isAlive():
                self.timer.cancel()
            self.pop_error_window("Send Editor is Empty!")
            self.ui.textEditSend.setFocus()
            return
        browser_text = self.ui.textEditSend.toPlainText()
        if self.send_disp_mode == self.ASCII_FLAG:
            self.tcpAgent.send_bytes( list( browser_text ) )
        elif self.send_disp_mode == self.HEX_FLAG:
            send_bytes = hexConv.stringTobytes( browser_text )
            self.tcpAgent.send_bytes( send_bytes )


    @QtCore.pyqtSlot(name="on_pushbuttonclear_clicked")
    def on_pushButtonClear_clicked(self):
        self.ui.textBrowserRec.clear()

    @QtCore.pyqtSlot(name="on_pushbuttonwriteip_clicked")
    def on_pushButtonWriteIp_clicked(self):
        # need root authorization.
        net_word = self.ui.comboBoxEthList.currentText()
        net_dev_name = net_word.split(",")
        if net_dev_name[0] == "lo":
            self.pop_error_window("'lo' may not modify the ip.")
            return
        print( "current select deivce :" + net_dev_name[0] )
        net_addr = self.ui.lineEditLocalIp.text()
        if platform.system() == "Linux" :
            msg = ""
            try:
                ret = subprocess.call(["ifconfig", net_dev_name[0], net_addr])
            except Exception as ret_e:
                msg = ret_e
            else:
                pass
            if ret == 0:
                self.pop_info_window( msg + net_dev_name[0] + ": " + net_addr + " set succussful")
            else:
                self.pop_error_window( msg +  net_dev_name[0] + ": " + net_addr + " set failed" )
        elif platform.system() == "Windows":
            pass
    def on_pushButtonAppIp_clicked(self):
        pass

    @QtCore.pyqtSlot(str, name="sig_tcp_agent_send_msg")
    def on_tcpAgent_send_msg(self, msg):
        print("recv : sig_tcp_agent_send_msg ")
        self.pop_error_window( msg )

    @QtCore.pyqtSlot(str, name="sig_tcp_agent_recv_network_msg")
    def on_tcpAgent_recv_network_msg(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    # deal with the signal and slot
    win.tcpAgent.sig_tcp_agent_send_msg.connect( win.on_tcpAgent_send_msg )
    win.tcpAgent.sig_tcp_agent_recv_network_msg.connect( win.on_tcpAgent_recv_network_msg )

    win.show()
    sys.exit(app.exec_())