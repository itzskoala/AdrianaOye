"""
Gradio UI for Adriana. Run with:
    python -m source.agent.app
"""

import gradio as gr
from source.agent.adriana import GEMINI_MODEL, chat_sync

if __name__ == "__main__":
    gr.ChatInterface(
        fn=chat_sync,
        title="Adriana — Social Intelligence",
        description=(
            f"Powered by **{GEMINI_MODEL}** via Gemini · "
            "Ask me what's trending, analyze a topic, or send a report via email."
        ),
        examples=[
            "What's trending right now?",
            "What are people saying on Reddit about artificial intelligence?",
            "Search news for the latest on climate change.",
            "What's being posted on Instagram under #travel?",
            "Analyze Reddit discussions about Tesla.",
        ],
        # theme=gr.themes.Soft(),
    ).launch()
