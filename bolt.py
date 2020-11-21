from boltiot import Bolt
from cs50 import SQL
from winsound import Beep
from time import localtime, sleep

db = SQL("sqlite:///maindb.db")

D_ID = input("Bolt device ID:")
A_KEY = input("API key:")
uname = input("Enter your Dankemo username:")

bolt_inst = Bolt(A_KEY, D_ID)

def main():
    while True:
        try:
            tnote = db.execute("SELECT note FROM journals WHERE username=:username AND date=CURRENT_DATE", username=uname)
            if not tnote:
                utime = db.execute("SELECT time FROM users WHERE username=:username", username=uname)[0]["time"]
                if localtime().tm_hour >= utime:
                    bolt_inst.digitalWrite(0, 'HIGH')
                    sleep(2)
                    bolt_inst.digitalWrite(0, 'LOW')           
            sleep(60)
        except Exception as e:
            print(e)
            sleep(60)

if __name__ == '__main__':
    main()