import os

def write_exit_file(value):
    fp = open('ExitFile.txt','w')
    fp.write(value)
    fp.close()
    
if __name__== "__main__":
    write_exit_file('1')
    