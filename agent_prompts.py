
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder


def query_analyzer_agent_prompt():

        user ="""
        Rules:
        - If the question is vague, ambiguous, incomplete (e.g., 'What is the average?' without specifying what to average), or not related to MongoDB querying — return:
        {{
            "response": 0,
            "description": "No data retrieved. Please be more specific with your question."
        }}
        - You can Add additional suggestions in description specifying what is missing or what is not clear to you
        
        - If the question is valid and specific (e.g., 'Find the average age of users'), return:
        {{
            "response": 1,
            "description": "The question is valid."
        }}

        ### Be reasonable in your judgement while classifying questions as valid or invalid
        ### do not ask for too many specifications.
        ### You final answer  should be properly formatted  in strctured JSON

        Given User question: 
        {user_question}
        """    

        prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert at validating users question for clarity and completeness for querying a MongoDB EMS database.
        """),
                ("user", user)
            ])
        return prompt_template


def data_fetcher_agent_prompt():


        user = """
        You are a specialized agent designed to interact with a MongoDB database.
        Given an input question, create a syntactically correct MongoDB query to run, then look at the results of the query and return the answer.
Never query for all the fields from a specific collection, only ask for the relevant fields given the question.      

You have access to tools for interacting with the database.
Only use the information returned by the  tools to construct your final answer.       
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

The query MUST include the database name ,then collection name and then contents of the aggregation pipeline.

To start you should ALWAYS look at the collections in the database and see what you can query.
Do NOT skip this step.
Then you should query the schema of the most relevant collections.

First form a natural language answer then:

Return only a valid JSON object as the final output in the following format:
{{
        "answer": "<natural language summary of the data>",
        "data": [<list of JSON objects with relevant fields>]
}}        

            """    

            
        prompt_template = ChatPromptTemplate.from_messages([
                    ("system", """You are an expert in analyzing the schema of the mongo db cluster and selecting the appropriate pipeline i.e database, collection(s) and relevant fields to adrress the users question.
            """),
                    ("user", user),
                    MessagesPlaceholder(variable_name="messages")
                ])
        return prompt_template




"""Return only a valid JSON object in the following format:
{{
        "answer": "<natural language summary of the data>",
        "data": [<list of JSON objects with relevant fields>]
}}


        Instructions:
- In the "answer" field, write a natural language summary **describing the data**.
- Do not just say “listed below” or “as follows”. Instead, explain insights, comparisons, or trends observed in the data.
- If no data is found, still return `"data": []` and make the summary reflect that (e.g., "No users found with admin privileges.").
- Do not include any text outside the JSON respons
"""