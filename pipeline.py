
from agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


def extract_agent_response(result):
    """Extract the final readable response from a LangChain agent."""

    messages = result.get("messages", [])

    for message in reversed(messages):
        # Skip messages that only contain tool calls
        if getattr(message, "tool_calls", None):
            continue

        content = getattr(message, "content", "")

        if isinstance(content, str) and content.strip():
            return content

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(item.get("text", ""))

                elif isinstance(item, str):
                    parts.append(item)

            response = "\n".join(parts).strip()

            if response:
                return response

    raise ValueError("Agent returned an empty response.")


def run_research_pipeline(topic: str, on_stage_update=None) -> dict:
    """
    Execute the complete ResearchMind pipeline.

    Four stages:
    1. Search Agent
    2. Reader Agent
    3. Writer Chain
    4. Critic Chain

    on_stage_update(stage, status, result)
    Status values: running, done, failed
    """

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Please provide a valid research topic.")

    topic = topic.strip()

    results = {
        "topic": topic,
        "search": "",
        "reader": "",
        "writer": "",
        "critic": "",
    }

    def update(stage, status, result=None):
        """Send progress updates to the Streamlit interface."""

        if on_stage_update is not None:
            on_stage_update(stage, status, result)

    # =========================================================
    # STAGE 1: SEARCH AGENT
    # =========================================================

    update("search", "running")

    try:
        print("\n" + "=" * 55)
        print("STAGE 1: SEARCH AGENT")
        print("=" * 55)

        search_agent = build_search_agent()

        search_response = search_agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Research the following topic: {topic}\n\n"
                        "Find recent and reliable information. "
                        "Prefer trustworthy sources. "
                        "Include relevant source URLs and key findings."
                    ),
                }
            ]
        })

        results["search"] = extract_agent_response(search_response)

        if not results["search"].strip():
            raise ValueError("Search Agent returned no results.")

        update("search", "done", results["search"])

        print("Search Agent completed successfully.")

    except Exception as exc:
        update("search", "failed", str(exc))
        raise RuntimeError(
            f"Search Agent failed: {exc}"
        ) from exc

    # =========================================================
    # STAGE 2: READER AGENT
    # =========================================================

    update("reader", "running")

    try:
        print("\n" + "=" * 55)
        print("STAGE 2: READER AGENT")
        print("=" * 55)

        reader_agent = build_reader_agent()

        reader_response = reader_agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Research topic: {topic}\n\n"
                        "Read the following search results. "
                        "Identify the most relevant URLs and use "
                        "the scraping tool to retrieve detailed content. "
                        "Summarize the retrieved information accurately. "
                        "Do not invent scraped content.\n\n"
                        f"Search results:\n{results['search'][:8000]}"
                    ),
                }
            ]
        })

        results["reader"] = extract_agent_response(reader_response)

        if not results["reader"].strip():
            raise ValueError("Reader Agent returned no content.")

        update("reader", "done", results["reader"])

        print("Reader Agent completed successfully.")

    except Exception as exc:
        update("reader", "failed", str(exc))
        raise RuntimeError(
            f"Reader Agent failed: {exc}"
        ) from exc

    # =========================================================
    # STAGE 3: WRITER CHAIN
    # =========================================================

    update("writer", "running")

    try:
        print("\n" + "=" * 55)
        print("STAGE 3: WRITER CHAIN")
        print("=" * 55)

        research = (
            "SEARCH RESULTS:\n"
            + results["search"]
            + "\n\nRETRIEVED RESEARCH CONTENT:\n"
            + results["reader"]
        )

        report = writer_chain.invoke({
            "topic": topic,
            "research": research,
        })

        if not isinstance(report, str) or not report.strip():
            raise ValueError("Writer Chain returned an empty report.")

        results["writer"] = report

        update("writer", "done", results["writer"])

        print("Writer Chain completed successfully.")

    except Exception as exc:
        update("writer", "failed", str(exc))
        raise RuntimeError(
            f"Writer Chain failed: {exc}"
        ) from exc

    # =========================================================
    # STAGE 4: CRITIC CHAIN
    # =========================================================

    update("critic", "running")

    try:
        print("\n" + "=" * 55)
        print("STAGE 4: CRITIC CHAIN")
        print("=" * 55)

        feedback = critic_chain.invoke({
            "report": results["writer"],
        })

        if not isinstance(feedback, str) or not feedback.strip():
            raise ValueError("Critic Chain returned empty feedback.")

        results["critic"] = feedback

        update("critic", "done", results["critic"])

        print("Critic Chain completed successfully.")

    except Exception as exc:
        update("critic", "failed", str(exc))
        raise RuntimeError(
            f"Critic Chain failed: {exc}"
        ) from exc

    # =========================================================
    # PIPELINE COMPLETED
    # =========================================================

    print("\n" + "=" * 55)
    print("RESEARCHMIND PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 55)

    return results


# =============================================================
# LOCAL EXECUTION
# =============================================================

if __name__ == "__main__":

    research_topic = input(
        "\nEnter your research topic: "
    ).strip()

    try:
        final_results = run_research_pipeline(research_topic)

        print("\n\nFINAL RESEARCH REPORT")
        print("=" * 55)
        print(final_results["writer"])

        print("\n\nCRITIC FEEDBACK")
        print("=" * 55)
        print(final_results["critic"])

    except Exception as error:
        print(f"\nPipeline Error: {error}")
