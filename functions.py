import openai
import os
import re
import random

#generate openai response; returns messages with openai response
def ideator(messages):

  key = os.environ.get("OPENAI_API_KEY")
  openai.api_key = key

  result = openai.ChatCompletion.create(
    model="gpt-4",
    messages= messages
  )
  response = result["choices"][0]["message"]["content"]
  
  def split_sms(message):
      import re
  
      # Use regular expressions to split the string at ., !, or ? followed by a space or newline
      sentences = re.split('(?<=[.!?]) (?=\\S)|(?<=[.!?])\n', message.strip())
      # Strip leading and trailing whitespace from each sentence
      sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
  
      # Initialize part1 and part2 as empty lists
      part1 = []
      part2 = []
  
      # For each sentence, add it to the part which currently has the shortest total length
      for sentence in sentences:
          if sum(len(s) for s in part1) <= sum(len(s) for s in part2):
              part1.append(sentence)
          else:
              part2.append(sentence)
  
      # Join the sentences in each part back into strings
      strings = [" ".join(part1), " ".join(part2)]
      
      return strings




  
  split_response = split_sms(response)
  count = len(split_response)
  for section in split_response:
    section = {
      "role": "assistant", 
      "content": section
    }
    messages.append(section)

  return messages, count


#prompt user with botresponse in terminal and ask for an input. returns messages with human response
#change this from input function to streamlit function
def terminaltalker(messages):

  botresponse = messages[-1]["content"]
  userresponse = input(botresponse+"\n")
  messages.append(
  {
    "role": "user",
    "content": userresponse
  }
  )
  return messages

#starts terminal conversation. Respond with exit() to exit. 
def terminalbot():
    import redis
    redis_host = os.environ.get("REDIS_1_HOST")
    redis_port = 25061
    redis_password = os.environ.get("REDIS_1_PASSWORD")
    rd = redis.Redis(host=redis_host, port=redis_port, password=redis_password, ssl=True, ssl_ca_certs="/etc/ssl/certs/ca-certificates.crt")

    system_prompt = rd.get("carr@improovy.com-systemprompt-01").decode('utf-8')
    initial_text = rd.get("carr@improovy.com-initialtext-01").decode('utf-8')
    
    #initialize message
    messages = [
          {"role": "system", "content": system_prompt},
          {"role": "assistant", "content": initial_text}]
    
    while True:
       messages = terminaltalker(messages)
       if messages[-1]["content"] == "exit()":
          break
       ideator(messages)
