import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.game.models import Game, GameResult, GamePayer


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
        payer_user_id: Optional[int] = None,
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


class GamePayerRepository:
    """PRODUCT_LADDER용 다중 결제자 관리"""

    @staticmethod
    def create(db: Session, game_result_id: int, user_id: int) -> GamePayer:
        payer = GamePayer(
            game_result_id=game_result_id,
            user_id=user_id,
            payment_status="PENDING",
        )
        db.add(payer)
        db.commit()
        db.refresh(payer)
        return payer

    @staticmethod
    def create_bulk(db: Session, game_result_id: int, user_ids: list[int]) -> list[GamePayer]:
        payers = []
        for user_id in user_ids:
            payer = GamePayer(
                game_result_id=game_result_id,
                user_id=user_id,
                payment_status="PENDING",
            )
            db.add(payer)
            payers.append(payer)
        db.commit()
        for payer in payers:
            db.refresh(payer)
        return payers

    @staticmethod
    def list_by_game_result(db: Session, game_result_id: int) -> list[GamePayer]:
        return db.query(GamePayer).filter(GamePayer.game_result_id == game_result_id).all()
