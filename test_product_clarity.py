import unittest

from product_clarity import (
    CoachState,
    next_question,
    readiness,
    record_answer,
    scope_redirect,
    snapshot,
)


class ProductClarityTests(unittest.TestCase):
    def test_starts_with_product_idea(self):
        self.assertEqual(next_question(CoachState()), "In one sentence, what are you trying to create?")

    def test_adapts_to_first_missing_field(self):
        state = CoachState()
        record_answer(state, "product_idea", "A maintenance planner for small HVAC companies")
        self.assertIn("primary customer", next_question(state).lower())

    def test_challenges_overbroad_customer_before_advancing(self):
        state = CoachState()
        record_answer(state, "product_idea", "A better scheduling app")
        record_answer(state, "primary_customer", "Everyone")
        self.assertIn("too broad", next_question(state).lower())

    def test_challenges_feature_creep(self):
        state = CoachState()
        record_answer(state, "must_have", "login, chat, billing, reports, calendar, marketplace")
        self.assertIn("more than five", next_question(state).lower())

    def test_redirects_out_of_scope_topic(self):
        redirect = scope_redirect("Should I file a patent before I talk to users?")
        self.assertIn("later Mind to Market stage", redirect)

    def test_rejects_unknown_field(self):
        with self.assertRaises(ValueError):
            record_answer(CoachState(), "branding", "Blue logo")

    def test_completed_state_is_ready(self):
        state = CoachState(
            answers={
                "product_idea": "A maintenance planner for independent HVAC service companies",
                "primary_customer": "Owners of HVAC companies with 3 to 15 technicians",
                "problem": "Recurring maintenance visits are missed because schedules live in disconnected calendars and notes",
                "solution": "A shared maintenance queue that creates the next visit and alerts the office before it is due",
                "value_proposition": "The owner retains recurring revenue and avoids manual calendar audits",
                "potential_advantage": "A workflow designed around technician routes and recurring service agreements",
                "must_have": "customer list, recurring schedule, due alerts",
                "nice_to_have": "route optimization, branded reminders",
                "later": "payments, inventory, marketplace",
            }
        )
        result = readiness(state)
        self.assertEqual(result["score"], 100)
        self.assertIn("Ready", result["status"])
        self.assertIsNone(next_question(state))

    def test_snapshot_has_stable_structure(self):
        state = CoachState(answers={"product_idea": "A safer ladder accessory"})
        result = snapshot(state)
        self.assertEqual(result["product_statement"], "A safer ladder accessory")
        self.assertEqual(set(result["version_1"]), {"must_have", "nice_to_have", "later"})
        self.assertIn("readiness", result)


if __name__ == "__main__":
    unittest.main()
