"""Functional tests for POST /query and /query/{graph_id} using a real PostgreSQL database."""

import json

import pytest

from tests.conftest import make_sample_graph_1, make_sample_graph_3


class TestQueryEndpointMixedQueries:
    @pytest.fixture(autouse=True)
    def seed(self, db_session):
        make_sample_graph_1(db_session)

    def test_mixed_query_sample_graph_1(self, client):
        """Full request matching sample_graph_1_input.json → sample_graph_1_output.json."""
        payload = {
            "queries": [
                {"paths": {"start": "a", "end": "e"}},
                {"cheapest": {"start": "a", "end": "e"}},
                {"cheapest": {"start": "a", "end": "h"}},
            ]
        }
        resp = client.post("/query/g1", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        answers = data["answers"]
        assert len(answers) == 3

        # --- paths answer ---
        paths_answer = answers[0]["paths"]
        assert paths_answer["from"] == "a"
        assert paths_answer["to"] == "e"
        paths = [tuple(p) for p in paths_answer["paths"]]
        assert ("a", "b", "e") in paths
        assert ("a", "e") in paths

        # --- cheapest a->e ---
        cheapest_ae = answers[1]["cheapest"]
        assert cheapest_ae["from"] == "a"
        assert cheapest_ae["to"] == "e"
        assert cheapest_ae["path"] == ["a", "e"]

        # --- cheapest a->h (no path) ---
        cheapest_ah = answers[2]["cheapest"]
        assert cheapest_ah["from"] == "a"
        assert cheapest_ah["to"] == "h"
        assert cheapest_ah["path"] is False

    def test_response_matches_expected_output(self, client):
        """Compare against the canonical sample_graph_1_output.json."""
        with open("samples/good/sample_graph_1_output.json") as f:
            expected = json.load(f)

        with open("samples/good/sample_graph_1_input.json") as f:
            payload = json.load(f)

        resp = client.post("/query/g1", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        # answers count matches
        assert len(data["answers"]) == len(expected["answers"])

        # paths query: same paths (order may differ)
        expected_paths = [tuple(p) for p in expected["answers"][0]["paths"]["paths"]]
        actual_paths = [tuple(p) for p in data["answers"][0]["paths"]["paths"]]
        assert set(expected_paths) == set(actual_paths)

        # cheapest a->e
        assert data["answers"][1]["cheapest"]["path"] == expected["answers"][1]["cheapest"]["path"]

        # cheapest a->h → false
        assert data["answers"][2]["cheapest"]["path"] is False


class TestQueryEndpointCheapestPathsTiebreaker:
    @pytest.fixture(autouse=True)
    def seed(self, db_session):
        make_sample_graph_3(db_session)

    def test_equal_cost_tiebreaker(self, client):
        """graph_3: cheapest a->e picks path with fewest nodes (a->d->e, cost=4), when score is otherwise the same."""
        payload = {
            "queries": [
                {"cheapest": {"start": "a", "end": "e"}},
            ]
        }
        resp = client.post("/query/g3", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["answers"][0]["cheapest"]["path"] == ["a", "d", "e"]

    def test_response_matches_expected_output(self, client):
        """Compare against the canonical sample_graph_3_output.json."""
        with open("samples/good/sample_graph_3_input.json") as f:
            payload = json.load(f)
        with open("samples/good/sample_graph_3_output.json") as f:
            expected = json.load(f)

        resp = client.post("/query/g3", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["answers"][1]["cheapest"]["path"] == expected["answers"][1]["cheapest"]["path"]


class TestQueryEndpointGraphNotFound:
    def test_404_for_nonexistent_graph(self, client):
        payload = {"queries": [{"paths": {"start": "a", "end": "b"}}]}
        resp = client.post("/query/nonexistent", json=payload)
        assert resp.status_code == 404
        assert "nonexistent" in resp.json()["detail"]


class TestQueryItemValidation:
    @pytest.fixture(autouse=True)
    def seed(self, db_session):
        make_sample_graph_1(db_session)

    def test_422_when_both_paths_and_cheapest_set(self, client):
        """A query item with both paths and cheapest must return HTTP 422."""
        payload = {
            "queries": [
                {"paths": {"start": "a", "end": "e"}, "cheapest": {"start": "a", "end": "e"}}
            ]
        }
        resp = client.post("/query/g1", json=payload)
        assert resp.status_code == 422

    def test_422_when_neither_paths_nor_cheapest_set(self, client):
        """An empty query item (neither paths nor cheapest) must return HTTP 422."""
        payload = {"queries": [{}]}
        resp = client.post("/query/g1", json=payload)
        assert resp.status_code == 422


class TestQueryLatestEndpoint:
    def test_404_when_no_graphs_exist(self, client):
        payload = {"queries": [{"paths": {"start": "a", "end": "b"}}]}
        resp = client.post("/query", json=payload)
        assert resp.status_code == 404

    def test_queries_latest_graph(self, client, db_session):
        from tests.conftest import make_sample_graph_1

        make_sample_graph_1(db_session)
        payload = {"queries": [{"cheapest": {"start": "a", "end": "e"}}]}
        resp = client.post("/query", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["answers"][0]["cheapest"]["path"] == ["a", "e"]


class TestDisconnectedNodePaths:
    @pytest.fixture(autouse=True)
    def seed(self, db_session):
        make_sample_graph_1(db_session)

    def test_paths_false_for_disconnected_nodes(self, client):
        """When no path exists between nodes, paths must be false (not [] or null)."""
        payload = {"queries": [{"paths": {"start": "a", "end": "h"}}]}
        resp = client.post("/query/g1", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        paths_answer = data["answers"][0]["paths"]
        assert paths_answer["paths"] is False
