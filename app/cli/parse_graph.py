"""CLI application for parsing XML graph files and optionally inserting into the DB."""

import json

import click

from app.config import load_config
from app.db import get_session
from app.logging import configure_logging, get_logger
from app.services.graph_service import GraphService, GraphXmlParseError, XmlGraphParser

configure_logging(load_config(), cli_mode=True)
_logger = get_logger(__name__)

@click.command()
@click.option("--file-path", required=True, help="Path to the XML graph file to parse")
@click.option("--print", "do_print", is_flag=True, default=False, help="Print parsed graph as JSON")
@click.option(
    "--insert", "do_insert", is_flag=True, default=False,
    help="Insert parsed graph into the database",
)
def cli(file_path: str, do_print: bool, do_insert: bool) -> None:
    """Parse a directed weighted graph from an XML file.

    See example files in samples/good/ for structure.
    """
    click.echo(f"Parsing XML file {file_path}...", err=True)
    _logger.debug("parse-xml-file", file_path=file_path, do_print=do_print, do_insert=do_insert)

    parser = XmlGraphParser()
    try:
        graph = parser.from_xml_file(file_path)
    except GraphXmlParseError as exc:
        click.echo(str(exc), err=True)
        raise click.exceptions.Exit(code=1) from exc

    if do_print:
        click.echo(json.dumps(graph.model_dump(), indent=2))

    if do_insert:
        try:
            # Note: would have preferred to use session.begin() context manager, but somehow that is
            # messing up with tests/MagicMock. Might fix.
            session = next(get_session())
            graph_id = GraphService(session=session).insert_graph(graph)
            session.commit()
            click.echo(f"Graph inserted to database with id: {graph_id}")
        except Exception as exc:
            click.echo(f"Database error: {exc}", err=True)
            session.rollback()
            raise click.exceptions.Exit(code=1) from exc
        finally:
            session.close()
    else:
        click.echo("(not inserted to database)", err=True)

    if not do_print and not do_insert:
        click.echo(
            f"Graph `{graph.name}` parsed successfully ({len(graph.nodes)} nodes, {len(graph.edges)} edges). "
            f"Use --print to print it, or --insert to insert it into the database."
        )
