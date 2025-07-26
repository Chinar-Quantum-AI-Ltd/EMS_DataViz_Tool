
from fastapi import FastAPI,Query

from fastapi.responses import JSONResponse
import uvicorn

from utils import check_mongo_connection
from agents import MONGO_AGENTS

from fastapi.responses import StreamingResponse

import io
import base64
import time

import asyncio
app = FastAPI()
agent = MONGO_AGENTS()
#defined two end points one for fetching the data other for displaying charts

@app.post("/fetch_data")
async def query_mongodb(query: str = Query(..., description="Enter your query")):

    """Fetches data from mongo db, returns a response with actual data and the respective answer in natural language"""   
    print("Received query:", query)
    if not check_mongo_connection():
                return {
                "response":"Failed to connect to MongoDB",
                "data":[],
                
            }
    
    try:

        start = time.time()
        
        is_valid = agent.query_analyzer_agent(query)
        if is_valid["response"] == 0 :
            end = time.time()
            
            print(f"Agent returned in {end - start:.2f} seconds")
            return JSONResponse(content={"input": query, "output": is_valid["description"]})
        
        
        print(f"Query analyzer returned ")
        
        fetched_data=await agent.data_fetcher_agent()
        end = time.time()
        print(f"Agents returned in {end - start:.2f} seconds")
        return JSONResponse(content={"input": query, "Data": fetched_data["data"], "Summary": fetched_data["answer"]})
    

    except Exception as e:

        print("Error:", str(e))
        return JSONResponse(status_code=500, content={"error": f"Execution failed: {e}"})
    




@app.get("/generate_visuals")
async def generate_visuals():
    """
    Generate a chart based on the user's query.
    Returns the image as a renderable file.
    """
    try:
        
        charts =agent.generate_visuals()
        if  charts is None:
            return JSONResponse(content={"error": "No query or result found to generate visuals."} )
        image_bytes = base64.b64decode(charts[0].raster)
        image_stream = io.BytesIO(image_bytes)
        #this is to view the chart directly in swagger ui
        return StreamingResponse(image_stream, media_type="image/png",headers={"Content-Disposition": "inline; filename=chart.png"})

      #this will bee used when calling the api from a frontend that decodes base64 strig:
        """return {
            "question": query,
            "chart_code": chart[0].code,
            "image_base64": chart[0].raster
        }"""

    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Visualization failed: {e}"})
    
    




















if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=7000,reload= True,)


