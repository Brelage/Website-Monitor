# Website-Monitor
Regularly monitors any websites you define and sends an Email if there seem to be problems with the connection or state of the websites.
Best used as a background process that runs 24/7 on a local server or in a containerized deployment.

## Features
- the script checks for the following things for the state of the websites:
    - whether the websites send back an http status-code below 400
    - whether the calls to any website time out (interval set to 10 seconds, can be adjusted)
    - whether there are any mentions of the word "error" or similar in the head of the website
- this script checks any websites you list in the website_list.json file. Every website gets tracked separately, so if only one of them starts having problems, then the program will send a notification only for that website.
- the intervall for checking the websites is slightly randomized (between 5-10 minutes). This intervall can easily be fine-tuned if need be. 
- the requests sent by the script are preloaded with headers and randomized user-agents, making it less likely for the script to be noticed as a bot by the website's server. 
- the script sends only a maximum of 4 Emails, after which it will keep checking the website's status, but won't send more Emails to avoid spamming.
- after finding a potential problem, the script uses exponential backoff approach to slow down the amount of calls sent to the faulty website. That way, the script only keeps sending more messages, if the problem persists over a longer period.
- the Emails sent by the script are created using html files, which allow for more modern and prettier formatting. 


## Setup
Here is a step by step explanation for how to set up this program:
1. clone the repository: 
```bash
git clone https://github.com/Brelage/Website-Monitor
```
2. run the setup script: 
```bash 
source setup.sh
```
3. input the websites into the website_list.json file
4. input your SMTP email credentials into the .env file
5. run the application: 
```bash 
python websiteMonitor.py
```

In order for the program to be able to run properly, you need to add at least one URL into the dictionary in the website_list.json file. 
The program also needs the necessary information to properly be able to send an Email via SMTP. To set this up, you need to fill out the values of the variables listed in the .env file. If you don't, then the program will raise an error prompting you to add the values.


# Recommendations
To personalise the Email message, change the text in the Email_message.html files and make sure that you do not change the variables in the text that will be inserted into the Email dynamically via the program itself.
