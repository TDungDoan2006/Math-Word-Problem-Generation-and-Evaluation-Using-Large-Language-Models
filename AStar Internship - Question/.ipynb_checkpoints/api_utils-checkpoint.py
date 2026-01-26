import os
import time
import json
import jiter

from openai import AzureOpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

import boto3
from botocore.exceptions import ClientError

from api_info import *

GPT_MODEL = "gpt-4.1"
GPT_MINI_MODEL = "gpt-4.1-mini"
Phi4_MODEL = "Phi-4"
Phi4_Reasoning_MODEL = "Phi-4-reasoning"
Llama_MODEL = "Llama-4-Maverick-17B-128E-Instruct-FP8"
DeepSeek_MODEL = "DeepSeek-R1-0528"

claude4_model_id = "apac.anthropic.claude-sonnet-4-20250514-v1:0"


API_Version = "2024-05-01-preview"


def create_openai_client():
    openai_client = AzureOpenAI(
        azure_endpoint=os.getenv("ENDPOINT_URL", OpenAI_Endpoint),
        api_key=os.getenv("AZURE_OPENAI_API_KEY", API_key),
        api_version="2025-03-01-preview"
        # api_version="2025-04-14"
    )
    return openai_client
    

def get_inputs(sys_prompt, user_prompt):
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
    inputs = input_sys + input_user
    return inputs


def get_GPT_txt_response(openai_client, sys_prompt, user_prompt, gpt_model=GPT_MODEL):
    start_t = time.time()
    try:
        inputs = get_inputs(sys_prompt, user_prompt)
        response = openai_client.responses.create(
            model=gpt_model,
            input=inputs
        )
        if response.status == 'completed':
            llm_response = {'response': response.output_text, 'status': 0}
        else:
            llm_response = {'response': '', 'status': 1}
    except Exception as e:
        llm_response = {'response': '', 'status': -1}
        print(f">>> Error processing submission: {str(e)}")
    response_time = time.time()-start_t

    llm_response['response_time'] = response_time
    if gpt_model!=GPT_MODEL:
        llm_response['model'] = gpt_model
    return llm_response
        

def get_GPT_struct_response(openai_client, sys_prompt, user_prompt, struct_type, gpt_model=GPT_MODEL):
    start_t = time.time()
    try:
        inputs = get_inputs(sys_prompt, user_prompt)
        response = openai_client.responses.parse(
            model=gpt_model,
            input=inputs,
            text_format=struct_type,
        )
        if response.status == 'completed':
            llm_response = {'status': 0}
            response_obj = response.output_parsed
            for key in response_obj.model_fields:
                value = getattr(response_obj, key)
                llm_response[key] = value
        else:
            llm_response = {'response': '', 'status': 1}
    except Exception as e:
        llm_response = {'response': '', 'status': -1}
        print(f">>> Error processing submission: {str(e)}")
        with open("error.txt", 'a', encoding='utf-8') as file:
            file.write(f"Response:\n{llm_response}\n")
    response_time = time.time()-start_t

    llm_response['response_time'] = response_time
    if gpt_model!=GPT_MODEL:
        llm_response['model'] = gpt_model
    return llm_response


def create_client(endpoint=EndPoint, api_version=API_Version):
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(API_key),
        api_version=api_version
    )
    return client


def get_LLM_response(client, model_name, sys_prompt, user_prompt):
    start_t = time.time()
    try:
        response = client.complete(
            messages=[
                SystemMessage(content=sys_prompt),
                UserMessage(content=user_prompt),
            ],
            model=model_name
        )
        llm_response = {'response': response.choices[0].message.content, 'status': 0}
    except Exception as e:
        llm_response = {'response': '', 'status': -1}
        print(f">>> Error processing submission: {str(e)}")
    response_time = time.time()-start_t
    llm_response['response_time'] = response_time
    return llm_response


def get_aws_client():
    boto3.setup_default_session(
        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
        region_name=region_name)
    client = boto3.client("bedrock-runtime")
    return client


def get_claude_response(client, model_id, sys_prompt, user_prompt, config={}):
    inputs = [
        {
            "role": "user",
            "content": [{"text": user_prompt}],
        }
    ]
    
    start_t = time.time()
    try:
        # Send the message to the model, using a basic inference configuration.
        response = client.converse(
            modelId=model_id,
            messages=inputs,
            inferenceConfig=config,
        )
        response_text = response["output"]["message"]["content"][0]["text"]
        llm_response = {'response': response_text, 'status': 0}
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        llm_response = {'response': '', 'status': -1}
    response_time = time.time()-start_t

    llm_response['response_time'] = response_time
    return llm_response
    


        
