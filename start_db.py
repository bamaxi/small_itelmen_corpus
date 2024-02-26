import argparse
import logging
from pathlib import Path

from app import db, create_app
from app.update_db.update import (
    add_file_data,
    BASE_FILE,
    set_parse_logging,
    make_argparser,
    act_on_args,
)


if __name__ == "__main__":
    parser = make_argparser(
        prog_name=Path(__file__).name, description="Init database and add desired texts"
    )
    args = parser.parse_args()

    print(args)
    act_on_args(args)
