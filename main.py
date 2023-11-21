import streamlit as st
from functions import ideator
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client

#connect to supabase database
urL: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(urL, key)
data, count = supabase.table("bots_dev").select("*").eq("id", "mike").execute()
bot_info = data[1][0]

def main():

    # Create a title for the chat interface
    st.title("Improovy Bot")
    st.write("This bot is still in alpha. To test, first select some fields then click the button below.")

    st.write("These are standin variables to demonstrate the bot's ability to integrate variables into its instruction set.")
    
    #variables for system prompt
    name = 'Mike'
    booking_link = 'https://calendly.com/d/y7c-t9v-tnj/15-minute-meeting-with-improovy-painting-expert'
    initial_description = st.text_input("add project description here")

    #from contact
    lead_full_name = "John Doe"
    email = "johndoe@gmail.com"
    address=st.text_input('enter address')
    additional_notes = 'n/a'
    #from deal
    status='open'
    stage='uncontacted lead'

    timeline='1-2 weeks'
    spreadsheet='spreadsheet.com/sheet'
    zipcode= st.text_input('zip code', value = 'unknown')
    interior_surfaces = 'unknown'
    interior_wall_height = 'unknown'
    exterior_surfaces = 'unknown'
    exterior_wall_height = 'unknown'
    
    #from booking
    resched_link='none'
    cancel_link='none'
    meeting_booked='none'
    meeting_time='none'

    system_prompt = bot_info['system_prompt']
    system_prompt = system_prompt.format(name = name, booking_link = booking_link, initial_description = initial_description, lead_full_name = lead_full_name, email = email,
                                         address = address, status = status, stage = stage, timeline = timeline, spreadsheet = spreadsheet, zipcode = zipcode, interior_surfaces = interior_surfaces,
                                         interior_wall_height = interior_wall_height, exterior_surfaces = exterior_surfaces, exterior_wall_height = exterior_wall_height, resched_link = resched_link,
                                         cancel_link = cancel_link, meeting_booked = meeting_booked, meeting_time = meeting_time, additional_notes = additional_notes)

    initial_text = bot_info['initial_text']
    initial_text = initial_text.format(name = name, first_name = lead_full_name, description = initial_description, address = address, booking_link = booking_link)

    
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
