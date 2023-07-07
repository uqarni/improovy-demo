import streamlit as st
from functions import ideator
import json
import os
import sys
from datetime import datetime
import redis



def main():

    # Create a title for the chat interface
    st.title("Improovy Bot")
    st.write("This bot is still in alpha. To test, first select some fields then click the button below.")

    st.write("These are standin variables to demonstrate the bot's ability to integrate variables into its instruction set.")
    
    #variables for system prompt
    name = st.selectbox('Seller Name', ('Joe', 'Susan', 'Mo'))
    lead_name = st.text_input("What is your name")
    booking_link = 'bookinglink.com/' 
    description = st.text_input("add project description here")
    address = st.text_input("type in address")
    if name is None or name == "":
        name = 'unknown'
    if lead_name is None or lead_name == "": 
        lead_name = 'unknown'
    if description is None or description == "":
        description = 'unknown'
    if address is None or address == "":
        address = 'unknown'
        
    redis_host = os.environ.get("REDIS_1_HOST")
    redis_port = 25061
    redis_password = os.environ.get("REDIS_1_PASSWORD")
    rd = redis.Redis(host=redis_host, port=redis_port, password=redis_password, ssl=True, ssl_ca_certs="/etc/ssl/certs/ca-certificates.crt")

    system_prompt = rd.get("carr@improovy.com-systemprompt-01").decode('utf-8')
    system_prompt = system_prompt.format(name = name, lead_name = lead_name, description = description, address = address, booking_link = booking_link)

    initial_text = rd.get("carr@improovy.com-initialtext-01").decode('utf-8')
    initial_text = initial_text.format(name = name, lead_name = lead_name, description = description, address = address, booking_link = booking_link)

    
    if st.button('Click to Start or Restart'):
        st.write(initial_text)
        restart_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('database.jsonl', 'r') as db, open('archive.jsonl','a') as arch:
        # add reset 
            arch.write(json.dumps({"restart": restart_time}) + '\n')
        #copy each line from db to archive
            for line in db:
                arch.write(line)

        #clear database to only first two lines
        with open('database.jsonl', 'w') as f:
        # Override database with initial json files
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": initial_text}            
            ]
            f.write(json.dumps(messages[0])+'\n')
            f.write(json.dumps(messages[1])+'\n')



    #initialize messages list and print opening bot message
    #st.write("Hi! This is Tara. Seems like you need help coming up with an idea! Let's do this. First, what's your job?")

    # Create a text input for the user to enter their message and append it to messages
    userresponse = st.text_input("Enter your message")
    

    # Create a button to submit the user's message
    if st.button("Send"):
        #prep the json
        newline = {"role": "user", "content": userresponse}

        #append to database
        with open('database.jsonl', 'a') as f:
        # Write the new JSON object to the file
            f.write(json.dumps(newline) + '\n')

        #extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        #generate OpenAI response
        messages, count = ideator(messages)

        #append to database
        with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')



        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            string = string + message["role"] + ": " + message["content"] + "\n\n"
        st.write(string)
            

if __name__ == '__main__':
    main()
