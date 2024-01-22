from threading import *
import time
from socket import *
#from os import *
import os

class  Protocol_TOPC(Thread): 
    noofparticipants=0
    participantstatus={}
    reply={'Participant_A':"false","Participant_B":"false","Participant_C":"false"}
    def __init__(self,coorid):
        Thread.__init__(self)
        self.commitstatus=0
        print(f"My ID: >>> ({coorid})") 
        self.logfile="coordinatorlog.txt"   
        
        if os.path.exists(self.logfile):
            try:
                with open(self.logfile, 'r') as f:
                    line = f.readline()
                    self.commitstatus = int(line.strip())
            except Exception as e:
                print("coordinator_log file read error:", e)
        else:
            try:
                with open(self.logfile, 'w') as f:
                    f.write(str(0))
                    self.commitstatus = 0
                print("File created")
            except Exception as e:
                print("coordinator_log file write error:", e)            
        timer = Timer(0, self.checkNoParticipants)
        timer.start()

    def initiateParticipant(self,conn):
        ptid=conn.recv(1024).decode() 
        print(f"{ptid} <<<Connected>>>")                
        if(ptid=='Participant_A' and Protocol_TOPC.noofparticipants>=3):
            Protocol_TOPC.participantstatus[ptid]='reconnected'
            self.trasactionPending(ptid,conn)
        elif(ptid=='Participant_A'):
            Protocol_TOPC.participantstatus[ptid]='connected'
            self.participant1=self.Participant(ptid,conn)
            
        elif(ptid=='Participant_B' and Protocol_TOPC.noofparticipants>=3):
            Protocol_TOPC.participantstatus[ptid]='reconnected'
            self.trasactionPending(ptid,conn)
        elif(ptid=='Participant_B'):
            Protocol_TOPC.participantstatus[ptid]='connected'
            self.participant2=self.Participant(ptid,conn)
            
        elif(ptid=='Participant_C' and Protocol_TOPC.noofparticipants>=3):
            Protocol_TOPC.participantstatus[ptid]='reconnected'
            self.trasactionPending(ptid,conn)
        elif(ptid=='Participant_C'):
            Protocol_TOPC.participantstatus[ptid]='connected'
            self.participant3=self.Participant(ptid,conn)
            #self.checkNoParticipants()

    def saveStatusToLogFile(self, file, value):
        with open(file, 'w') as f:
            f.write(str(value))

    def extractStatusFromLogFile(self, file):
        with open(file, 'r') as f:
            value = int(f.read())
        return value   
    
    class  Participant(Thread):      
        def __init__(self,myid,conn):
            Thread.__init__(self)
            self.timecounter=0
            self.myid=myid
            self.conn=conn
            Protocol_TOPC.noofparticipants=Protocol_TOPC.noofparticipants+1
            
        def writeMessageToParticipants(self,sendmsg):
            try:
               self.conn.sendall(sendmsg.encode())
               print(f"Message to {self.myid} >>> {sendmsg}")  
            except Exception as e:
              #print("write to participant message error:",e)
              print(f"Partipant {self.myid} >>> not resonding")   

        def readMessageFromParticipants(self):
            msgFromParticipantst=""
            def readMessage():
                nonlocal msgFromParticipantst  
                while(msgFromParticipantst==""):
                    try:
                        self.timecounter=self.timecounter+1
                        if(self.timecounter==10): 
                            if(Protocol_TOPC.reply[self.myid]!='Ready'):            
                              self.timecounter=0  
                              print(f"timeout due to {self.myid} not responded ")  
                              print(f">>> Reply from {self.myid} is rollback")  
                              msgFromParticipantst="rollback"
                            else:
                               break   
                            #break
                        else:
                            msgFromParticipantst=self.conn.recv(1024).decode()
                            print(f"Reply from {self.myid} <<< {msgFromParticipantst}")  
                            Protocol_TOPC.reply[self.myid]=msgFromParticipantst
                            self.timecounter=0  
                            #break
                    except Exception as e:
                        print(f"client {self.myid} >>> not responding")
                        #break 
                        time.sleep(1)
            t=Timer(2,readMessage)
            t.start() 
            t.join()
            return msgFromParticipantst  
     

    def checkNoParticipants(self):
        while(True):
            try:
              if(Protocol_TOPC.noofparticipants==3):
                self.start()
                break
              time.sleep(5)                     
            except Exception as e:
                   print("Verificatin of participants error:",e)
                   break

            
    def run(self):
        
        print("Coordinator 2PC communication Voting initiated:")
        try:
            if(self.commitstatus==0):      
                  print("Ready For Poling")
                  time.sleep(2)
                  self.participant1.writeMessageToParticipants("Ready For Poling") 
                  self.participant2.writeMessageToParticipants("Ready For Poling") 
                  self.participant3.writeMessageToParticipants("Ready For Poling") 
                  paricipant_msg1=self.participant1.readMessageFromParticipants() 
                  paricipant_msg2=self.participant2.readMessageFromParticipants() 
                  paricipant_msg3=self.participant3.readMessageFromParticipants() 
                  time.sleep(2) 
                  
                  if(paricipant_msg1 =="Ready" and  paricipant_msg2 =="Ready"  and paricipant_msg3 =="Ready"):
                    self.participant1.writeMessageToParticipants("commit") 
                    #print("A")
                    updatedValue = self.extractStatusFromLogFile(self.logfile) + 1
                    #print("B")
                    self.saveStatusToLogFile(self.logfile, updatedValue)
                    #print("C")
                    time.sleep(2)

                    self.participant2.writeMessageToParticipants("commit") 
                    updatedValue = self.extractStatusFromLogFile(self.logfile) + 1
                    self.saveStatusToLogFile(self.logfile, updatedValue)
                    time.sleep(2)

                    self.participant3.writeMessageToParticipants("commit") 
                    updatedValue = self.extractStatusFromLogFile(self.logfile) + 1
                    self.saveStatusToLogFile(self.logfile, updatedValue)
                    time.sleep(2)                    
                  else:
                    self.participant1.writeMessageToParticipants("rollback") 
                    time.sleep(2)                    
                    self.participant2.writeMessageToParticipants("rollback") 
                    time.sleep(2)                    
                    self.participant3.writeMessageToParticipants("rollback") 
                    time.sleep(2)                    
            else:
                    self.participant1.writeMessageToParticipants("commit") 
                    updatedValue = self.extractStatusFromLogFile(self.logfile) + 1
                    self.saveStatusToLogFile(self.logfile, updatedValue)
                    time.sleep(2)

                    self.participant2.writeMessageToParticipants("commit") 
                    updatedValue = self.extractStatusFromLogFile(self.logfile) + 1
                    self.saveStatusToLogFile(self.logfile, updatedValue)
                    time.sleep(2)

                    self.participant3.writeMessageToParticipants("commit") 
                    updatedValue = self.extractStatusFromLogFile(self.logfile) + 1
                    self.saveStatusToLogFile(self.logfile, updatedValue)
                    time.sleep(2)

            self.participant1.readMessageFromParticipants() 
            self.participant2.readMessageFromParticipants() 
            self.participant3.readMessageFromParticipants() 
            self.saveStatusToLogFile(self.logfile,0)
        except Exception as e:
            print("Error in  Participants Communication:",e) 


    def trasactionPending(self,processid,conn):
        try:
               if(Protocol_TOPC.reply[processid]=='Ready'):
                   sendmsg="commit"
               else:
                   sendmsg="rollback"
               conn.sendall(sendmsg.encode())
               print(f"Message to {processid} >>> {sendmsg}")
               msgFromParticipantst=conn.recv(1024).decode()
               print(f"Reply from {processid} <<< {msgFromParticipantst}")   
        except Exception as e:
              #print("write to participant message error:",e)
              print(f"Partipant {processid} >>> not resonding") 
        


if(__name__ == "__main__"): 
      try:
             P_TPC=Protocol_TOPC("Coordinator")
             host = gethostname()    
             port = 7891
             
             #print(f"hostname:{host}")
             #print(f"port:{port}")
             with socket(AF_INET, SOCK_STREAM) as s:
                  s.bind((host, port))
                  s.listen(3)
                  #print(f"Server Socket >>> {s}")
                  print(f"Sever started to process Participants")
                  while(True):
                     conn, addr = s.accept()  
                     #print(f"Client connection >>> {conn},{addr}")
                     P_TPC.initiateParticipant(conn)

                     time.sleep(4)


      except Exception as e:
           print("Participants connection error:",e)
           
 

