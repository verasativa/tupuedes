import posthog
import uuid


class Metrics:
    def __init__(self):
        posthog.project_api_key = 'phc_Awt6Oq4LCk8sKB3VQ6CdFUQJV88ARQSO3zfXZGbXwdF'
        posthog.host = 'https://app.posthog.com'
        self.id = uuid.getnode()

    def log_event(self, event_name):
        posthog.capture(self.id, event_name)