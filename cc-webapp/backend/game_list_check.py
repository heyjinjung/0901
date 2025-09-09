#!/bin/bash
# 스크립트: game_list_check.py
from app.models.game_models import Game
from app.database import SessionLocal

db = SessionLocal()
games = db.query(Game).all()

for g in games:
    print(f"id: {g.id}, name: {g.name}, type: {g.game_type}")

db.close()
