🤖 Multi-Agent AI System (RAG + Streamlit)
An intelligent multi-agent AI system that uses Retrieval-Augmented Generation (RAG) to search, analyze, and generate high-quality responses using multiple collaborating agents.

🚀 Overview
This project simulates real-world AI systems using multiple specialized agents:

🔍 Search Agent – Fetches relevant information
📖 Reader Agent – Extracts and understands data
✍️ Writer Agent – Generates responses
🧠 Critic Agent – Improves output quality
🧩 Features
Multi-agent architecture
RAG pipeline implementation
Real-time response generation
Streamlit UI
Modular design
🛠️ Tech Stack
Python
Streamlit
LangChain
OpenAI API
📂 Project Structure
project/
│── app.py              # Streamlit UI
│── agents.py           # Agent logic
│── pipeline.py         # RAG pipeline (core flow)
│── tools.py            # Search & scraping tools
│── requirements.txt
│── .env
│── README.md
🔄 Pipeline Explanation (pipeline.py)
The pipeline.py file manages the end-to-end RAG flow:

Takes user query
Calls Search Agent to retrieve data
Passes results to Reader Agent
Writer Agent generates response
Critic Agent reviews and refines output
👉 This pipeline ensures:

Better accuracy
Structured reasoning
High-quality answers
⚙️ Installation
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
🔑 Environment Setup
Create a .env file:

OPENAI_API_KEY=your_api_key_here
▶️ Run on Localhost
Start the application:

python -m streamlit run app.py
After running, open your browser:

Local URL: http://localhost:8501
Network URL: http://192.168.0.102:8501
💡 Example Workflow
Enter a query in UI
System searches data
Agents process information
Final refined answer displayed
🌍 Real-World Use Cases
AI research assistant
Content generation
Chatbots
Knowledge retrieval systems
🧠 Future Improvements
Memory-enabled agents
Better ranking algorithms
API deployment
UI enhancements
👨‍💻 Author
Prasad mediboina*
