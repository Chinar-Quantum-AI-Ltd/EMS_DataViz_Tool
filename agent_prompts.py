
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
            Given a set of monog db tools and a user question analyze the schema of cluster using appropriate tools at each step. 
            The goal is to accurately identify the  database , collection(s) within database, understand the structure and semantics using a sample document from each relevant collection , and use this information to identify which fields or sub fields should be used to construct the mongo db  query that best addresses the user's question.

            After you selected the field understand what that field does and its aggregation pipeline e.g users.leaveDate.leave_status: This field indicates whether a leave request has been approved or not
            **Note** : If the user's question involves a time unit (e.g., minutes, hours, years, months) not directly stored in the database,  derive it by converting from related fields and include it as a new field in the output (e.g., convert months to years  or minutes to hours)
            formulate a proper approach  and the query to get the final result.
            
            Now after you figured out everthing thing:
            You must extract a JSON response with *both* `answer` and `data` fields.
            - `answer` should explain the result in natural language.
            - `data` must be a list of field-value dictionaries (even if empty).




        Example of required format:
        {{
        "answer": "There is 1 user with admin privileges.",
        "data": [{{
            "username": "admin_user",
            "role": "admin"
        }}]
        }}

        If there’s no data, still include an empty list in "data".
        Do not include any extra text or explanation outside of the Json 
        Think step by step and verify you output before you answer.
            """    

            
        prompt_template = ChatPromptTemplate.from_messages([
                    ("system", """You are an expert in analyzing the schema of the mongo db cluster and selecting the appropriate pipeline i.e database, collection(s) and relevant fields to adrress the users question.
            """),
                    ("user", user),
                    MessagesPlaceholder(variable_name="messages")
                ])
        return prompt_template