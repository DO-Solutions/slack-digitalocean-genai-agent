from logging import Logger
from ai.providers import get_available_providers
from slack_sdk import WebClient
from state_store.get_redis_user_state import get_redis_user_state
import sys

"""
Callback for handling the 'app_home_opened' event. It checks if the event is for the 'home' tab,
generates a list of model options for a dropdown menu, retrieves the user's state to set the initial option,
and publishes a view to the user's home tab in Slack.
"""


def app_home_opened_callback(event: dict, logger: Logger, client: WebClient):
    if event["tab"] != "home":
        return

    user_id = event["user"]
    print(f"🏠 App Home opened by user: {user_id}")

    # create a list of options for the dropdown menu each containing the model name and provider
    options = [
        {
            "text": {"type": "plain_text", "text": f"{model_info['name']} ({model_info['provider']})", "emoji": True},
            "value": f"{model_name} {model_info['provider'].lower()}",
        }
        for model_name, model_info in get_available_providers().items()
    ]

    # retrieve user's state to determine if they already have a selected model
    provider, model = get_redis_user_state(user_id, True)
    initial_option = None

    if provider and model:
        print(f"📋 Retrieved user state from Redis - User: {user_id}, Provider: {provider}, Model: {model}")
        # set the initial option to the user's previously selected model
        initial_option = list(filter(lambda x: x["value"].startswith(model), options))
        if not initial_option:
            print(f"⚠️ No matching option found for model '{model}', using default")
    else:
        print(f"ℹ️ No provider selection found for user: {user_id}")
        # add an empty option if the user has no previously selected model.
        options.append(
            {
                "text": {"type": "plain_text", "text": "Select a provider", "emoji": True},
                "value": "null",
            }
        )

    try:
        client.views_publish(
            user_id=user_id,
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "Welcome to Sailor Home Page!", "emoji": True},
                    },
                    {"type": "divider"},
                    {
                        "type": "rich_text",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [{"type": "text", "text": "Pick an option", "style": {"bold": True}}],
                            }
                        ],
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "static_select",
                                "initial_option": initial_option[0] if initial_option else options[-1],
                                "options": options,
                                "action_id": "pick_a_provider",
                            }
                        ],
                    },
                ],
            },
        )
        print(f"✅ Successfully published home view for user: {user_id}")
    except Exception as e:
        print(f"❌ Error publishing home view: {e}", file=sys.stderr)
        logger.error(e)
