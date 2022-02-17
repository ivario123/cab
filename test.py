import sys
from email.mime import base
import requests
import configparser
import json
import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed

config = configparser.ConfigParser()
config.read("config/auth.cfg")
remaining_assignments = []

class assignment:
    
    def __init__(self,task) -> None:
        # Task 1 is the date the task is due
        # Task 0 is the task title
        assert type(task[1]) == str
        # split the date time info
        due = task[1]
        due = due.split('T')
        # This could be cleaned up but I can't be botherd
        due[0] = due[0].split('-')
        due[0] = [int(val) for val in due[0]]
        # Convert to datetime
        date = datetime.datetime(due[0][0],due[0][1],due[0][2])    


        self.weekdays = ["Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag"]
        self.months = ["Januari","Februari","Mars","April","Maj","Juni","Juli","Augusti","September","Oktober","November","December"]
        self.deadline_arr = due[0]
        # Get current month as string
        self.month = self.months[date.month-1]
        # Get current week day as string
        self.day = self.weekdays[date.weekday()]      
        self.lable = task[0]
        self.date_time = date
        self.deadline_hours = due[1][:5]
    def get_remaining_days(self):
        return (self.date_time-datetime.datetime.now()).days+1
    def __repr__(self) -> str:
        return f"""Uppgiften : {self.lable}
har deadline {self.day} den {self.deadline_arr[2]}{'a' if self.deadline_arr[2] <=1 else 'e'} {self.month} kl {self.deadline_hours}
vilket är om {self.get_remaining_days()} {'dag' if abs(self.get_remaining_days()) == 1 else 'dagar'}"""
    def __str__(self) -> str:
        return self.__repr__()


def get_data(course_id, ):
    base_url = f"https://ltu.instructure.com:443/api/v1/courses/{course_id}/assignments?include[]=all_dates"
    key = config["API"]["API_KEY"]
    result = requests.get(base_url,headers={"Authorization":f"Bearer {key}"}).text
    JSON = json.loads(result)
    tasks = [(submission["name"] , submission["due_at"]) for submission in JSON]
    return [assignment(task) for task in tasks]

def send_next_assignment(assignments):
    webhook = DiscordWebhook(url=config["API"]["DISCORD_WEBHOOK"])
    # Formatting the message to look nice
    content = str(assignments[0])
    



    webhook.execute()
    config.set("LAST_REPORTED","DEADLINE_DATE",str(assignments[0].deadline_arr))
    config.set("LAST_REPORTED","TASK_NAME",assignments[0].lable)
    # Writing our configuration file to 'example.ini'
    with open('config/auth.cfg', 'w') as configfile:
        config.write(configfile)

def update_data(assignments):
    prev_next = assignments[0] if len(assignments) > 0 else 0
    assignments = [assignment for assignment in get_data(sys.argv[1]) if assignment.get_remaining_days()>0]
    if(assignments[0] != prev_next and assignments[0].lable != config["LAST_REPORTED"]["TASK_NAME"] and
        str(assignments[0].deadline_arr) != config["LAST_REPORTED"]["DEADLINE_DATE"]):
        send_next_assignment(assignments)
    return assignments
if __name__ == "__main__":
    args = sys.argv
    if len(sys.argv) != 2:
        print("=====================")
        print("Specify the course id")
        print("=====================")
        exit()
    while 1:
        remaining_assignments = update_data(remaining_assignments)
        
    