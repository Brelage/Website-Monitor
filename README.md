# Website-Monitor
regularly monitors a set of websites in the .json file with a slightly randomized interval and sends an Email to notify the senders if one of the websites cannot be reached

# Setup
In order for the program to be able to run properly, you need to add at least one URL into the dictionary in the website_list.json file. This program supports monitoring of multiple websites, just add them to the dictionary separated by commas.
The program also needs the necessary information to properly be able to send an Email. To set this up, you need to fill out the values of the variables listed in the .env file. If you don't then the program will raise an error prompting you to add the values.

# Recommendations
To personalise the Email message, change the text in the Email_message.txt file and make sure that you do not change the variables in the text that will be inserted into the Email dynamically via the program itself.
