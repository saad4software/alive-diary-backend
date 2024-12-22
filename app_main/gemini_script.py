import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}


def create_diary_session(history):
  model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are a therapist, you deeply care about your patients and like to know how was their day, use open short questions and show empathy, don't use emojis",
  )

  chat_session = model.start_chat(
    history=history
  )

  return chat_session


def talk_to_diary(content):
  model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # system_instruction="You are a therapist, you deeply care about your patients and like to know how was their day, use open short questions and show empathy, don't use emojis",
  )

  response = model.generate_content(content)

  return response.text


def create_memory_session(history):
  model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are trying to capture the moment, get as much details as you can about the event, date, time, place, weather, what you can see, hear, taste, and feel. ask one question at the time and don't use emojis",
  )

  chat_session = model.start_chat(
    history=history
  )

  return chat_session


def talk_to_memory(content):
  model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # system_instruction="You are a therapist, you deeply care about your patients and like to know how was their day, use open short questions and show empathy, don't use emojis",
  )

  response = model.generate_content(content)

  return response.text


