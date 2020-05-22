import hashlib, socket, threading, sys, datetime, errno, os, sqlite3, pathlib


def startUp():#start up section to see if its a new user
    ans=client.recv(1024).decode('ascii')
    if ans == 'no':
        locateUser()
    elif ans == 'yes':
        newUser()
    else:
        print('Error')
        
def locateUser():
    found=False
    while found==False:
        userN=client.recv(1024).decode('ascii')
        sql="SELECT USERID FROM shadow WHERE USERID='%s';"%userN
        cursor.execute(sql)
        results=cursor.fetchone()
        if results is None:
            client.send('not found'.encode('ascii'))
            print('Access Denied : No user found')
            client.close()
        else:
            client.send('found'.encode('ascii'))
            print('found')
            found=True   
    if found==True:
        check = checkPass(userN)
        if check:
            client.send('success'.encode('ascii'))
            print('Access Granted')
            adminCheck(userN)
            return userN
        else:
            client.send('fail'.encode('ascii'))
            print('Access Denied ')
            client.close()

     
def checkPass(userN): #checks password for existing user
    access= False
    passW=client.recv(1024).decode('ascii') #gets password from client
    check="SELECT KEY FROM shadow WHERE USERID='%s'"%userN #sql query made with username
    cursor.execute(check)#executes query
    result=cursor.fetchone()#fetches the result of execution
    for r in result:
        if passW in result:
            print('Key match with db')
            log.write('-user login-'+userN)
            return True
        else:
            print('Key doesnt match db')
            return False
            
def newUser():#generates new user
    created=False
    while created==False:
        user=client.recv(1024).decode('ascii')
        sql="SELECT USERID FROM shadow WHERE USERID='%s';"%user
        cursor.execute(sql)
        result=cursor.fetchone()
        if result is None:
            print(result)
            client.send('yes'.encode('ascii'))
            newPass(user)
            created=True
        
        else:
            client.send('no'.encode('ascii'))

    return    
        
def newPass(user):#adds password for new user
    passW=client.recv(1024).decode('ascii')
    writeTo="INSERT INTO shadow (USERID, KEY, ADMIN) VALUES('%s','%s','0')"%(user, passW)
    cursor.execute(writeTo)
    connection.commit()

    return 
    


def adminCheck(userN):#admin check section
        check="SELECT ADMIN FROM shadow WHERE USERID='%s'"%userN
        cursor.execute(check)
        result=cursor.fetchone()
        for r in result:
            if r == 1:
                client.send('yes'.encode('ascii'))
                print('Admin logged')
                senddata(client)
                return
            else:
                client.send('no'.encode('ascii'))
                return
            
## above is login section
            
def senddata(client):
    data=client.recv(1024).decode('ascii')
    print(data)
    if data == 'yes':
        #location=os.path.abspath('results.txt')#searches for file location
        print('Results file found: file at\n %s'%location)
        print('sending data')
        filesize=str(os.path.getsize(location))
        print(filesize)
        client.send(filesize.encode('ascii'))
        with open(location,'rb') as f:
            l=f.read(1024)
            while l:
                print('Sending....')
                client.send(l)
                l=f.read(1024)
            print('Data Sent')
            f.close()
        return
    else:
        return

##above is to send file to admin client

def handleClient(client, screenName):#handles client
    clientConnected=True
    while clientConnected:
        try:#waits for message coming in from client and does different depending on message
            msg=client.recv(1024).decode('ascii')
            response='Number of People Online\n'
            if '-list' in msg:
                clientNo=0
                for name in keys:
                    clientNo += 1
                    response=response+str(clientNo)+'::'+name+'\n'
                client.send(response.encode('ascii'))
            elif '-quit' in msg:
                response='Stopping Session and exiting..'
                client.send(response.encode('ascii'))
                for k,v in screenNames.items():
                    v.send((screenName+' has left the group\n').encode('ascii'))
                print(time,screenName+' logged out')
                screenNames.pop(screenName)#removes the screenname from the users list
                clientConnected=False

            else:
                print(time,msg)
                for k,v in screenNames.items():
                    v.send(msg.encode('ascii'))
        except:
            response='theres been an error'
            print(response)
            client.send(response.encode('ascii'))


#db locate and connect and define cursor            
dbSetup=os.path.join('db/user.db')
connection= sqlite3.connect(dbSetup)
cursor=connection.cursor()

#socket set up
time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host=str(socket.gethostbyname(socket.gethostname()))
port=5858
try:#try to bind to host and port
    s.bind((host,port))
except socket.error:#if bind doesnt work as socket busy etc prints fail and exits to stop error
    print('Binding Failed')
    sys.exit()
s.listen()#if bind ok listens to post
print('Server Now Ready.....')
print('IP of Server:%s'%host)
screenNames={}#dic of screen names as keys and client addresses as values
#server running section
serverRunning=True
while serverRunning:
    location=os.path.abspath('results.txt')
    log=open(location,'a+')#opens a results file to write log info 
    client,address=s.accept()#accepts incoming connections
    log.write('\n'+str(time)+ str(address)+'joined:')
    try:
        startUp()#starts the login process
        screenName=client.recv(1024).decode('ascii')
        #gets a generic screen name from client
        keys=screenNames.keys()
        log.write(' screenname-'+screenName+'\n')
        print(time,'%s connected to the server'%str(screenName))
        client.send('Welcome to Messenger. \nTo chat, just type your message,\nThe commands are -list for list of current members or -quit to quit'.encode('ascii'))
        #if screenname not in list of screennames add them to it
        if(screenName not in screenNames):
            for k,v in screenNames.items():
                v.send((screenName+' has joined the group\n').encode('ascii'))
            screenNames[screenName]=client
            print("Current Clients:")
            print(keys)#list of clients
            try:
                #try to create a thread for handling clients
                threading.Thread(target=handleClient,args=(client,screenName,)).start()
            except:
                #if thread doesnt work remove client from list and close their connection
                print('Threading Error')
                screenNames.pop(screenName)
                s.close()
    except socket.error as e:#exception error for broken pipes (32)
        if e.errno == 32:
            screenNames.pop(screenName)
            clientConnected=False


