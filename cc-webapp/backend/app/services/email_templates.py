from typing import Tuple, Dict, Any

TEMPLATES: Dict[str, Dict[str, str]] = {
    "welcome": {
        "subject": "Welcome to Casino Club, {nickname}!",
        "text": (
            "Hello {nickname},\n\n"
            "Thanks for joining Casino Club! Your starting bonus is {bonus} tokens.\n"
            "Have fun and good luck!\n"
        ),
        "html": (
            "<h2>Welcome, {nickname}!</h2>"
            "<p>Thanks for joining Casino Club! Your starting bonus is <b>{bonus}</b> tokens.</p>"
        ),
    },
    "reward": {
        "subject": "You received a reward: {reward}",
        "text": (
            "Hi {nickname},\n\n"
            "You've just received a reward: {reward}. Current balance: {balance} tokens.\n"
        ),
        "html": (
            "<p>Hi {nickname},</p><p>You've received a reward: <b>{reward}</b>. "
            "Current balance: <b>{balance}</b> tokens.</p>"
        ),
    },
    "event": {
        "subject": "Event update: {event_name}",
        "text": (
            "Hello {nickname},\n\nEvent update: {event_name}. Don't miss it!\n"
        ),
        "html": (
            "<p>Hello {nickname},</p><p>Event update: <b>{event_name}</b>. Don't miss it!</p>"
        ),
    },
}


def render(template: str, context: Dict[str, Any]) -> Tuple[str, str, str]:
    t = TEMPLATES.get(template)
    if not t:
        raise ValueError("unknown_template")
    subject = t["subject"].format(**context)
    text = t["text"].format(**context)
    html = t["html"].format(**context)
    return subject, text, html
