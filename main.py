from playwright.sync_api import sync_playwright
from groq import Groq
import subprocess
import base64
import re
import os 

client = Groq(api_key="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")

def operating_system():
    return os.sys.platform == "darwin"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def getResponse(image_path):
    base64_image = encode_image(image_path)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Given the image of an event ad/poster, return the information in the following format: \n DATE: 'Month day, 2025' \n START TIME: 'HH:MM AM/PM' \n END TIME: 'HH:MM AM/PM' \n EVENT: 'Name of Event' \n URL: 'url' \n LOCATION: 'address' \n \n Use NONE if information is not present. Use exactly the same format. \n \n Do not return anything else or use markdown. \n \n"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-90b-vision-preview",
    )
    return chat_completion.choices[0].message.content

def parse_response(response):
    global date, start_time, end_time, event, url, location
    date_match = re.search(r"DATE:\s*([A-Za-z]+ \d{1,2}, \d{4})", response)
    start_time_match = re.search(r"START TIME:\s*([\d:]+\s*[APMampm]+)", response)
    end_time_match = re.search(r"END TIME:\s*([\d:]+\s*[APMampm]+)", response)
    event_match = re.search(r"EVENT:\s*(.+)", response)
    url_match = re.search(r"URL:\s*(.+)", response)
    location_match = re.search(r"LOCATION:\s*(.+)", response)

    date = date_match.group(1) if date_match else ""
    start_time = start_time_match.group(1) if start_time_match else ""
    end_time = end_time_match.group(1) if end_time_match else ""
    event = event_match.group(1) if event_match else ""
    url = url_match.group(1) if url_match and url_match.group(1) != "NONE" else ""
    location = location_match.group(1) if location_match else ""

    return date, start_time, end_time, event, url, location
    
# nam.le94568@gmail.com
def main():
    print("""
  ____                      __     ___     _             
 / ___| _   _ _ __   ___ _ _\ \   / (_)___(_) ___  _ __  
 \___ \| | | | '_ \ / _ \ '__\ \ / /| / __| |/ _ \| '_ \ 
  ___) | |_| | |_) |  __/ |   \ V / | \__ \ | (_) | | | |
 |____/ \__,_| .__/ \___|_|    \_/  |_|___/_|\___/|_| |_|
             |_|  
    """)
    print("""
What would you like to use?
(1) Apple Calendar [MacOS Only]
(2) Todoist [Cross-Platform]
(3) Exit
""")
    choice = input("Enter your choice: ")
    image_path = input("Drag and drop the image here: ") # if operating_system() else input("Drop the image here: ")
    response = getResponse(image_path)
    parse_response(response)

    if choice == "1":
        if operating_system():
            apple_script = f'''
tell application "Calendar"
    tell calendar "Home"
        set eventStartDate to date "{date} {start_time}"
        set eventEndDate to date "{date} {end_time}"
        make new event with properties {{summary:"{event}", start date:eventStartDate, end date:eventEndDate, location:"{location}", url:"{url}"}}
    end tell
end tell'''
            subprocess.run(["osascript", "-e", apple_script], check=True)
        else:
            print("This function only runs on macOS.")
            return
    elif choice == "2":
        email = input("Todoist Email: ")
        password = input("Todoist Password: ")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://app.todoist.com/auth/login")
            page.fill('input[placeholder="Enter your email..."]', email)
            page.fill('input[placeholder="Enter your password..."]', password) 
            page.click('button[aria-describedby="agreement-footnote"]')   
            page.click('button:text("Add task")')
            page.fill('p[class="is-empty is-editor-empty"]', event + "@" + location)
            page.click('span[class="date date_today"]')
            page.fill('input[aria-label="Type a date"]', date + " " + start_time)
            page.keyboard.press('Enter')
            page.click('button[data-testid="task-editor-submit-button"]')
            page.wait_for_timeout(5000)
    elif choice == "3":
        exit()
    elif choice == "4":
        exit()
    else:
        print("Invalid choice. Please try again.")
    

main()
