"""
Rule engine for disputes.
"""


class DecisionEngine:
    ACCEPT_RULES = {
        "email_bounce": "EMAIL_BOUNCE",
        "phone_invalid": "WRONG_ORG",
        "firm_inactive": "CLOSED_FIRM",
        "duplicate": "DUPLICATE",
    }

    REJECT_RULES = {
        "no_response": "CONTACTED_NOT_INTERESTED",
        "wrong_person": "CONTACTED_NOT_INTERESTED",
    }

    @classmethod
    def evaluate(cls, evidence_data):
        if not isinstance(evidence_data, dict):
            return "reject", "DEFAULT_REJECT"

        rule_type = evidence_data.get("rule_type")
        if rule_type in cls.ACCEPT_RULES:
            return "accept", cls.ACCEPT_RULES[rule_type]
        if rule_type in cls.REJECT_RULES:
            return "reject", cls.REJECT_RULES[rule_type]

        for key, reason in cls.ACCEPT_RULES.items():
            if evidence_data.get(key):
                return "accept", reason

        for key, reason in cls.REJECT_RULES.items():
            if evidence_data.get(key):
                return "reject", reason

        return "reject", "DEFAULT_REJECT"
