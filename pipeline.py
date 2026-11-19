
from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


# --------------------------------------------------
# 1. HELPER: EXTRACT AGENT RESPONSE
# --------------------------------------------------

def extract_agent_response(result: dict) -> str:
    """
    Extract the final text response from a LangChain agent.
    Skips intermediate tool-call messages.
    """

    messages = result.get("messages", [])

    for message in reversed(messages):

        content = getattr(message, "content", "")

        tool_calls = getattr(message, "tool_calls", [])

        # Skip messages that only request tool execution
        if tool_calls:
            continue

        if isinstance(content, str) and content.strip():
            return content.strip()

        # Handle structured content blocks
        if isinstance(content, list):
            text_parts = []

            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))

            combined = "\n".join(text_parts).strip()

            if combined:
                return combined

    raise ValueError(
        "Agent completed without producing a text response."
    )


# --------------------------------------------------
# 2. RESEARCH PIPELINE
# --------------------------------------------------

def run_research_pipeline(topic: str) -> dict:
    """
    Execute the complete four-stage research workflow.

    Stages:
        1. Search Agent
        2. Reader Agent
        3. Writer Chain
        4. Critic Chain

    Returns:
        Dictionary containing search results,
        scraped content, report and critic feedback.
    """

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    topic = topic.strip()

    state = {
        "topic": topic,
        "search_results": "",
        "scraped_content": "",
        "report": "",
        "feedback": ""
    }

    # --------------------------------------------------
    # STEP 1: SEARCH AGENT
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("STEP 1 - SEARCH AGENT")
    print("=" * 60)

    try:

        search_agent = build_search_agent()

        search_result = search_agent.invoke({
            "messages": [
                (
                    "user",
                    (
                        f"Research the following topic: {topic}\n\n"
                        "Find recent, reliable and detailed information. "
                        "Use the web search tool to gather relevant sources. "
                        "Include source titles, URLs and useful findings. "
                        "Do not invent sources."
                    )
                )
            ]
        })

        state["search_results"] = extract_agent_response(
            search_result
        )

        if not state["search_results"]:
            raise ValueError("Search agent returned empty results.")

        print("\nSEARCH RESULTS:")
        print(state["search_results"])

    except Exception as e:

        raise RuntimeError(
            f"Search Agent failed: {str(e)}"
        ) from e

    # --------------------------------------------------
    # STEP 2: READER AGENT
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("STEP 2 - READER AGENT")
    print("=" * 60)

    try:

        reader_agent = build_reader_agent()

        reader_result = reader_agent.invoke({
            "messages": [
                (
                    "user",
                    (
                        f"Read and analyze the research sources "
                        f"about: {topic}\n\n"
                        "Below are the search results:\n\n"
                        f"{state['search_results'][:6000]}\n\n"
                        "Instructions:\n"
                        "1. Identify the most relevant URLs.\n"
                        "2. Use the scraping tool to retrieve webpage content.\n"
                        "3. Extract important facts, technical details "
                        "and evidence.\n"
                        "4. Summarize the retrieved information.\n"
                        "5. Clearly identify sources that could not be accessed.\n"
                        "Do not invent scraped content."
                    )
                )
            ]
        })

        state["scraped_content"] = extract_agent_response(
            reader_result
        )

        if not state["scraped_content"]:
            raise ValueError("Reader agent returned empty content.")

        print("\nSCRAPED CONTENT:")
        print(state["scraped_content"])

    except Exception as e:

        raise RuntimeError(
            f"Reader Agent failed: {str(e)}"
        ) from e

    # --------------------------------------------------
    # STEP 3: WRITER CHAIN
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("STEP 3 - WRITER CHAIN")
    print("=" * 60)

    try:

        research_combined = (
            "SEARCH RESULTS:\n\n"
            f"{state['search_results']}\n\n"
            "DETAILED SCRAPED CONTENT:\n\n"
            f"{state['scraped_content']}"
        )

        report = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })

        if not isinstance(report, str) or not report.strip():
            raise ValueError("Writer returned an empty report.")

        state["report"] = report.strip()

        print("\nFINAL RESEARCH REPORT:")
        print(state["report"])

    except Exception as e:

        raise RuntimeError(
            f"Writer Chain failed: {str(e)}"
        ) from e

    # --------------------------------------------------
    # STEP 4: CRITIC CHAIN
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("STEP 4 - CRITIC CHAIN")
    print("=" * 60)

    try:

        feedback = critic_chain.invoke({
            "report": state["report"]
        })

        if not isinstance(feedback, str) or not feedback.strip():
            raise ValueError("Critic returned empty feedback.")

        state["feedback"] = feedback.strip()

        print("\nCRITIC EVALUATION:")
        print(state["feedback"])

    except Exception as e:

        raise RuntimeError(
            f"Critic Chain failed: {str(e)}"
        ) from e

    # --------------------------------------------------
    # PIPELINE COMPLETED
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("RESEARCH PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    return state


# --------------------------------------------------
# 3. LOCAL EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    topic = input(
        "\nEnter a research topic: "
    ).strip()

    try:

        result = run_research_pipeline(topic)

        print("\nRESEARCH COMPLETED")
        print("\nFinal Report:")
        print(result["report"])

        print("\nCritic Feedback:")
        print(result["feedback"])

    except Exception as error:

        print("\nPIPELINE ERROR:")
        print(str(error))
