from apps.disputes.rule_engine import DecisionEngine


def test_decision_engine_accept():
    decision, reason = DecisionEngine.evaluate({"email_bounce": True})
    assert decision == "accept"
    assert reason == "EMAIL_BOUNCE"


def test_decision_engine_reject():
    decision, reason = DecisionEngine.evaluate({"no_response": True})
    assert decision == "reject"
    assert reason == "CONTACTED_NOT_INTERESTED"


def test_decision_engine_default_reject():
    decision, reason = DecisionEngine.evaluate({})
    assert decision == "reject"
    assert reason == "DEFAULT_REJECT"
