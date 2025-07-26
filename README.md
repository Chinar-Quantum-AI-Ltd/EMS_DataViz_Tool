# EMS - Data Viz Tool

**A Conversational Data Visualization Tool Powered by AI Agents**

---

## Overview

**EMS - Data Viz Tool** is an interactive conversational system that enables users to generate data visualizations (charts/graphs) by  asking questions in natural language.

This system leverages the power of:

- AI Agents (LLM-based)
- MongoDB MCP Server for data access via tools
- Lida tools for chart generation

---

## From Query to Chart:

1. **Query Analysis**  
   User queries are analyzed and validated using a dedicated LLM agent to ensure they are valid enough to fetch data meaningfully.

2. **Data Retrieval**  
   Once validated, the system connects to a MongoDB database and retrieves the required data using tools exposed by the [MongoDB MCP Server](https://github.com/mongodb-js/mongodb-mcp-server).
   This is faciliated via AI Agents.

3. **Visualization Generation**  
   The retrieved data is passed to LidA tools, which automatically generate relevant visualizations (e.g., bar charts, line charts, pie charts) based on the intent and structure of the query.


---

## Tech Stack:

| Component       | Description                                                 |
|----------------|-------------------------------------------------------------|
| FastAPI         | Backend API layer for interfacing with agents and charts   |
| LangChain       | Framework for building LLM-powered agents                  |
| MongoDB         | Primary data store                                          |
| MCP Server      | Tool layer to expose MongoDB operations as callable tools  |
| LIDA Tools      | Generates visualizations from natural language and data    |
| OpenAI / GPT    | LLM provider for agents                                     |

---

## Features

- Validate user queries using a Query Analyzer Agent
- Automatically start and interact with MongoDB MCP Server via Data Fetcher Agent
- Use HTTP or Stdio transport modes for tool integration
- Generate insights and visualizations with minimal user input
- Return data and charts as responses in FastAPI Swagger UI

---


## Security Note

If you're using the HTTP transport mode with MongoDB MCP Server, ensure:

- Use HTTPS in production
- Protect with authentication and firewalls
- Never expose the server directly to the internet

See: [MCP Security Best Practices](https://github.com/mongodb-js/mongodb-mcp-server#security-best-practices)

---

## References

- [MongoDB MCP Server](https://github.com/mongodb-js/mongodb-mcp-server)
- [LangChain Documentation](https://docs.langchain.com/)
- [LIDA (Language Interface for Data Analysis)](https://github.com/visheratin/lida)
- [FastAPI](https://fastapi.tiangolo.com/)
