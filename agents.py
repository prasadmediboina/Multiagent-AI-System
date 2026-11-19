
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url

load_dotenv()


# Get Groq API key from environment or Streamlit secrets
def get_groq_api_key():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Configure it in your .env "
            "file or Streamlit Cloud Secrets."
        )

    return api_key


# Initialize Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=get_groq_api_key()
)


# 1. Search Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a professional research search agent. "
            "Find recent, reliable information. Prefer trustworthy sources. "
            "Include relevant URLs and summarize your findings."
        )
    )


# 2. Reader Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a research reading agent. "
            "Identify the most relevant URLs from the search results. "
            "Use the scraping tool to retrieve detailed content. "
            "Summarize the retrieved information accurately. "
            "Do not invent scraped content."
        )
    )


# 3. Writer Chain
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research writer. "
        "Write clear, structured and insightful reports."
    ),
    (
        "human",
        """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list only URLs present in the supplied research)

Be detailed, factual and professional.
Never invent sources or URLs."""
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# 4. Critic Chain
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. "
        "Be honest, specific and objective."
    ),
    (
        "human",
        """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()
