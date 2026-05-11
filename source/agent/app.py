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
            f"Ask me what's trending, analyze a topic, or send a report via email."
        ),
        examples=[
            "What's trending right now?",
            "Search news for the latest on World Cup 2026.",
            "What's being posted on Instagram under #telemundo?",
            "Given recent trends, what types of social media posts should Telemundo create?",
            "Analyze Reddit discussions about Tesla.",
        ],
        # theme=gr.themes.Soft(),
    ).launch()
