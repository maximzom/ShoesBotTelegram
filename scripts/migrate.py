#!/usr/bin/env python3
"""
Database migration script.
Run with: python scripts/migrate.py
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_sqlite_to_postgres(source_db: str, target_db: str):
    """
    Migrate from SQLite to PostgreSQL.

    Args:
        source_db: SQLite database path
        target_db: PostgreSQL connection string
    """
    logger.info(f"Migrating from {source_db} to {target_db}")

    try:
        # Create engines
        source_engine = create_engine(f"sqlite:///{source_db}")
        target_engine = create_engine(target_db)

        # Get table names
        with source_engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)).fetchall()

        logger.info(f"Found {len(tables)} tables to migrate")

        for table_name in tables:
            table = table_name[0]
            logger.info(f"Migrating table: {table}")

            # Read data from source
            with source_engine.connect() as conn:
                data = conn.execute(text(f"SELECT * FROM {table}")).fetchall()
                columns = [col[0] for col in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()]

            if not data:
                logger.info(f"Table {table} is empty, skipping")
                continue

            # Prepare insert statement
            placeholders = ', '.join(['%s'] * len(columns))
            col_names = ', '.join([f'"{col}"' for col in columns])
            insert_sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

            # Insert into target
            with target_engine.connect() as conn:
                for row in data:
                    try:
                        conn.execute(text(insert_sql), row)
                    except SQLAlchemyError as e:
                        logger.warning(f"Error inserting row into {table}: {e}")
                conn.commit()

            logger.info(f"Migrated {len(data)} rows from {table}")

        logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


def create_backup_sql(db_path: str, output_file: str):
    """
    Create SQL backup of database.

    Args:
        db_path: SQLite database path
        output_file: Output SQL file
    """
    import sqlite3

    logger.info(f"Creating backup of {db_path} to {output_file}")

    try:
        conn = sqlite3.connect(db_path)

        with open(output_file, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")

        conn.close()

        logger.info(f"Backup created: {output_file}")

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        sys.exit(1)


def restore_from_sql(db_path: str, sql_file: str):
    """
    Restore database from SQL file.

    Args:
        db_path: SQLite database path
        sql_file: SQL file to restore from
    """
    import sqlite3

    logger.info(f"Restoring {db_path} from {sql_file}")

    try:
        # Remove existing database
        if os.path.exists(db_path):
            os.remove(db_path)

        conn = sqlite3.connect(db_path)

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        conn.executescript(sql_script)
        conn.commit()
        conn.close()

        logger.info(f"Database restored from {sql_file}")

    except Exception as e:
        logger.error(f"Restore failed: {e}")
        sys.exit(1)


def main():
    """Main migration script."""
    import argparse

    parser = argparse.ArgumentParser(description="Database migration utilities")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate SQLite to PostgreSQL')
    migrate_parser.add_argument('--source', required=True, help='SQLite database path')
    migrate_parser.add_argument('--target', required=True, help='PostgreSQL connection string')

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create SQL backup')
    backup_parser.add_argument('--db', default='data/shop.db', help='Database path')
    backup_parser.add_argument('--output', default='backup.sql', help='Output SQL file')

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from SQL backup')
    restore_parser.add_argument('--db', default='data/shop.db', help='Database path')
    restore_parser.add_argument('--input', required=True, help='Input SQL file')

    args = parser.parse_args()

    if args.command == 'migrate':
        migrate_sqlite_to_postgres(args.source, args.target)

    elif args.command == 'backup':
        create_backup_sql(args.db, args.output)

    elif args.command == 'restore':
        restore_from_sql(args.db, args.input)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()