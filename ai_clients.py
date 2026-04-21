import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types
from anthropic import Anthropic

load_dotenv()

client_1 = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client_2 = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
client_3 = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# OpenAI API
def openai_b64(img_b64):
    response = client_1.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role":"user",
                "content":[
                    {
                        "type":"input_text",
                        "text":"Give one word answer in JSON"
                    },
                    {
                        "type":"input_image",
                        "image_url": f"data:image/png;base64,{img_b64}"
                    }
                ]
            }
        ]
    )
    
    return(response.output_text)

# Local Files Not Supported
def get_response_img(img):
    response = client_1.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role":"user",
                "content":[
                    {
                        "type":"input_text",
                        "text":"Give one word answer in JSON"
                    },
                    {
                        "type":"input_image",
                        "image_url": f"file://{img}"
                    }
                ]
            }
        ]
    )
    
    return(response.output_text)

# Genai API
def genai_b64(img_64):
    response = client_2.models.generate_content(
        model='gemini-2.0-flash',
        contents=[
            types.Part.from_bytes(
                data=img_64,
                mime_type='image/jpeg'
            ),
            "Give one word answer in JSON"
        ]
    )

    return(response.text)

# Claude API
def anthropic_b64(img_64):
    message = client_3.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_64,
                        },
                    },
                    {
                        "type": "text", 
                        "text": "Give one word answer in JSON."
                    },
                ],
            }
        ],
    )

    return(message)