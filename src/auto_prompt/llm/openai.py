from dotenv import load_dotenv
import os
from openai import OpenAI, AzureOpenAI
import json
from .models.openai import MessageRole

class OpenAICompletionEngine:
    
    def __init__(self, cred_source='env', manual_cred={}):
        if cred_source == 'env':
            assert load_dotenv() == True
            # self.client = OpenAI(
            #     api_key=os.environ.get("OPENAI_API_KEY")
            # )
            self.client = AzureOpenAI(
                api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
                api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint = os.getenv("AZURE_OPENAI_BASE_URL")
            )
        elif cred_source == 'manual':
            self.client = OpenAI(
                api_key = manual_cred["OPENAI_API_KEY"],  
            )
        else:
            raise Exception("Invalid value for `cred_source`")
    
        self._messages: List[Dict] = list()
        self._model = "gpt-4-32k"
    
    def set_model(self, model) -> None:
        self._model = model
        
        
    def _insert_system_message(self, message: str) -> None:
        self._messages.append(
            {
                "role": "system",
                "content": message
            })
        
    def _insert_user_message(self, message: str) -> None:
        self._messages.append(
            {
                "role": "user",
                "content": message
            })
        
    def insert_message(self, role: MessageRole, message: str) -> None:
        if role == MessageRole.USER.value:
            self._insert_user_message(message)
        elif role == MessageRole.SYSTEM.value:
            self._insert_system_message(message)
        else:
            raise Exception("Message role not valid.")
    
    
    def get_response(self):
        try:
            response = self.client.chat.completions.create(
                model=self._model,
                messages=self._messages,
                ).choices[0].message.content
            return response
        except Exception as e:
            print(e)
            print('error')

    def get_response_with_tool(self, tool):
        try:
            response = self.client.chat.completions.create(
                model=self._model,
                messages=self._messages,
                tools=[tool],
                tool_choice={"type": "function", "function": {"name": tool['function']['name']}}
                ).choices[0].message.tool_calls[0].function.arguments

            response = json.loads(response)
            return response
        except Exception as e:
            print(e)
            print('error')
