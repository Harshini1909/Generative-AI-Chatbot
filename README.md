# Generative AI Chatbot

---

## Overview

This application is a conversational chatbot powered by **Google Generative AI** and **LangChain**. It enables users to interact with an AI assistant, manage conversational context, and collect schema-based data dynamically. Data is stored persistently in a **PostgreSQL** database, ensuring robustness and reliability. The chatbot includes an intuitive **Gradio-based** user interface for easy interaction.

---

## Features

- **Persistent Storage**: Uses PostgreSQL to store and retrieve conversation history, ensuring data is safely retained.
- **Schema-Based Data Collection**: Allows dynamic collection and validation of user data based on JSON schema definitions.
- **Memory-Powered Conversations**: Retains and uses past interactions for context-aware responses, powered by LangChain.
- **Interactive Gradio Interface**: Provides a user-friendly web-based interface for seamless interaction with the chatbot.
- **Extensible Design**: Built with flexibility to easily incorporate additional features or functionalities.

---

## Design and Approach

### Chatbot Design

1. **Conversation Workflow**:
   - Users can interact with the chatbot to either provide schema-based data or engage in Q&A sessions.
   - Schema-based inputs define the data structure, ensuring type validation (e.g., `text`, `number`).
   - Data collection and chat responses are processed in real time.

2. **Context Management**:
   - The chatbot retains conversation context using LangChain’s `PersistentChatHistory`.
   - Chat history is stored in PostgreSQL for consistent multi-turn interactions, even across sessions.

3. **Database Design**:
   - A `chat_history` table stores messages with fields for `user_id`, `conversation_id`, `message_type`, and `content`.
   - Dynamic tables are created as per user-provided schemas, allowing flexible data storage.

---

### Data Integrity

1. **Input Validation**:
   - User inputs are validated based on schema definitions, ensuring type consistency.
   - For example, fields marked as `number` are checked to ensure valid numeric input.

2. **Database Constraints**:
   - PostgreSQL enforces schema rules, rejecting invalid or incomplete entries.
   - This ensures consistency and prevents data corruption.

---

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- PostgreSQL installed and running
- API key for Google Generative AI

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Harshini1909/Generative-AI-Chatbot.git
   cd chatbot_project
   ```

2. **Set Up the Python Environment**:
   - Create and activate a virtual environment:
     ```bash
     python -m venv chatbot_env
     source chatbot_env/bin/activate  # Windows: chatbot_env\Scripts\activate
     ```
   - Install project dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Set Up the Database**:
   - Create a PostgreSQL database:
     ```sql
     CREATE DATABASE chatbot;
     ```
   - Create the `chat_history` table:
     ```sql
     CREATE TABLE chat_history (
         user_id TEXT,
         conversation_id TEXT,
         message_type TEXT,
         content TEXT
     );
     ```

4. **Configure Environment Variables**:
   - Create a `.env` file in the project root with the following:
     ```
     GOOGLE_API_KEY=your_google_api_key
     POSTGRES_DB=chatbot
     POSTGRES_USER=your_postgres_username
     POSTGRES_PASSWORD=your_postgres_password
     POSTGRES_HOST=localhost
     POSTGRES_PORT=5432
     ```

5. **Run the Application**:
   - Start the chatbot:
     ```bash
     python main.py
     ```
   - Open the Gradio interface in your browser to interact with the chatbot.

---

## Usage Instructions

1. Launch the chatbot by running the command:
   ```bash
   python main.py
   ```
2. Open the Gradio interface in your web browser.
3. Use the **Schema (JSON)** input to provide a schema for dynamic data collection. Example schema:
   ```json
   {
       "table_name": "user_data",
       "fields": [
           {"name": "username", "type": "text", "label": "Enter your name"},
           {"name": "age", "type": "number", "label": "Enter your age"},
           {"name": "email", "type": "text", "label": "Enter your email"}
       ]
   }
   ```
4. Enter your query in the **Your Question** field to interact with the chatbot.

---

## Approach to Maintaining Conversation Context

1. **Persistent Context**:
   - LangChain's `PersistentChatHistory` manages chat history by storing messages in PostgreSQL.
   - Each message is tagged with unique identifiers (`user_id` and `conversation_id`) for consistent tracking.

2. **Dynamic Retrieval**:
   - During each session, the chatbot retrieves previous messages from the database, ensuring continuity in the conversation.

---

## Approach to Ensuring Data Integrity

1. **Schema-Driven Validation**:
   - Input data is validated against the user-defined schema (e.g., field types like `text` or `number`).
   - Invalid inputs are rejected during interaction.

2. **Database Enforcement**:
   - PostgreSQL enforces table schemas, preventing malformed or inconsistent data from being stored.

---

## Enhancements and Future Improvements

1. **Advanced Schema Features**:
   - Support for additional field types (e.g., dates, enums) and constraints (e.g., ranges, patterns).

2. **Contextual Memory Enhancements**:
   - Utilize LangChain’s memory modules, such as `ConversationBufferMemory`, for advanced session handling.

3. **Additional Validations**:
   - Implement validation for schema completeness and consistency before processing.

---

## Acknowledgments

This project utilizes:
- [LangChain](https://langchain.readthedocs.io/) for conversational AI workflows.
- [Google Generative AI](https://ai.google/) for natural language processing.
- [PostgreSQL](https://www.postgresql.org/) for database storage.
- [Gradio](https://gradio.app/) for user-friendly interfaces.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
