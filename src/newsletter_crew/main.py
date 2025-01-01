from newsletter_crew.crew import NewsletterGenCrew
# import os


def load_html_template():
    with open("src/newsletter_crew/config/newsletter_template.html", "r") as file:
        html_template = file.read()
    return html_template


def run():
    inputs = {
        "topic": input("Enter the topic: "),
        "html_template": load_html_template(),
        "personal_message": input("Enter a personal message: ") or "No personal message provided.",
    }
    NewsletterGenCrew().crew().kickoff(inputs=inputs)
