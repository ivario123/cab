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
language = app_cfg["GENERAL"]["language"]


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
        self.month = json.loads(app_cfg[language]["months"])[date.month-1]
        # Get current week day as string
        self.day = json.loads(app_cfg[language]["weekdays"])[date.weekday()]      
        self.lable = task[0]
        self.date_time = date
        self.deadline_hours = due[1][:5]
        self.url = task[2]

    # Formats the date to look nice
    def format_date(self):
        return app_cfg[language]["task_date_format"].format(
            self.day,
            self.deadline_arr[2],
            app_cfg[language]["singular_number_ending"] if self.deadline_arr[2] <=2 else app_cfg[language]["plural_number_ending"], # This i local to swede, change this if you need to
            self.month,
            self.deadline_hours,
            '\n',
            self.get_remaining_days(),
            app_cfg[language]["day_singular"] if abs(self.get_remaining_days()) == 1 else app_cfg[language]["day_plural"]
        )


    # Returns days remaning untill deadline
    def get_remaining_days(self):
        return (self.date_time-datetime.datetime.now()).days+1


    # Returns a string repr of the assignment
    def __repr__(self) -> str:
        return app_cfg[language]["task_format"].format(
            self.lable ,
            '\n',
            self.format_date())


    # Return repr
    def __str__(self) -> str:
        return self.__repr__()


    # comparing assignments
    def __eq__(self, __o: object) -> bool:
        if type(__o) == assignment:
            return self.deadline_arr == __o.deadline_arr and self.lable == __o.lable
        else:
            return self.lable == __o










def send_next_assignment(assignments):
    assignment = assignments[0]
    webhook = DiscordWebhook(url=auth["API"]["DISCORD_WEBHOOK"])

    def send_message():
        # Formatting the message to look nice
        webhook.content = app_cfg[language]["message_rubric"]
        embed = DiscordEmbed(
        title=app_cfg[language]["next_task_rubric"], description=assignment.lable, color='03b2f8'
        )
        embed.add_embed_field(name=app_cfg[language]["deadline_rubric"], value=assignment.format_date(), inline=False)
        embed.add_embed_field(name=app_cfg[language]["url_rubric"], value=assignment.url, inline=False)
        webhook.add_embed(embed)
        webhook.execute()
    
    send_message()
    app_cfg.set("LAST_REPORTED","DEADLINE_DATE",str(assignments[0].deadline_arr))
    app_cfg.set("LAST_REPORTED","TASK_NAME",assignments[0].lable)
    # Writing our configuration file to 'example.ini'
    with open('config/app.cfg', 'w') as configfile:
        app_cfg.write(configfile)

def get_data(course_id, ):
    base_url = app_cfg["GENERAL"]["api_course_assignments_url"].format(course_id)
    key = auth["API"]["API_KEY"]
    result = requests.get(base_url,headers={"Authorization":f"Bearer {key}"}).text
    JSON = json.loads(result)
    tasks = [(submission["name"] , submission["due_at"],submission["html_url"]) for submission in JSON]
    return [assignment(task) for task in tasks]


def check_for_new_data(assignments):
    prev_next = assignments[0] if len(assignments) > 0 else 0
    assignments = get_data(sys.argv[1]) # Trusting the canvas api to actually return only future assignments
    app_cfg.read("config/app.cfg")
    print(f"Current next assignment is {assignments[0]}")
    if(assignments[0] != prev_next):
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
        remaining_assignments = check_for_new_data(remaining_assignments)
        time.sleep(int(app_cfg["GENERAL"]["sleep_time"]))  # sleep for a minute