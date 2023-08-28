import sqlite3
from gpiozero import LED, Button
import time

class StatusEntry:
    def __init__(self, status_id: int, time_stamp: float, led_active: bool):
        self.status_id = status_id
        self.time_stamp = time_stamp
        self.led_active = led_active

class ORM:
    def __init__(self, file_name: str):
        self.connection = sqlite3.connect(file_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        
    def get_status_entries(self) -> list[StatusEntry]:
        sql = '''SELECT * FROM status_entry;'''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        
        status_entries = []
        for i in result:
            status_entries.append(StatusEntry(i[0], float(i[1]), bool(i[2])))
        return status_entries
    
    def save_status_entry(self, status_entry: StatusEntry):
        self.cursor.execute("INSERT INTO status_entry (time_stamp, led_active) VALUES (?, ?)",
                           (status_entry.time_stamp, status_entry.led_active))
        print('Saved entry')
        self.connection.commit()
        
class Main:
    def __init__(self):
      self.orm = ORM('main.db')
      self.led = LED(22)
      self.led.off()
      
      self.button = Button(24)
      self.button.when_pressed = self.pressed
      
      self.led_active = False
      
    def pressed(self):
        if self.led_active:
            self.led_off()
            self.led_active = False
        else:
            self.led_on()
            self.led_active = True
        
    def led_on(self):
      self.led.on()
      
      #Entry to database
      self.orm.save_status_entry(StatusEntry(-1, time.time(), True))
      
    def led_off(self):
      self.led.off()
      
      # Entry to database
      self.orm.save_status_entry(StatusEntry(-1, time.time(), False))

if __name__ == '__main__':
    main = Main()
    for i in main.orm.get_status_entries():
        print(f'EINTRAG: status_id={i.status_id}, time_stamp={i.time_stamp}, led_active={i.led_active}')
