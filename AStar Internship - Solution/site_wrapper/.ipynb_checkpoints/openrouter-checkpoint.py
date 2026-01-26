import os
import json
import ast
import re

import torch
import pandas as pd
import numpy as np
import sklearn as sk

from dotenv import load_dotenv
from together import Together
from openai import OpenAI

load_dotenv()
TOKEN = os.getenv("AStarPrivate")
if TOKEN is None:
    raise RuntimeError("Token parsing failed")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=TOKEN,
)

class OpenRouter():
    def __init__(self):
        return 

    def get_inputs(self,sys_prompt, user_prompt):
        if sys_prompt!=None and sys_prompt!='':
            input_sys = [{
                "role": "developer",
                "content": sys_prompt
            }]  
        else:
            input_sys = []
        if user_prompt!=None and user_prompt!='':
            input_user = [{
                "role": "user",
                "content": user_prompt
            }]
        else:
            input_user = []
        self.inputs = input_sys + input_user
        return self.inputs
    
    def get_LLM_response(self,model,sys_prompt,user_prompt):
        prompt = [{
                        "role": "user",
                        "content": sys_prompt
                    },
                    {
                        "role" : "user",
                        "content" : user_prompt
                    }]
        response = client.chat.completions.create(
                        model=model,
                        messages=prompt,
                        temperature=0.9
                    )
        message = response.choices[0].message
        if message is None or message.content is None:
            print(f"No valid message returned for question: {info["question"]}")
        self.response = response
        return message.content

