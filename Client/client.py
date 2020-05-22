import hashlib, socket, threading, sys, datetime, os, getpass
from pathlib import Path


def startUpC():#startup asking if 1st time users
        access=False
        while access == False:
                w=input('is it your 1st time here? :')
                w=w.lower()
                if w == 'yes':#new users
                        s.send(w.encode('ascii'))
                        access=True
                        newUserC()
                elif w == 'no':#exisiting
                        s.send(w.encode('ascii'))
                        access=True
                        locateUserC()
                        
                else:
                        print('thats wrong')

def locateUserC(): #checks file for username
        uName= input('please provide your username :')
        s.send(uName.encode('ascii'))
        found=s.recv(1024).decode('ascii')
        if found == 'found':
                checkPassC(uName)
                adminCheck(uName)
   
        if found == 'not found':
                print('sorry thats not a correct username, please reload and retry, goodbye')
                sys.exit()
                
def newUserC():#generates new user
        created=False
        while created==False:
                newUser=input('Please provide a new username :')
                s.send(newUser.encode('ascii'))
                ans=s.recv(1024).decode('ascii')
                if ans == 'yes':
                        print('Username is avaliable')
                        newPassC(newUser)
                        created= True
                if ans == 'no':
                        print('unable to create this username pick another')
        return
        
def newPassC(newUser): #adds password for new user
        match=False
        while match== False:
                passw=getpass.getpass(prompt='Please enter Password:',stream=None)
                #getpass hides the input from echoing to assist with security
                newpass=getpass.getpass(prompt='Please Renter Password:',stream=None)
                #prompt is what its written instead of input stream is set to none to default the terminal
                if passw == newpass:#if passwords match run script
                        newpass=newpass.encode('utf-8')
                        newpass=hashlib.sha256(newpass)
                        newpass=newpass.hexdigest()
                        s.send(newpass.encode('ascii'))
                        match=True
                else:
                        print('Passwords didnt match please retry')
        return                                
     
def checkPassC(uName):#checks password for existing user
        
        pWord=getpass.getpass(prompt='Password:',stream=None)
        pWord=pWord.encode('utf-8')#needs to be encoded before hashing
        pWord=hashlib.sha256(pWord)
        pWord=pWord.hexdigest()
        s.send(pWord.encode('ascii'))
        ans=s.recv(1024).decode('ascii')
        if ans == 'success':
                print('successfully logged in')
                return True
        else:
                print('credentials incorrect. terminating connection please retry')
                sys.exit()

def adminCheck(uName):#checks if the username is admin. if it is run the recv data section
        admin=s.recv(2014).decode('ascii')
        if admin== 'yes':
                recieveData()
                return     
        else:
                return
###        above is login section
        
def recieveData():#recv data bit for admin only
        data=input('do you want to get updated user info?')
        data=data.lower()
        s.send(data.encode('ascii'))
        if data == 'yes':
                filesize=s.recv(1024).decode('ascii')#recieves the file size from server
                print(filesize)
                print('recv bit')
                print('recieving data from server')
                filepath=os.path.join('python client server/Client/Downloads','userlist.txt')#specify the file location 
                if not os.path.exists('python client server/Client/Downloads'):
                        #if file location doesnt exist -
                        os.makedirs('python client server/Client/Downloads')#- create location
                f=open(filepath,'wb+')#write to file
                l=s.recv(1024)
                total=len(l)
                while l:
                        print('recieving......')
                        f.write(l)
                        if (str(total) != filesize):#checks if the total length is less than filesize
                                print('trying to recieve')
                                l=s.recv(1024)
                                total = total + len(l)
                        else:
                                break
                f.close()
                print('admin data has been recieved successfully')
                return
        else:
                return

##above is sending admin data
        
def receiveMsg(sock): #recv messages
    serverDown = False
    while clientRunning and (not serverDown):
        try:#try for 
            msg = sock.recv(1024).decode('ascii')
            print(time,msg)
        except:
            print('Server is Down. You are now Disconnected. Press enter to exit...')
            serverDown = True

#start socket 
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host=str(socket.gethostbyname(socket.gethostname()))
port=5858
try:
        s.connect((host,port))
except socket.error:
        print('unable to connect')
        sys.exit()
time=datetime.datetime.now().strftime('%H:%M')
clientRunning=True
startUpC()#runs the login section
threading.Thread(target=receiveMsg, args=(s,),daemon=True).start()#sets up recv thread for client side
un=input('whats your screen name for this session?')#creates a screen name
s.send(un.encode('ascii'))
s.send('-list'.encode('ascii'))#sends 1st request to get list of users at start
#client now running
while clientRunning:#send messages out to server
        try:
                tempMsg=input('')
                msg=un+'>>'+tempMsg
                if '-quit' in msg:
                        s.send('-quit'.encode('ascii'))
                        clientRunning=False
                else:
                        s.send(msg.encode('ascii'))
        except IOError as e:
                if e.errno == 32:
                        print('error with thread')
                        sys.exit()
                      
        


