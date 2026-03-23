"""CLI tests for parse_graph command using Click CliRunner."""

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from app.cli.parse_graph import cli

GOOD_XML = "samples/good/sample_graph_1.xml"
INVALID_XML = "samples/invalid/sample_graph_invalid_1.xml"


class TestPrintFlag:
    def test_print_valid_xml_outputs_json(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--file-path", GOOD_XML, "--print"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "g1"
        assert data["name"] == "Sample Graph 1"
        assert len(data["nodes"]) == 5
        assert len(data["edges"]) == 5

    def test_print_invalid_xml_exits_with_code_1(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--file-path", INVALID_XML, "--print"])
        assert result.exit_code == 1


class TestInsertFlag:
    def test_insert_valid_xml_prints_graph_id(self):
        runner = CliRunner()

        with patch("app.cli.parse_graph.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = iter([mock_session])
            with patch("app.cli.parse_graph.GraphService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.insert_graph.return_value = "g1"
                mock_service_cls.return_value = mock_service

                result = runner.invoke(
                    cli,
                    ["--file-path", GOOD_XML, "--insert"],
                )

        assert result.exit_code == 0
        assert "g1" in result.output

    def test_insert_db_error_exits_with_code_1(self):
        runner = CliRunner()

        with patch("app.cli.parse_graph.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = iter([mock_session])
            with patch("app.cli.parse_graph.GraphService") as mock_service_cls:
                mock_service = MagicMock()
                mock_service.insert_graph.side_effect = Exception("DB connection failed")
                mock_service_cls.return_value = mock_service

                result = runner.invoke(
                    cli,
                    ["--file-path", GOOD_XML, "--insert"],
                )

        assert result.exit_code == 1

    def test_insert_invalid_xml_exits_with_code_1(self):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--file-path", INVALID_XML, "--insert"],
            env={"DATABASE_URL": "postgresql://fake/fake"},
        )
        assert result.exit_code == 1


class TestMissingFilePath:
    def test_missing_file_path_shows_usage_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code != 0
