from typing import List
import os  # For environment variables
import json  # To handle JSON schemas
import psycopg2  # PostgreSQL database connectivity
import atexit  # To handle cleanup tasks
from dotenv import load_dotenv  # To load environment variables from .env file
import gradio as gr  # For building a user-friendly interface

from langchain_google_genai import ChatGoogleGenerativeAI  # Google Generative AI model
from langchain_core.chat_history import BaseChatMessageHistory  # Base class for chat history
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage  # Message types for chat
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # Prompt templates
from langchain_core.runnables import ConfigurableFieldSpec  # Configurable fields for chat session
from langchain_core.runnables.history import RunnableWithMessageHistory  # Runnable with history
from pydantic import BaseModel, Field  # Data validation and settings management

# Load environment variables from the .env file
load_dotenv()

# Initialize connection to PostgreSQL database
db_connection = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),  # Database name
    user=os.getenv("POSTGRES_USER"),  # Database user
    password=os.getenv("POSTGRES_PASSWORD"),  # Database password
    host=os.getenv("POSTGRES_HOST"),  # Hostname
    port=os.getenv("POSTGRES_PORT")  # Port number
)
db_cursor = db_connection.cursor()  # Create a cursor to execute SQL queries

# Initialize the language model with Google Generative AI
llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_MODEL"), api_key=os.getenv("GOOGLE_API_KEY"))  # type: ignore

# Define the prompt template for the chatbot
chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),  # System's role
        MessagesPlaceholder(variable_name="history"),  # Placeholder for chat history
        ("human", "{question}")  # Human's query
    ]
)

# Define a class to manage chat history stored in PostgreSQL
class PersistentChatHistory(BaseChatMessageHistory, BaseModel):
    user_id: str  # User identifier
    conversation_id: str  # Conversation identifier
    messages: List[BaseMessage] = Field(default_factory=list)  # List of messages

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Initialize the parent class
        self.messages = self.fetch_existing_messages()  # Load messages from the database

    def add_message(self, message: BaseMessage) -> None:
        # Insert a new message into the database
        message_type = "AI" if isinstance(message, AIMessage) else "Human"
        db_cursor.execute(
            """
            INSERT INTO chat_history (user_id, conversation_id, message_type, content)
            VALUES (%s, %s, %s, %s)
            """,
            (self.user_id, self.conversation_id, message_type, message.content)
        )
        db_connection.commit()  # Commit the transaction
        self.messages.append(message)  # Add to local list

    def fetch_existing_messages(self) -> List[BaseMessage]:
        # Retrieve all messages for the user and conversation
        db_cursor.execute(
            """
            SELECT message_type, content FROM chat_history
            WHERE user_id = %s AND conversation_id = %s
            """,
            (self.user_id, self.conversation_id)
        )
        rows = db_cursor.fetchall()  # Fetch all results
        return [
            AIMessage(content=row[1]) if row[0] == "AI" else HumanMessage(content=row[1])
            for row in rows
        ]

    def clear(self) -> None:
        # Delete all messages for the user and conversation
        db_cursor.execute(
            """
            DELETE FROM chat_history
            WHERE user_id = %s AND conversation_id = %s
            """,
            (self.user_id, self.conversation_id)
        )
        db_connection.commit()  # Commit the transaction
        self.messages.clear()  # Clear the local list

# Define a chain that connects prompts with the language model
session_chain = chat_prompt | llm

# Create a runnable with message history for managing sessions
chat_with_memory = RunnableWithMessageHistory(
    session_chain,  # Chat chain
    get_session_history=lambda user_id, conversation_id: PersistentChatHistory(user_id=user_id, conversation_id=conversation_id),  # Retrieve chat history
    input_messages_key="question",  # Key for user input
    history_messages_key="history",  # Key for chat history
    history_factory_config=[  # Configuration for user and conversation IDs
        ConfigurableFieldSpec(
            id="user_id",
            annotation=str,
            name="User ID",
            description="Unique identifier for the user",
            default="",
            is_shared=True
        ),
        ConfigurableFieldSpec(
            id="conversation_id",
            annotation=str,
            name="Conversation ID",
            description="Unique identifier for the conversation",
            default="",
            is_shared=True
        )
    ]
)

# Function to handle schema-based data collection
def process_schema(schema: dict):
    table_name = schema.get("table_name", "dynamic_data")  # Table name from schema
    fields = schema.get("fields", [])  # Fields from schema

    # Create table dynamically if it does not exist
    columns_sql = ", ".join([f"{field['name']} {'TEXT' if field['type'] == 'text' else 'NUMERIC'}" for field in fields])
    db_cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});")
    db_connection.commit()

    # Collect and validate data based on schema
    data_to_insert = {}
    for field in fields:
        input_value = input(f"{field['label']}: ")  # Prompt for user input
        if field["type"] == "number":
            input_value = float(input_value)  # Convert to float if numeric
        data_to_insert[field["name"]] = input_value  # Store in dictionary

    # Insert collected data into the database
    db_cursor.execute(
        f"INSERT INTO {table_name} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join(['%s'] * len(data_to_insert))})",
        tuple(data_to_insert.values())
    )
    db_connection.commit()
    return f"Data successfully saved to table '{table_name}'."  # Confirm success

# Gradio-based interface for user interaction
with gr.Blocks() as chat_interface:
    gr.Markdown("# AI Assistant with Schema-Based Input")  # Interface title
    with gr.Row():  # Row layout
        schema_input = gr.Textbox(label="Schema (JSON)", placeholder="Provide a JSON schema")  # Input for schema
        query_input = gr.Textbox(label="Your Question", placeholder="Type your query here")  # Input for query
    submit_button = gr.Button("Submit")  # Button to submit inputs
    chat_output = gr.Chatbot(label="Chat Output")  # Display for chat output

    # Function to handle schema or query
    def handle_interaction(schema, question, history):
        if schema.strip():  # Check if schema is provided
            try:
                schema_dict = json.loads(schema)  # Parse JSON schema
                return process_schema(schema_dict)  # Process schema
            except json.JSONDecodeError:
                return "Invalid JSON format for schema."  # Error message for invalid JSON
        else:
            return chat_with_memory.invoke({"question": question}).content  # Process chat query

    submit_button.click(handle_interaction, inputs=[schema_input, query_input, chat_output], outputs=chat_output)  # Link inputs and outputs

# Launch the Gradio interface
chat_interface.launch()

# Clean up database connection on exit
atexit.register(lambda: db_connection.close())
