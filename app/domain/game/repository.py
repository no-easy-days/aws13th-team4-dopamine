import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.game.models import Game, GameResult


class GameRepository:
    @staticmethod
    def get_by_id(db: Session, game_id: int) -> Optional[Game]:
        return db.query(Game).filter(Game.id == game_id).first()

    @staticmethod
    def get_by_room(db: Session, room_id: int) -> Optional[Game]:
        return (
            db.query(Game)
            .filter(Game.room_id == room_id)
            .order_by(Game.created_at.desc())
            .first()
        )

    @staticmethod
    def create(db: Session, room_id: int, started_by_user_id: Optional[int] = None) -> Game:
        now = datetime.utcnow()
        game = Game(
            room_id=room_id,
            status="DONE",
            started_by_user_id=started_by_user_id,
            started_at=now,
            ended_at=now,
            seed=secrets.token_hex(32),
        )
        db.add(game)
        db.commit()
        db.refresh(game)
        return game


class GameResultRepository:
    @staticmethod
    def get_by_game(db: Session, game_id: int) -> Optional[GameResult]:
        return db.query(GameResult).filter(GameResult.game_id == game_id).first()

    @staticmethod
    def create(
        db: Session,
        game_id: int,
        product_id: int,
        recipient_user_id: int,
        payer_user_id: int,
    ) -> GameResult:
        result = GameResult(
            game_id=game_id,
            product_id=product_id,
            recipient_user_id=recipient_user_id,
            payer_user_id=payer_user_id,
            payment_status="PENDING",
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
