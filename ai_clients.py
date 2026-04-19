import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_response_b64(img_b64):
    response = client.responses.create(
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
    response = client.responses.create(
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