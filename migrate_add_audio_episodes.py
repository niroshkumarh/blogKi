"""
Migration: add audio_episodes table.

Usage:
  python migrate_add_audio_episodes.py
"""
from app import app
from models import db  # noqa: F401  (ensures db is initialized)
import models  # noqa: F401  (ensures AudioEpisode model is imported/registered)


def main():
    with app.app_context():
        db.create_all()
        print("OK: audio_episodes table ensured (db.create_all).")


if __name__ == "__main__":
    main()

