# Project2 Tomasulo模擬器實驗報告

設計思路
* 概述
o 按照要求設計了流水線，實現了3個加減法器，2個乘除法器，2個Load部件
o 實現了6個加減法保留站，3個乘除法保留站，3個Load Buffer
o 實現了32個浮點數暫存器，分別為F0到F31
* 硬件
o 見codes/tomasulo/hardware.py
o 實現基類HardWare，子類Adder、Multer、Loader，以及實例化規定數量的部件
* 保留站和Load Buffer
o 見codes/tomasulo/reservationstation.py
o 實現保留站基類RS，Load Buffer基類LoadBuffer，並實現ReservationStation類整合它們
* 流水線
o 見codes/tomasulo/tomasulo.py
o 實現類Tomasulo，其中：
* Tomasulo.step(n)方法模擬流水線經過n個時間週期的過程，n默認為1
*   while n > 0 : # n個時間週期
*      self .clock += 1
* 
*      # WRITEBACK
*      for LB in self . RS . LB .values():
*          ... #寫回Load Buffer中運行結束的指令結果
* 
*      for ARS in self . RS . ARS .values():
*          ... #寫回加減法保留站中運行結束的指令結果
* 
*      for MRS in self . RS . MRS .values():
*          ... #寫回乘除法保留站中運行結束的指令結果
* 
*      # EXCUTE
*      for LB in self . RS . LB .values():
*          if LB .busy is True and LB .remain is not None :
*              LB .remain -= 1 #剩餘週期-1
*              if LB .remain == 0 : #當剩餘週期為0，記錄指令執行完畢的時間
*                  if self .inst[ LB .inst].ExecComp is None and self .inst[ LB .inst].rs == LB .name:
*                      self .inst[ LB .inst].ExecComp = self .clock
*                  Load[ LB . FU ].free() #釋放Load部件資源
* 
*      for ARS in self . RS . ARS .values():
*          ... #同理
* 
*      for MRS in self . RS . MRS .values():
*          ... #同理
* 
*      # ISSUE
*      if self . PC .status is None and self . PC .value < len ( self .inst): #有指令需要發射
*          inst = self .inst[ self . PC .value]
*          res = self . RS .busy(inst)
*          if res is not None :
*              if inst.Issue is None :
*                  inst.Issue = self .clock #記錄指令發射時間和發射指令的保留站名
*                  if inst.op == Config. OP_LD :
*                      inst.rs = self . RS . LB [res].name
*                  elif inst.op == Config. OP_ADD or inst.op == Config. OP_SUB or inst.op == Config. OP_JUMP :
*                      inst.rs = self . RS . ARS [res].name
*                  elif inst.op == Config. OP_MUL or inst.op == Config. OP_DIV :
*                      inst.rs = self . RS . MRS [res].name
*                  else :
*                      return
* 
*              if inst.op == Config. OP_LD : #指令發射
*                  ...
*              elif inst.op == Config. OP_ADD or inst.op == Config. OP_SUB :
*                  ...
*              elif inst.op == Config. OP_MUL or inst.op == Config. OP_DIV :
*                  ...
*              elif inst.op == Config. OP_JUMP :
*                  ...
*              else :
*                  return
*              if inst.op != Config. OP_JUMP :
*                  self . PC .value += 1 # PC寄存器+1
*          else :
*              pass
* 
*      # EXCUTE HardWare
*      ready = []
*      for LB in self . RS . LB .values():
*          if LB .busy is True and LB . FU is None : #硬件就緒時取出保留站中就緒的指令
*              ready.append( LB )
*      ready = sorted (ready, key = lambda x :x.inst) #按照指令的id排序
*      loaderlist = []
*      for loader in Load.values():
*          if loader.status is None :
*              loaderlist.append(loader)
*      lenth = min ( len (ready), len (loaderlist))
*      for i in range (lenth):
*          loader = loaderlist[i] #將就緒的指令發送到硬件執行
*          LB = ready[i]
*          loader.op = self .inst[ LB .inst].op
*          loader.status = LB .name
*          loader.vj = LB .im
*          LB .remain = Config. TIME [loader.op]
*          LB . FU = loader.name
* 
*      ready = []
*      for ARS in self . RS . ARS .values():
*          ... #同理
* 
*      ready = []
*      for MRS in self . RS . MRS .values():
*          ... #同理
* 
     n -= 1 
* Tomasulo.reset()方法通過調用各個部件的free()方法來重置流水線
* Tomasulo.insert_inst()方法輸入指令
?UI說明界面
* 按鈕
o 輸入指令輸入框輸入指令，或者從文件導入


o 單步/多步執行單步調試或者輸入需要執行的步數來調試
o 自動運行自動運行模擬器，每秒運行一步直到結束，期間自動運行按鈕變為暫停按鈕，其他按鈕不可用

o 運行直到結束運行模擬器直到所有指令運行結束

此時只有清除按鈕可用，其他按鈕不可用

o 清除清空記錄，重置模擬器
?部署運行
* 編譯運行模擬器使用Python3.6編寫，GUI採用PyQt5，編譯運行需要先安裝Python3.6以及PyQt5的相關庫，命令行進入codes文件夾：
o 運行命令行界面python run.py core
o 運行GUI?python run.py或python run.py gui
* 運行Release版本： 進入release/dist文件夾運行run.exe
?測試
* 測試樣例在codes/static/test文件夾中，其中test0.nel為test2.nel為基本測例，剩下的為新編寫的測例，均通過了測試
* 其中test3.nel和test4.nel是綜合測試，test5.nel為JUMP測試，實現0到0x10的循環
* 測試結果均正確

