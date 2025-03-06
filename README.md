# Website-Monitor
Regularly monitors a set of websites in the .json file with a slightly randomized interval between 5 and 10 minutes and sends an Email to notify the receivers if one of the websites cannot be reached. Best used as a background process that runs 24/7 on a local server. 


# Setup
To get this program to run, you need to install the requirements listed in the requirements.txt file. To do so, simply run the setup shellscript.

Here is a step by step explanation for how to set up this program in your own IDE through the integrated terminal:
1. clone the repository: 
```bash
git clone https://github.com/Brelage/Website-Monitor
```
2. navigate into the project: 
```bash
cd WebsiteMonitor
```
3. run the setup script: 
```bash 
source setup.sh
```
4. activate the virtual environment: 
```bash source .venv/bin/activate
```
5. input the websites into the website_list.json file
6. input the email credentials into the .env file
7. run the application: 
```bash 
python websiteMonitor
```

In order for the program to be able to run properly, you need to add at least one URL into the dictionary in the website_list.json file. This program supports monitoring of multiple websites, just add them to the dictionary separated by commas.
The program also needs the necessary information to properly be able to send an Email. To set this up, you need to fill out the values of the variables listed in the .env file. If you don't then the program will raise an error prompting you to add the values.


# Recommendations
To personalise the Email message, change the text in the Email_message.txt file and make sure that you do not change the variables in the text that will be inserted into the Email dynamically via the program itself.
