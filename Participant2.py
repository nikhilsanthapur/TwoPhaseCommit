# Paricipant2 process
import time
import socket     
from random import *
from threading import *

class ParticipantProcess:
    def __init__(self):
        try:
            self.participantid="Participant_B"
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect((socket.gethostname(), 7891)) 
            self.soc.sendall("Participant_B".encode()) 
            self.connectAttempt=0
            #print(f"Distribution Connection Info   >>> {self.soc} ")
            print(f"<<{self.participantid}>> Connected to Coordinate Server") 
            self.connectToCoordinator()
        except Exception as e:	
            print(f"Participant Constructor error:{e}") 
	
    def connectToCoordinator(self):
        #randval = randint(1, 10)
        msgFromCoordinator=""
        timer=0
        msgAfterTimeOut=""
        while (True):
            try:
                def readFromCoordinator():
                    nonlocal msgAfterTimeOut
                    nonlocal msgFromCoordinator
                    nonlocal timer
                    while(msgFromCoordinator==""):
                        try:
                            timer=timer+1
                            if (timer == 10):
                                timer = 0 
                                print("Timeout due to Coordinator not responded ") 
                                msgAfterTimeOut = "rollback" 
                                break
 
                            else:
                                msgFromCoordinator = self.soc.recv(1024).decode('utf-8') 
                                timer = 0 
                                break
                            sleep(3)
                        except Exception as e:
                            print("Coordinator server down >>> not responding")
                            #time.sleep(0.5)
                            if self.connectAttempt == 0:
                                self.connectAttempt += 1
                                def reConnectCoordinator():
                                    while True:
                                        try:
                                            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                            self.soc.connect((socket.gethostname(), 7891)) 
                                            #print(f"Reconnecting to Coordinator: >>>{self.soc}")
                                            print(f"<<{self.participantid}>> Reconnected to Coordinate Server")
                                            self.soc.sendall("Participant_B".encode())
                                            if self.connectAttempt == 1:
                                                self.connectAttempt = 0
                                            break
                                        except Exception as e1:
                                            print("Coordinator disconnected")
                                            time.sleep(1)
                                thrd = Thread(target=reConnectCoordinator)
                                thrd.start()
                                timerThread.cancel()
                                return
                timerThread=Timer(3,readFromCoordinator)
                timerThread.start() 
                timerThread.join()

                if(len(msgFromCoordinator)>0):
                     print(f"Coordinator msg  <<< {msgFromCoordinator}") 
                if msgFromCoordinator == "Ready For Poling" and msgAfterTimeOut == "rollback":
                    self.soc.sendall("Fail".encode()) 
                    print("Participant_B    >>>  Response Fail Due to Coordinator TimeOut")
                    msgFromCoordinator=""
                    msgAfterTimeOut = ""                      
                elif (msgFromCoordinator=="Ready For Poling"):
                    randval = randint(1, 10)
                    print(f"Random value{randval}")
                    if (randval % 7 != 0):
                        self.soc.sendall("Ready".encode())
                        print("Participant_B    >>>   response Ready") 
                    else :
                        self.soc.sendall("Fail".encode()) 
                        print("Participant_B    >>>   Response Fail") 
						
                    msgFromCoordinator="" 
					

                elif (msgFromCoordinator=="commit"):
                        self.soc.sendall("Task Completed and lock rollbacked".encode()) 
                        print("Participant_B    >>>   Response Task Completed and lock rollbacked") 
                        msgFromCoordinator="" 
                elif (msgFromCoordinator=="rollback") :
                        self.soc.sendall("Task aborted and lock rollbacked".encode()) 
                        print("Participant_B    >>>   Response Task aborted and lock rollbacked") 
                        msgFromCoordinator=""
            except Exception as e:
                #print("connectToCoordinator inner error:" , e)
                print("Participant_B    >>>   Response Task aborted and lock rollbacked") 
                break 


if(__name__ == "__main__"): 
   ParticipantProcess()
