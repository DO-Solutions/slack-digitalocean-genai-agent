# This file defines constant messages used by the Slack bot for when a user mentions the bot without text,
# when summarizing a channel's conversation history, and a default loading message.
# Used in `app_mentioned_callback`, `dm_sent_callback`, and `handle_summary_function_callback`.

MENTION_WITHOUT_TEXT = """
Hi there! You didn't provide a message with your mention.
    Mention me again in this thread so that I can help you out!
"""
SUMMARIZE_CHANNEL_WORKFLOW = """
A user has just joined this Slack channel.
Please create a quick summary of the conversation in this channel to help them catch up.
Don't use user IDs or names in your response.
"""
SUMMARIZE_THREAD_PROMPT = """
Please summarize this thread conversation to highlight the key points and conclusions.
Keep the summary concise and focused on the important information.
Don't use user IDs in your response.
"""
DEFAULT_LOADING_TEXT = "Adjusting the sails..."
