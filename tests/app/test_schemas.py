"""Tests for Pydantic schema serialization edge cases."""

import json

from app.schemas import AnswerItem, CheapestPath, NodePaths


class TestCheapestPathSerialization:
    def test_path_serializes_as_false_when_no_path(self):
        """Critical: path=False must serialize as JSON `false`, not null or []."""
        cp = CheapestPath(**{"from": "a"}, to="h", path=False)
        data = json.loads(cp.model_dump_json(by_alias=True))
        assert data["path"] is False, f"Expected false, got {data['path']!r}"

    def test_path_serializes_as_list_when_path_exists(self):
        cp = CheapestPath(**{"from": "a"}, to="e", path=["a", "e"])
        data = json.loads(cp.model_dump_json(by_alias=True))
        assert data["path"] == ["a", "e"]

    def test_from_alias_in_dict(self):
        cp = CheapestPath(**{"from": "a"}, to="e", path=["a", "e"])
        dumped = cp.model_dump(by_alias=True)
        assert "from" in dumped
        assert dumped["from"] == "a"

    def test_from_alias_in_json(self):
        cp = CheapestPath(**{"from": "x"}, to="y", path=False)
        data = json.loads(cp.model_dump_json(by_alias=True))
        assert "from" in data
        assert data["from"] == "x"


class TestNodePathsSerialization:
    def test_from_alias_in_json(self):
        np = NodePaths(**{"from": "a"}, to="e", paths=[["a", "e"]])
        data = json.loads(np.model_dump_json(by_alias=True))
        assert "from" in data
        assert data["from"] == "a"

    def test_empty_paths(self):
        # An empty list [] is a distinct valid state (e.g. start==end with no self-loops).
        # When no path exists between disconnected nodes, the service returns False instead.
        np = NodePaths(**{"from": "a"}, to="h", paths=[])
        data = json.loads(np.model_dump_json(by_alias=True))
        assert data["paths"] == []

    def test_paths_serializes_as_false_when_no_paths(self):
        """Critical: paths=False must serialize as JSON `false`, not null or []."""
        np = NodePaths(**{"from": "a"}, to="h", paths=False)
        data = json.loads(np.model_dump_json(by_alias=True))
        assert data["paths"] is False, f"Expected false, got {data['paths']!r}"


class TestAnswerItemNoneExclusion:
    def test_only_paths_set_omits_cheapest_key(self):
        """AnswerItem with only paths set must not include a cheapest key in JSON."""
        np = NodePaths(**{"from": "a"}, to="e", paths=[["a", "e"]])
        item = AnswerItem(paths=np)
        data = json.loads(item.model_dump_json(by_alias=True))
        assert "paths" in data
        assert "cheapest" not in data, f"cheapest key should be absent, got: {data}"

    def test_only_cheapest_set_omits_paths_key(self):
        """AnswerItem with only cheapest set must not include a paths key in JSON."""
        cp = CheapestPath(**{"from": "a"}, to="e", path=["a", "e"])
        item = AnswerItem(cheapest=cp)
        data = json.loads(item.model_dump_json(by_alias=True))
        assert "cheapest" in data
        assert "paths" not in data, f"paths key should be absent, got: {data}"
