# -*- coding: UTF-8 -*-
import sys, time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from tomasulo.tomasulo import Tomasulo as TomasuloCore
from tomasulo.hardware import Add, Mult, Load


initial = [
    "LD,F1,0x2",
    "LD,F2,0x1",
    "LD,F3,0xFFFFFFFF",
    "SUB,F1,F1,F2",
    "DIV,F4,F3,F1",
    "JUMP,0x0,F1,0x2",
    "JUMP,0xFFFFFFFF,F3,0xFFFFFFFD",
    "MUL,F3,F1,F4"
]

class AutoRunThread(QThread):
    refresh = pyqtSignal()

    def __init__(self, tomasulo):
        super(AutoRunThread, self).__init__()
        self.auto = True
        self.tomasulo = tomasulo

    def run(self):
        while self.auto is True and self.tomasulo.tomasulo.end() is False:
            self.tomasulo.tomasulo.step()
            self.refresh.emit()
            time.sleep(1)

    def stop(self):
        self.auto = False


class Tomasulo(QWidget):
    autostop = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.reshape()
        self.initIcon()
        self.initToolTip()
        self.initButton()

        self.tomasulo = TomasuloCore()
        self.initData()

        self.inst = QTableWidget()
        self.inst.setRowCount(1000)
        self.inst.setColumnCount(4)
        self.inst.setHorizontalHeaderLabels(["指令", "發射周期", "執行完畢", "寫回结果"])
        instList = []
        for i in range(1000):
            instList.append(str(i))
        self.inst.setVerticalHeaderLabels(instList)
        self.inst.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inst.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inst.setSelectionMode(QAbstractItemView.SingleSelection)
        self.inst.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.inst.resizeColumnsToContents()
        self.inst.setShowGrid(False)
        self.initInst()

        self.LB = QTableWidget()
        self.LB.setRowCount(3)
        self.LB.setColumnCount(7)
        self.LB.setHorizontalHeaderLabels(["名稱", "Busy", "剩餘周期", "FU", "操作碼", "立即數", "指令id"])
        self.LB.verticalHeader().setVisible(False)
        self.LB.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.LB.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.LB.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.LB.setSelectionMode(QAbstractItemView.SingleSelection)
        self.LB.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.LB.resizeColumnsToContents()
        self.LB.setShowGrid(False)
        self.initLB()

        self.RS = QTableWidget()
        self.RS.setRowCount(9)
        self.RS.setColumnCount(9)
        self.RS.setHorizontalHeaderLabels(["名稱", "Busy", "剩餘周期", "FU", "操作碼", "Vj", "Vk", "Qj", "Qk"])
        self.RS.verticalHeader().setVisible(False)
        self.RS.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.RS.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.RS.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.RS.setSelectionMode(QAbstractItemView.SingleSelection)
        self.RS.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.RS.resizeColumnsToContents()
        self.RS.setShowGrid(False)
        self.initRS()

        self.register = QTableWidget()
        self.register.setRowCount(2)
        self.register.setColumnCount(33)
        registerList = ['PC']
        registerList.extend(self.tomasulo.register.keys())
        self.register.setHorizontalHeaderLabels(registerList)
        self.register.setVerticalHeaderLabels(["狀態", "數值"])
        self.register.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.register.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.register.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.register.setSelectionMode(QAbstractItemView.SingleSelection)
        self.register.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.register.resizeColumnsToContents()
        self.register.setShowGrid(False)
        self.initregister()

        self.autorunthread = AutoRunThread(self)
        self.autorunthread.refresh.connect(self.refresh)
        self.autostop.connect(self.autorunthread.stop)

        buttonlayout = QVBoxLayout()
        buttonlayout.addWidget(self.initbtn)
        buttonlayout.addWidget(self.clocklbl)
        buttonlayout.addWidget(self.clock)
        buttonlayout.addWidget(self.stepbtn)
        buttonlayout.addWidget(self.stepsbtn)
        buttonlayout.addWidget(self.autobtn)
        buttonlayout.addWidget(self.resultbtn)
        buttonlayout.addWidget(self.resetbtn)
        buttonlayout.addStretch()
        buttonlayout.setSpacing(20)

        instlayout = QVBoxLayout()
        instlayout.addWidget(QLabel("Instructions"))
        instlayout.addWidget(self.inst, 1)
        instlayout.setContentsMargins(20, 0, 0, 20)

        rslayout = QVBoxLayout()
        rslayout.addWidget(QLabel("Load Buffer"))
        rslayout.addWidget(self.LB, 1)
        rslayout.addWidget(QLabel("Reservation Stations"))
        rslayout.addWidget(self.RS, 4)
        rslayout.setContentsMargins(20, 0, 0, 20)

        tablelayout = QHBoxLayout()
        tablelayout.addLayout(instlayout, 1)
        tablelayout.addLayout(rslayout, 2)

        registerlayout = QVBoxLayout()
        registerlayout.addWidget(QLabel("Registers"))
        registerlayout.addWidget(self.register, 1)
        registerlayout.setContentsMargins(20, 0, 0, 20)

        mainlayout = QVBoxLayout()
        mainlayout.addLayout(tablelayout, 4)
        mainlayout.addLayout(registerlayout, 1)

        layout = QHBoxLayout(self)
        layout.addLayout(buttonlayout)
        layout.addLayout(mainlayout)
        layout.setContentsMargins(20, 20, 20, 20)

        self.show()

    def reshape(self):
        self.resize(1440, 900)
        self.setWindowTitle("Tomasulo")
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initIcon(self):
        self.setWindowIcon(QIcon('static/icon.png'))

    def initToolTip(self):
        QToolTip.setFont(QFont('SansSerif', 10))

    def initButton(self):
        self.initbtn = QPushButton("輸入指令", self)
        self.initbtn.setToolTip("輸入指令")
        self.initbtn.clicked.connect(self.initdialog)

        self.clocklbl = QLabel("時鐘周期：", self)
        self.clock = QLCDNumber(self)
        self.clock.setSegmentStyle(QLCDNumber.Flat)
        self.clock.setDigitCount(5)
        self.clock.setMode(QLCDNumber.Dec)
        self.clock.display('0')

        self.stepbtn = QPushButton("單步執步", self)
        self.stepbtn.setToolTip("執行一步")
        self.stepbtn.clicked.connect(self.step)

        self.stepsbtn = QPushButton("多步執行", self)
        self.stepsbtn.setToolTip("執行輸入的步數")
        self.stepsbtn.clicked.connect(self.stepsdialog)

        self.autobtn = QPushButton("自動運行", self)
        self.autobtn.setToolTip("每秒運行一步，自動運行到结束")
        self.autobtn.clicked.connect(self.autorun)

        self.resultbtn = QPushButton("運行到結束", self)
        self.resultbtn.setToolTip("自動運行到產生結果")
        self.resultbtn.clicked.connect(self.getresult)

        self.resetbtn = QPushButton("清除", self)
        self.resetbtn.setToolTip("回到初始狀態")
        self.resetbtn.clicked.connect(self.reset)

    def initData(self):
        for line in initial:
            self.tomasulo.insert_inst(line)

    def initInst(self):
        i = 0
        for inst in self.tomasulo.inst:
            content = QTableWidgetItem(inst.content)
            content.setToolTip(inst.content)
            content.setTextAlignment(Qt.AlignVCenter)
            self.inst.setItem(i, 0, content)
            Issue = QTableWidgetItem(str(inst.Issue) if inst.Issue is not None else None)
            Issue.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.inst.setItem(i, 1, Issue)
            ExecComp = QTableWidgetItem(str(inst.ExecComp) if inst.ExecComp is not None else None)
            ExecComp.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.inst.setItem(i, 2, ExecComp)
            WriteResult = QTableWidgetItem(str(inst.WriteResult) if inst.WriteResult is not None else None)
            WriteResult.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.inst.setItem(i, 3, WriteResult)
            i += 1

    def initLB(self):
        i = 0
        for LB in self.tomasulo.RS.LB.values():
            name = QTableWidgetItem(LB.name)
            name.setToolTip(LB.name)
            name.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LB.setItem(i, 0, name)
            busy = QTableWidgetItem('YES' if LB.busy else None)
            busy.setToolTip("保留站是否被占用")
            busy.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LB.setItem(i, 1, busy)
            remain = QTableWidgetItem(str(LB.remain) if LB.remain is not None else None)
            remain.setToolTip("剩餘的時間周期")
            remain.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LB.setItem(i, 2, remain)
            fu = QTableWidgetItem(LB.FU)
            fu.setToolTip("執行該指令的功能部件名")
            fu.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LB.setItem(i, 3, fu)
            op = QTableWidgetItem(LB.op)
            op.setToolTip("指令操作碼")
            op.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LB.setItem(i, 4, op)
            im = QTableWidgetItem(LB.im)
            im.setToolTip("指令立即數")
            im.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LB.setItem(i, 5, im)
            inst = QTableWidgetItem(str(LB.inst) if LB.inst is not None else None)
            inst.setToolTip("指令的id")
            inst.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.LB.setItem(i, 6, inst)
            i += 1

    def initRS(self):
        def init(RS, i):
            name = QTableWidgetItem(RS.name)
            name.setToolTip(RS.name)
            name.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 0, name)
            busy = QTableWidgetItem('YES' if RS.busy else None)
            busy.setToolTip("保留站是否被占用")
            busy.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 1, busy)
            remain = QTableWidgetItem(str(RS.remain) if RS.remain is not None else None)
            remain.setToolTip("剩餘的時間周期")
            remain.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 2, remain)
            fu = QTableWidgetItem(RS.FU)
            fu.setToolTip("執行該指令的功能部件名")
            fu.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 3, fu)
            op = QTableWidgetItem(RS.op)
            op.setToolTip("指令操作碼")
            op.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 4, op)
            vj = QTableWidgetItem(str(RS.vj) if RS.vj is not None else None)
            vj.setToolTip("Vj")
            vj.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 5, vj)
            vk = QTableWidgetItem(str(RS.vk) if RS.vk is not None else None)
            vk.setToolTip("Vk")
            vk.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 6, vk)
            qj = QTableWidgetItem(RS.qj)
            qj.setToolTip("Qj")
            qj.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 7, qj)
            qk = QTableWidgetItem(RS.qk)
            qk.setToolTip("Qk")
            qk.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.RS.setItem(i, 8, qk)
        i = 0
        for ARS in self.tomasulo.RS.ARS.values():
            init(ARS, i)
            i += 1
        for MRS in self.tomasulo.RS.MRS.values():
            init(MRS, i)
            i += 1

    def initregister(self):
        status = QTableWidgetItem(self.tomasulo.PC.status)
        status.setToolTip(self.tomasulo.PC.status)
        status.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.register.setItem(0, 0, status)
        value = QTableWidgetItem(str(self.tomasulo.PC.value) if self.tomasulo.PC.value is not None else None)
        value.setToolTip(str(self.tomasulo.PC.value) if self.tomasulo.PC.value is not None else None)
        value.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.register.setItem(1, 0, value)
        i = 1
        for register in self.tomasulo.register.values():
            status = QTableWidgetItem(register.status)
            status.setToolTip(register.status)
            status.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.register.setItem(0, i, status)
            value = QTableWidgetItem(str(register.value) if register.value is not None else None)
            value.setToolTip(str(register.value) if register.value is not None else None)
            value.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.register.setItem(1, i, value)
            i += 1

    def step(self):
        self.tomasulo.step()
        self.refresh()

    def steps(self, step):
        self.tomasulo.step(step)
        self.refresh()

    def autorun(self):
        if self.autobtn.text() == "自動運行":
            self.autobtn.setText("暫停")
            self.buttondisable(self.initbtn, self.stepbtn, self.stepsbtn, self.resultbtn, self.resetbtn)
            self.autorunthread.auto = True
            self.autorunthread.start()
        elif self.autobtn.text() == "暫停":
            self.autobtn.setText("自動運行")
            self.buttonenable(self.initbtn, self.stepbtn, self.stepsbtn, self.resultbtn, self.resetbtn)
            self.autostop.emit()


    def getresult(self):
        while self.tomasulo.end() is False:
            self.tomasulo.step()
        self.refresh()

    def initUI(self):
        self.initInst()
        self.initLB()
        self.initRS()
        self.initregister()

    def refresh(self):
        self.initUI()
        self.clock.display(self.tomasulo.clock)
        if self.tomasulo.end():
            if self.autobtn.text() == "暫停":
                self.autobtn.setText("自動運行")
            self.buttondisable(self.initbtn, self.stepbtn, self.stepsbtn, self.autobtn, self.resultbtn)
            self.buttonenable(self.resetbtn)
            msg = QMessageBox.information(self, "執行完畢", "Tomasulo模擬器運行完畢！", QMessageBox.Ok, QMessageBox.Ok)

    def reset(self):
        self.tomasulo.reset()
        self.initUI()
        self.clock.display(0)
        if self.autobtn.text() == "暫停":
            self.autobtn.setText("自動運行")
        self.buttonenable(self.initbtn, self.stepbtn, self.stepsbtn, self.autobtn, self.resultbtn)

    def buttondisable(self, *args):
        for arg in args:
            arg.setEnabled(False)

    def buttonenable(self, *args):
        for arg in args:
            arg.setEnabled(True)

    def stepsdialog(self):
        dialog = QDialog()
        dialog.setWindowTitle("請輸入執行步數")
        dialog.setWindowModality(Qt.ApplicationModal)
        line = QLineEdit(dialog)
        line.setAlignment(Qt.AlignLeft)
        line.setValidator(QIntValidator())
        line.setText('1')
        btn = QPushButton("確定", dialog)

        def btnclicked():
            self.steps(int(line.text()))
            dialog.close()
        btn.clicked.connect(btnclicked)

        layout = QHBoxLayout(dialog)
        layout.addWidget(line)
        layout.addWidget(btn)

        dialog.exec_()

    def initdialog(self):
        dialog = QDialog()
        dialog.setWindowTitle("請輸入指令")
        dialog.setWindowModality(Qt.ApplicationModal)
        text = QTextEdit(dialog)
        filebtn = QPushButton("從文件導入", dialog)
        btn = QPushButton("確定", dialog)

        def showfiledialog():
            fname = QFileDialog.getOpenFileName(self, "打開文件")
            if fname[0]:
                with open(fname[0], 'r') as f:
                    data = f.read()
                    text.setPlainText(data)
        filebtn.clicked.connect(showfiledialog)

        def btnclicked():
            lines = text.toPlainText().strip().split('\n')
            if len(lines) > 0:
                self.tomasulo.inst.clear()
                self.inst.clearContents()
                for line in lines:
                    line.strip()
                    if len(line) <= 3:
                        continue
                    self.tomasulo.insert_inst(line)
                self.reset()
            dialog.close()
        btn.clicked.connect(btnclicked)

        buttonlayout = QHBoxLayout()
        buttonlayout.addWidget(filebtn)
        buttonlayout.addStretch()
        buttonlayout.addWidget(btn)

        layout = QVBoxLayout(dialog)
        layout.addWidget(text)
        layout.addLayout(buttonlayout)

        dialog.exec_()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出', "是否退出模擬器?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1].lower() == 'gui'):
        app = QApplication(sys.argv)
        w = Tomasulo()
        sys.exit(app.exec_())
    elif len(sys.argv) == 2 and sys.argv[1].lower() == 'core':
        toma = TomasuloCore()
        for line in initial:
            toma.insert_inst(line)
        print (toma)
        while True:
            for loader in Load.values():
                print (loader)
            for adder in Add.values():
                print (adder)
            for multer in Mult.values():
                print (multer)
            lin = input()
            if lin.lower() == "exit":
                break
            elif lin.lower() == "reset":
                toma.reset()
            else:
                toma.step(int(lin))
            print (toma)
            if toma.end():
                break
    else:
        pass
