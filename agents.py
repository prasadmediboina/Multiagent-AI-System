
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url


# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# 2. GET GROQ API KEY
# --------------------------------------------------

def get_groq_api_key():

    # First priority: Render environment variables
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    # Second priority: Streamlit secrets
    if not api_key:
        try:
            import streamlit as st

            api_key = st.secrets.get(
                "GROQ_API_KEY", ""
            ).strip()

        except Exception:
            api_key = ""

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Please configure it in Render Environment Variables."
        )

    return api_key


# --------------------------------------------------
# 3. INITIALIZE GROQ LLM
# --------------------------------------------------

def get_llm():

    api_key = get_groq_api_key()

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=api_key,
        max_retries=2,
        timeout=60
    )


llm = get_llm()


# --------------------------------------------------
# 4. SEARCH AGENT
# --------------------------------------------------

def build_search_agent():

    search_agent = create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a professional research search agent. "

            "Find recent and reliable information "
            "about the research topic. "

            "Prefer trustworthy sources such as "
            "research papers, academic publications, "
            "government websites and established news sources. "

            "Include relevant URLs and summarize your findings. "

            "Do not invent information or sources."
        )
    )

    return search_agent


# --------------------------------------------------
# 5. READER AGENT
# --------------------------------------------------

def build_reader_agent():

    reader_agent = create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a professional research reading agent. "

            "Identify the most relevant URLs from the search results. "

            "Use the scraping tool to retrieve detailed content. "

            "Extract important facts, evidence, statistics "
            "and technical explanations. "

            "Summarize retrieved information accurately. "

            "Do not invent scraped content. "
            "Clearly identify unavailable sources."
        )
    )

    return reader_agent


# --------------------------------------------------
# 6. WRITER CHAIN
# --------------------------------------------------

writer_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
        You are an expert research writer.

        Write detailed, structured, evidence-based
        and insightful research reports.

        Maintain a professional writing style.
        Avoid unsupported claims.
        """
    ),

    (
        "human",
        """
        Write a detailed research report on the topic below.

        Topic:
        {topic}

        Research Gathered:
        {research}

        Follow this structure:

        1. Introduction

        2. Key Findings
           - Minimum 3 well-explained findings
           - Include technical details where relevant
           - Explain important developments

        3. Analysis
           - Explain the significance of the findings
           - Identify challenges and limitations

        4. Conclusion

        5. Sources
           - List only URLs present in the supplied research

        Important:
        - Be factual and professional.
        - Do not invent sources or URLs.
        - Do not fabricate statistics.
        - Distinguish established findings from uncertainty.
        """
    )

])


writer_chain = (
    writer_prompt
    | llm
    | StrOutputParser()
)


# --------------------------------------------------
# 7. CRITIC CHAIN
# --------------------------------------------------

critic_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
        You are a professional research report critic.

        Evaluate research reports strictly,
        objectively and constructively.

        Check factual accuracy, evidence,
        completeness, clarity and source quality.
        """
    ),

    (
        "human",
        """
        Review the research report below.

        Report:
        {report}

        Evaluate the report using this exact format:

        Score: X/10

        Strengths:
        - ...
        - ...

        Areas to Improve:
        - ...
        - ...

        Factual Accuracy:
        ...

        Source Quality:
        ...

        One line verdict:
        ...
        """
    )

])


critic_chain = (
    critic_prompt
    | llm
    | StrOutputParser()
)


# --------------------------------------------------
# 8. INITIALIZATION CHECK
# --------------------------------------------------

def check_llm_configuration():

    try:
        api_key = get_groq_api_key()

        return {
            "status": "configured",
            "provider": "Groq",
            "api_key_loaded": bool(api_key),
            "model": "llama-3.3-70b-versatile"
        }

    except ValueError as error:

        return {
            "status": "error",
            "message": str(error)
        }
