from langgraph.prebuilt import create_react_agent
from utils import model_setup,mcp_server_params,check_mongo_connection, base64_to_image, model_config

from agent_prompts import query_analyzer_agent_prompt, data_fetcher_agent_prompt

from langchain_core.output_parsers import JsonOutputParser
from langgraph.checkpoint.memory import MemorySaver

import pandas as pd
from lida import Manager,llm

from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.client.stdio import stdio_client
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
import json



# Agents class -> contains three specialized agents
class MONGO_AGENTS:
     def __init__(self, query):
        self.query =query
        self.tools = None
        self.model =model_setup()
        self.result = None

     # Agent 1
     def query_analyzer_agent(self):
            """Analyzes the user side query and checks if query is valid enough to be processed futher """
            
        
            prompt_template =query_analyzer_agent_prompt()
            chain = prompt_template | self.model | JsonOutputParser()
            answer = chain.invoke({"user_question": self.query})

            if not isinstance(answer, dict):
              return ValueError("Unexpected response format from LLM. Expected a dictionary.")
              
              
            else: 
                  print (answer)
                  return answer
                       



     
     # Agent 2 
     async def data_fetcher_agent(self):
        
        """Data fetcher agent uses mongo db mcp tools and retrieves  data from Mongo DB based on users query"""
        server_params = mcp_server_params()
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.tools = await load_mcp_tools(session)
                #print("Loaded tools:", [tool.name for tool in self.tools])
               
                
                
                memory = MemorySaver()
                prompt_template = data_fetcher_agent_prompt()
                parser = JsonOutputParser()
                agent=create_react_agent(model=self.model, 
                            tools=self.tools, 
                            
                            prompt=prompt_template,
                            checkpointer=memory,
                            response_format=JsonOutputParser,
                            #response_format=output_parser,
                        )
        
        
                config = {"configurable": {"thread_id": "test-thread"}}
                try:
                    print("Invoking data_fetcher_agent agent...")
                    fetched_data = await agent.ainvoke({"messages": [("human", self.query)]}, config)
                    fetched_data = fetched_data["messages"][-1].content
                
                    
                     
                
                    try:
                                parsed = parser.parse(fetched_data)
                                print("Data fetched:\n")
                                print(json.dumps(parsed, indent=2))
                                print('='*80)
                                self.result = parsed
                                return parsed
                    except Exception as e:
                                print(f"Failed to parse string response: {e}")
                                return (f"Parsing error: {str(e)}" )
                        
                    
                except Exception as e:
                    import traceback
                    print("data_fetcher_agent failed with exception:", e)
                    traceback.print_exc()
                    return f"Agent error: {str(e)}"  
                
      # Agent 3   -> Lida        
     def generate_visuals(self): 
         """This agent uses lida to generate charts / graphs given the  data fetched from database"""

         if not self.query or not self.result:
            print("No query or result found to generate visuals")
            return None

        
        

         lida= Manager(text_gen = llm("openai", api_key=os.getenv("OPENAI_API_KEY"))) 

         df = pd.DataFrame(self.result["data"])
        
         if df.empty:
            print("No data found to visualize.")
            return None
         summary = lida.summarize(df,textgen_config=model_config(),summary_method ="llm")# the df can be a pandas dataframe or a string

         print("#####################") 
         print("SUMMARY:\n",summary)

         charts = lida.visualize(summary=summary ,goal=self.query,textgen_config=model_config(),library="seaborn") # exploratory data analysis
         print("######################")


         print(charts[0].code)


         base64_string=charts[0].raster
         image=base64_to_image(base64_string)
        
         with open("graph.png", "wb") as f:
            image.save(f, format="PNG") 
            print("image save successfully")
         return charts, self.query


                                                
                    

    
            
           
def run_agents():


    agent = MONGO_AGENTS("which employee has taken most no of approved leaves over the years check across all the departments and  give me the name of the employee and the no of approved leaves he she has taken")

    
             
    is_valid=agent.query_analyzer_agent()
    
    
    agent2_response=asyncio.run(agent.data_fetcher_agent())
       
        

    agent.generate_visuals()
        
        


     
    
if __name__ == "__main__":
    run_agents()
    
#Loaded tools: ['switch-connection', 'list-collections', 'list-databases', 'collection-indexes', 'collection-schema', 'find', 'collection-storage-size', 'count', 'db-stats', 'aggregate', 'explain', 'mongodb-logs']


