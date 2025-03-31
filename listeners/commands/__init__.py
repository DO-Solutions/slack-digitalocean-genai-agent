from slack_bolt import App
from .ask_command import ask_callback
from .summary_command import summary_callback


def register(app: App):
    app.command("/ask-sailor")(ask_callback)
    app.command("/sailor-summary")(summary_callback)
