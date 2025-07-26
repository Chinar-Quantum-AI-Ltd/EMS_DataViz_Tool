from langchain_openai import ChatOpenAI
from pymongo.mongo_client import MongoClient
import os

from lida_tools import TextGenerationConfig
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any,Union
from pymongo.server_api import ServerApi
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.client.stdio import stdio_client
from PIL import Image
import io
import base64

load_dotenv()

uri = os.getenv("MDB_MCP_CONNECTION_STRING")


OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

def model_setup():
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=10000,
            timeout=30,
            seed=42,
            top_p =1,
            max_retries=2,
            
        )
        return model



   
def check_mongo_connection():
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Pinged MongoDB: Successfully connected!")
        return True
    except Exception as e:
        print("MongoDB connection failed:", e)
        return False
    

#defined server parameters to run the mcp server in stdio setup (this does not support running application via Fast API)
def mcp_server_params():
#Server setup for MCP stdio connection
        server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "mongodb-mcp-server",
                "--useEnv",
                "--readOnly"
            ],
            env={
                "MDB_MCP_CONNECTION_STRING": uri
            }
        )

        return server_params



"""async def Load_Mongo_Tools()->Union[List, dict]:
   
    if not check_mongo_connection():
        return {
            "answer":"Failed to connect to MongoDB",
            "data":[],
            
        }
    # Server setup for MCP stdio connection
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "mongodb-mcp-server",
            "--useEnv",
            "--readOnly"
        ],
        env={
            "MDB_MCP_CONNECTION_STRING": uri
        }
    )


    
        
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                print("Type of tools", type(tools))
                return tools
    finally:
        print("DEBUG: Load_Mongo_Tools completed") """

class MongoDBResponse(BaseModel):
    """Structured response for MongoDB queries"""
    answer: str = Field(...,description="contains the summary of the retrieved results in natural language")
    data: List[Dict[str, Any]] = Field(...,description="actual data retrieved fromm the mongo db query")

class QueryValidationResponse(BaseModel):
    response: int = Field(..., description="1 or 0 based on whether the query is valid or not")
    description: str = Field(..., description="Explanation of the validation result")


def base64_to_image(base64_string):
    bytedata=base64.b64decode(base64_string)
    return Image.open(io.BytesIO(bytedata)) 

def model_config():

    openaiconfig = TextGenerationConfig(                  
                n=1,
                model="gpt-4o-mini",
                temperature=0,
                timeout=30,
                seed=42,
                top_p =1,
                max_retries=2,
                
            )
    return openaiconfig