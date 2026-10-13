from pathlib import Path

from agile_board import db

SEED_SQL = (Path(__file__).parent.parent / "scripts" / "seed.sql").read_text()


def test_seed_populates_people_and_tasks(db_conn):
    db_conn.execute(SEED_SQL)

    names = sorted(name for _, name in db.get_all_people(db_conn))
    assert names == ["Jordan Ellis", "Noah Park", "Priya Shah"]
    assert len(db.get_all_tasks(db_conn)) == 12
    assert len(db.get_tasks_by_status(db_conn, "Done")) == 4
    assert len(db.get_tasks_by_status(db_conn, "In Progress")) == 3
    assert sum(row[5] is None for row in db.get_all_tasks(db_conn)) == 3


def test_seed_skips_when_people_exist(db_conn):
    db.create_person(db_conn, "Existing")
    db_conn.execute(SEED_SQL)
    assert len(db.get_all_people(db_conn)) == 1
