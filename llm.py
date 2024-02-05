from openai import OpenAI
import streamlit as st
import os
import re
import random
from icecream import ic

openai = OpenAI(max_retries = 5)



def generate_streaming_response(self, messages, model = 'gpt-4-1106-preview', max_tokens=200):
    try:
        response = openai.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, stream=True)
        big_chunk = ""
        for chunk in response:
            chunk = chunk.choices[0].delta.content
            if chunk:
                big_chunk += chunk
                if chunk in ['!', '.', '?']:
                    to_yield = big_chunk
                    big_chunk = ""
                    yield to_yield

    
    except Exception as e:
        error_message = f"Attempt failed: {e}"
        print(error_message)


def split_sms(message):
    import re

    # Use regular expressions to split the string at ., !, or ? followed by a space or newline
    sentences = re.split('(?<=[.!?]) (?=\\S)|(?<=[.!?])\n', message.strip())
    # Strip leading and trailing whitespace from each sentence
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Compute the cumulative length of all sentences
    cum_length = [0]
    for sentence in sentences:
        cum_length.append(cum_length[-1] + len(sentence))
    
    total_length = cum_length[-1]

    # Find the splitting point
    split_point = next(i for i, cum_len in enumerate(cum_length) if cum_len >= total_length / 2)

    # Split the sentences into two parts at the splitting point
    part1 = sentences[:split_point]
    part2 = sentences[split_point:]

    # Join the sentences in each part back into strings and exclude any part that is empty
    strings = []
    if part1:
        strings.append(" ".join(part1))
    if part2:
        strings.append(" ".join(part2))
    
    return strings


#generate openai response; returns messages with openai response
def generate_responses(session_state):
  messages = session_state.messages

  system_prompt = session_state.system_prompt
  system_prompt = {"role": "system", "content": system_prompt}

  key = os.environ.get("OPENAI_API_KEY")
  openai.api_key = key

  response = openai.chat.completions.create(model=session_state.model, messages=[system_prompt , *messages], max_tokens=session_state.max_tokens, temperature = session_state.temp)
  response = response.choices[0].message.content
  split_response = split_sms(response)
  for section in split_response:
    session_state.messages.append({"role": "assistant", "content": section})
  st.rerun()
  # 

  # split_response = split_sms(response)
  # ic(split_response)
  # for section in split_response:
  #   section = {
  #     "role": "assistant", 
  #     "content": section
  #   }
  #   messages.append(section)
  #   session_state.messages = messages[1:]
  # st.rerun()


