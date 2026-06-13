"""
TMS — E2E Tests: AI Triage API
Tests triage status, chat conversations, red-flag detection, and rule-based fallback.
"""


class TestTriageStatus:
    def test_triage_status_endpoint(self, client):
        """TC-TRI-001: Triage status endpoint is accessible."""
        resp = client.get("/api/triage/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "gemini_available" in data
        assert "engine" in data
        # In CI without API key, rule-based fallback is expected
        assert data["engine"] in ("gemini", "rule-based")


class TestTriageChat:
    def test_initial_symptom_message(self, client, patient_headers):
        """TC-TRI-002: Triage chat responds to initial symptom message."""
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I have a headache",
            "conversation_history": [],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert "stage" in data
        assert data["stage"] in ("gathering", "clarifying", "assessment")
        assert len(data["reply"]) > 0

    def test_triage_with_fever(self, client, patient_headers):
        """TC-TRI-003: Triage responds to fever complaint."""
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I have a high fever since yesterday",
            "conversation_history": [],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["stage"] in ("gathering", "clarifying", "assessment")

    def test_triage_suggestions_present(self, client, patient_headers):
        """TC-TRI-004: Triage response includes suggestions."""
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I have stomach pain",
            "conversation_history": [],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "suggestions" in data

    def test_triage_multi_turn_conversation(self, client, patient_headers):
        """TC-TRI-005: Triage handles multi-turn conversation."""
        # Turn 1
        resp1 = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I have back pain",
            "conversation_history": [],
        })
        assert resp1.status_code == 200
        reply1 = resp1.json()["reply"]

        # Turn 2
        history = [
            {"role": "user", "content": "I have back pain"},
            {"role": "bot", "content": reply1},
        ]
        resp2 = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "It started 3 days ago",
            "conversation_history": history,
        })
        assert resp2.status_code == 200
        reply2 = resp2.json()["reply"]

        # Turn 3
        history.extend([
            {"role": "user", "content": "It started 3 days ago"},
            {"role": "bot", "content": reply2},
        ])
        resp3 = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "About 5 out of 10",
            "conversation_history": history,
        })
        assert resp3.status_code == 200

    def test_triage_with_patient_context(self, client, patient_headers):
        """TC-TRI-006: Triage accepts patient context."""
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I have dizziness",
            "conversation_history": [],
            "patient_context": {
                "age": 45,
                "gender": "Male",
                "conditions": ["Hypertension"],
            },
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data

    def test_triage_reaches_assessment(self, client, patient_headers):
        """TC-TRI-007: Triage reaches assessment after enough turns."""
        history = []
        messages = [
            "I have a headache",
            "Since yesterday morning",
            "About 6 out of 10",
            "Nothing helps much",
            "Also feeling a bit nauseous",
        ]
        for msg in messages:
            resp = client.post("/api/triage/chat", headers=patient_headers, json={
                "message": msg,
                "conversation_history": history,
            })
            assert resp.status_code == 200
            data = resp.json()
            history.append({"role": "user", "content": msg})
            history.append({"role": "bot", "content": data["reply"]})
            if data["stage"] == "assessment":
                assert data["triage_result"] is not None
                assert "tier" in data["triage_result"]
                break


class TestRedFlagDetection:
    def test_chest_pain_emergency(self, client, patient_headers):
        """TC-TRI-008: Chest pain triggers emergency response."""
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I have severe chest pain",
            "conversation_history": [],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_emergency"] is True
        assert data["stage"] == "assessment"
        assert data["triage_result"]["tier"] == "EMERGENT"

    def test_breathing_difficulty_emergency(self, client, patient_headers):
        """TC-TRI-009: Severe breathing difficulty triggers emergency."""
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I can't breathe properly, suffocating",
            "conversation_history": [],
        })
        assert resp.status_code == 200
        assert resp.json()["is_emergency"] is True

    def test_stroke_symptoms_emergency(self, client, patient_headers):
        """TC-TRI-010: Stroke symptoms trigger emergency."""
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I have sudden weakness on one side and slurred speech",
            "conversation_history": [],
        })
        assert resp.status_code == 200
        assert resp.json()["is_emergency"] is True

    def test_non_emergency_is_not_flagged(self, client, patient_headers):
        """TC-TRI-011: Normal symptoms do not trigger emergency."""
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": "I have a mild cough",
            "conversation_history": [],
        })
        assert resp.status_code == 200
        assert resp.json()["is_emergency"] is False

    def test_message_length_limit(self, client, patient_headers):
        """TC-TRI-012: Messages exceeding 500 chars are rejected."""
        long_msg = "a" * 501
        resp = client.post("/api/triage/chat", headers=patient_headers, json={
            "message": long_msg,
            "conversation_history": [],
        })
        assert resp.status_code == 400
