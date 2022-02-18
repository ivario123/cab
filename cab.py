import sys
import requests
import configparser
import json
import datetime
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

auth = configparser.ConfigParser()
auth.read("config/auth.cfg")
app_cfg = configparser.ConfigParser()
app_cfg.read("config/app.cfg")
remaining_assignments = []

weekdays = ["Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag"]
months = ["januari","februari","mars","april","maj","juni","juli","augusti","september","oktober","november","december"]
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
        
        self.deadline_arr = due[0]
        # Get current month as string
        self.month = months[date.month-1]
        # Get current week day as string
        self.day = weekdays[date.weekday()]      
        self.lable = task[0]
        self.date_time = date
        self.deadline_hours = due[1][:5]
        self.url = task[2]

    # Formats the date to look nice
    def format_date(self):
        return f"""{self.day} den {self.deadline_arr[2]}{'a' if self.deadline_arr[2] <=1 else 'e'} {self.month} kl {self.deadline_hours}
vilket är om {self.get_remaining_days()} {'dag' if abs(self.get_remaining_days()) == 1 else 'dagar'}"""


    # Returns days remaning untill deadline
    def get_remaining_days(self):
        return (self.date_time-datetime.datetime.now()).days+1


    # Returns a string repr of the assignment
    def __repr__(self) -> str:
        return f"""Uppgiften : {self.lable}
har deadline {self.format_date()}"""


    # Return repr
    def __str__(self) -> str:
        return self.__repr__()


    # comparing assignments
    def __eq__(self, __o: object) -> bool:
        if type(__o) == assignment:
            return self.deadline_arr == __o.deadline_arr and self.lable == __o.lable
        else:
            return self.lable == __o







def get_data(course_id, ):
    base_url = f"https://ltu.instructure.com:443/api/v1/courses/{course_id}/assignments?include[]=all_dates"
    key = auth["API"]["API_KEY"]
    result = requests.get(base_url,headers={"Authorization":f"Bearer {key}"}).text
    JSON = json.loads(result)
    tasks = [(submission["name"] , submission["due_at"],submission["html_url"]) for submission in JSON]
    return [assignment(task) for task in tasks]

def send_next_assignment(assignments):
    assignment = assignments[0]
    webhook = DiscordWebhook(url=auth["API"]["DISCORD_WEBHOOK"])

    def send_message():
        # Formatting the message to look nice
        webhook.content = "Hej! nu är det dags för en ny uppgift!"
        embed = DiscordEmbed(
        title="Nästa uppgift är", description=assignment.lable, color='03b2f8'
        )
        embed.add_embed_field(name="Den har deadline", value=assignment.format_date(), inline=False)
        embed.add_embed_field(name="Här är en länk till den!", value=assignment.url, inline=False)
        webhook.add_embed(embed)
        webhook.execute()
    
    send_message()
    app_cfg.set("LAST_REPORTED","DEADLINE_DATE",str(assignments[0].deadline_arr))
    app_cfg.set("LAST_REPORTED","TASK_NAME",assignments[0].lable)
    # Writing our configuration file to 'example.ini'
    with open('config/app.cfg', 'w') as configfile:
        app_cfg.write(configfile)

def update_data(assignments):
    prev_next = assignments[0] if len(assignments) > 0 else 0
    assignments = [assignment for assignment in get_data(sys.argv[1]) if assignment.get_remaining_days()>0]
    app_cfg.read("config/app.cfg")
    print(f"Current next assignment is {assignments[0]}")
    if(assignments[0] != prev_next 
        or assignments[0].lable != app_cfg["LAST_REPORTED"]["TASK_NAME"] 
        or str(assignments[0].deadline_arr) != app_cfg["LAST_REPORTED"]["DEADLINE_DATE"]):
        print("This is a new assignment! Notifying the discord")
        send_next_assignment(assignments)
    else:
        print("This is the same, gonna wait with the notification")
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
        time.sleep(60)  # sleep for a minute