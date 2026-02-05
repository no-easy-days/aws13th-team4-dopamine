import random
import secrets
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.domain.friend.repository import FriendRepository
from app.domain.game.models import Game, GameResult, GamePayer
from app.domain.game.repository import GameRepository, GameResultRepository, GamePayerRepository
from app.domain.room.models import Room
from app.domain.room.repository import RoomRepository, RoomParticipantRepository
from app.domain.room.schemas import RoomCreate, ProductRoomCreate, RoomDetailResponse, RoomResponse, ParticipantResponse, ReadyRequest, GameResultInfo, ProductInfo
from app.domain.wishlist.models import WishlistItem


class RoomService:
    def __init__(
        self,
        room_repository: RoomRepository | None = None,
        participant_repository: RoomParticipantRepository | None = None,
        friend_repository: FriendRepository | None = None,
        game_repository: GameRepository | None = None,
        game_result_repository: GameResultRepository | None = None,
        game_payer_repository: GamePayerRepository | None = None,
    ) -> None:
        self.room_repository = room_repository or RoomRepository()
        self.participant_repository = participant_repository or RoomParticipantRepository()
        self.friend_repository = friend_repository or FriendRepository()
        self.game_repository = game_repository or GameRepository()
        self.game_result_repository = game_result_repository or GameResultRepository()
        self.game_payer_repository = game_payer_repository or GamePayerRepository()

    def create_room(self, db: Session, user_id: int, payload: RoomCreate) -> RoomResponse:
        """위시리스트 아이템으로 방 생성"""
        # 위시리스트 아이템 확인
        wishlist_item = db.query(WishlistItem).filter(
            WishlistItem.id == payload.wishlist_item_id,
            WishlistItem.user_id == user_id,
        ).first()

        if not wishlist_item:
            raise NotFoundException(message="Wishlist item not found")

        # 방 생성
        room = self.room_repository.create(
            db,
            room_type="WISHLIST_GIFT",
            title=payload.title,
            max_participants=payload.max_participants,
            owner_user_id=user_id,
            product_id=wishlist_item.product_id,
            gift_owner_user_id=user_id,
        )

        response = RoomResponse.model_validate(room)
        response.current_participant_count = 0
        return response

    def create_product_room(self, db: Session, user_id: int, product_id: int, payload: ProductRoomCreate) -> RoomResponse:
        """상품 기반 방 생성 (PRODUCT_LADDER)"""
        from app.domain.product.models import Product

        # 상품 존재 확인
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundException(message="Product not found")

        # 방 생성
        room = self.room_repository.create(
            db,
            room_type="PRODUCT_LADDER",
            title=payload.title,
            max_participants=payload.max_participants,
            owner_user_id=user_id,
            product_id=product_id,
            gift_owner_user_id=None,  # PRODUCT_LADDER는 선물받는 대상이 미정
        )

        # PRODUCT_LADDER: 방장도 참여자로 자동 등록
        self.participant_repository.create(db, room.id, user_id, role="OWNER")

        response = RoomResponse.model_validate(room)
        response.current_participant_count = 1  # 방장이 참여자로 포함
        return response

    def get_room_detail(self, db: Session, user_id: int, room_id: int) -> RoomDetailResponse:
        """방 상세 조회 (입장 화면)"""
        room = self.room_repository.get_by_id(db, room_id)
        if not room:
            raise NotFoundException(message="Room not found")

        if room.status == "DELETED":
            raise NotFoundException(message="Room not found")

        # WISHLIST_GIFT: 방장이거나 친구인지 확인
        # PRODUCT_LADDER: 누구나 조회 가능
        if room.room_type == "WISHLIST_GIFT":
            is_owner = room.owner_user_id == user_id
            is_friend = self.friend_repository.get_by_owner_and_friend(
                db, owner_user_id=user_id, friend_user_id=room.gift_owner_user_id
            )
            if not is_owner and not is_friend:
                raise ForbiddenException(message="Not authorized to view this room")

        # 참여자 목록
        participants = self.participant_repository.list_by_room(db, room_id, state="JOINED")

        response = RoomDetailResponse.model_validate(room)
        response.participants = [ParticipantResponse.model_validate(p) for p in participants]
        response.current_participant_count = len(participants)
        response.current_ready_count = self.participant_repository.count_ready(db, room_id)

        # 상품 정보 조회
        if room.product_id:
            from app.domain.product.models import Product
            product = db.query(Product).filter(Product.id == room.product_id).first()
            if product:
                response.product = ProductInfo.model_validate(product)

        # 게임 완료 시 결과 포함
        if room.status == "DONE":
            game = self.game_repository.get_by_room(db, room_id)
            if game:
                game_result = self.game_result_repository.get_by_game(db, game.id)
                if game_result:
                    ready_participants = [p for p in participants if p.is_ready]
                    participant_user_ids = [p.user_id for p in ready_participants]

                    if room.room_type == "WISHLIST_GIFT":
                        # WISHLIST_GIFT: 방장은 참여자 목록만, 참여자는 당첨자만
                        is_recipient = user_id == room.gift_owner_user_id
                        if is_recipient:
                            response.game_result = GameResultInfo(
                                game_id=game_result.game_id,
                                payer_user_id=None,
                                recipient_user_id=game_result.recipient_user_id,
                                product_id=game_result.product_id,
                                participant_user_ids=participant_user_ids,
                            )
                        else:
                            response.game_result = GameResultInfo(
                                game_id=game_result.game_id,
                                payer_user_id=game_result.payer_user_id,
                                recipient_user_id=game_result.recipient_user_id,
                                product_id=game_result.product_id,
                                participant_user_ids=[],
                            )
                    else:
                        # PRODUCT_LADDER: 모두에게 당첨자(recipient) 공개
                        # payer_user_ids는 game_payers 테이블에서 조회
                        payers = self.game_payer_repository.list_by_game_result(db, game_result.id)
                        payer_user_ids = [p.user_id for p in payers]
                        response.game_result = GameResultInfo(
                            game_id=game_result.game_id,
                            payer_user_id=None,
                            recipient_user_id=game_result.recipient_user_id,
                            product_id=game_result.product_id,
                            participant_user_ids=participant_user_ids,
                            payer_user_ids=payer_user_ids,
                        )

        return response

    def _to_room_response(self, db: Session, room: Room) -> RoomResponse:
        """Room 객체를 RoomResponse로 변환 (참여자 수 포함)"""
        response = RoomResponse.model_validate(room)
        response.current_participant_count = self.participant_repository.count_joined(db, room.id)
        return response

    def list_my_rooms(self, db: Session, user_id: int) -> List[RoomResponse]:
        """내가 만든 방 목록"""
        rooms = self.room_repository.list_by_gift_owner(db, user_id)
        return [self._to_room_response(db, room) for room in rooms]

    def list_friend_rooms(self, db: Session, user_id: int) -> List[RoomResponse]:
        """친구들의 OPEN 상태 방 목록"""
        # 내 친구 목록 가져오기
        friends = self.friend_repository.list_by_owner(db, user_id)
        friend_user_ids = [f.friend_user_id for f in friends]

        if not friend_user_ids:
            return []

        rooms = self.room_repository.list_open_rooms_for_friend(db, friend_user_ids)
        return [self._to_room_response(db, room) for room in rooms]

    def list_participating_rooms(self, db: Session, user_id: int) -> List[RoomResponse]:
        """내가 참여 중인 방 목록 (내가 만든 방 제외)"""
        rooms = self.participant_repository.list_rooms_by_participant(db, user_id)
        return [self._to_room_response(db, room) for room in rooms]

    def list_rooms_by_friend(self, db: Session, user_id: int, friend_user_id: int) -> List[RoomResponse]:
        """특정 친구의 OPEN 상태 방 목록"""
        # 친구인지 확인
        is_friend = self.friend_repository.get_by_owner_and_friend(
            db, owner_user_id=user_id, friend_user_id=friend_user_id
        )
        if not is_friend:
            raise ForbiddenException(message="Not a friend")

        rooms = self.room_repository.list_by_friend(db, friend_user_id)
        return [self._to_room_response(db, room) for room in rooms]

    def list_rooms_by_product(self, db: Session, product_id: int) -> List[RoomResponse]:
        """특정 상품의 OPEN 상태 PRODUCT_LADDER 방 목록"""
        rooms = self.room_repository.list_by_product(db, product_id)
        return [self._to_room_response(db, room) for room in rooms]

    def list_rooms_by_source_product(self, db: Session, product_id: int) -> List[RoomResponse]:
        """같은 네이버 상품(source_product_id)의 모든 OPEN 상태 PRODUCT_LADDER 방 목록"""
        from app.domain.product.models import Product

        # product_id로 source, source_product_id 조회
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return []

        # source_product_id로 방 검색
        rooms = self.room_repository.list_by_source_product(db, product.source, product.source_product_id)
        return [self._to_room_response(db, room) for room in rooms]

    def join_room(self, db: Session, user_id: int, room_id: int) -> ParticipantResponse:
        """방 입장"""
        room = self.room_repository.get_by_id(db, room_id)
        if not room:
            raise NotFoundException(message="Room not found")

        if room.status != "OPEN":
            raise BadRequestException(message="Room is not open")

        # WISHLIST_GIFT: 방장은 입장 불가 (본인이 선물 받는 사람이므로)
        # PRODUCT_LADDER: 방장도 참여 가능
        if room.room_type == "WISHLIST_GIFT" and room.owner_user_id == user_id:
            raise BadRequestException(message="Owner cannot join as participant")

        # WISHLIST_GIFT: 친구인지 확인
        # PRODUCT_LADDER: 누구나 입장 가능
        if room.room_type == "WISHLIST_GIFT":
            is_friend = self.friend_repository.get_by_owner_and_friend(
                db, owner_user_id=user_id, friend_user_id=room.gift_owner_user_id
            )
            if not is_friend:
                raise ForbiddenException(message="Only friends can join")

        # 기존 참여 기록 확인
        existing = self.participant_repository.get_by_room_and_user(db, room_id, user_id)
        if existing:
            if existing.state == "JOINED":
                raise BadRequestException(message="Already joined")
            # LEFT 상태면 재입장 처리
            participant = self.participant_repository.rejoin(db, existing)
            return ParticipantResponse.model_validate(participant)

        # 신규 입장
        participant = self.participant_repository.create(db, room_id, user_id, role="MEMBER")
        return ParticipantResponse.model_validate(participant)

    def set_ready(self, db: Session, user_id: int, room_id: int, is_ready: bool) -> Tuple[ParticipantResponse, Optional[GameResult], Optional[List[int]]]:
        """레디 상태 변경. 정원이 다 차면 자동으로 사다리타기 시작."""
        try:
            # 비관적 락으로 방 조회 (동시성 제어)
            room = self.room_repository.get_by_id_for_update(db, room_id)
            if not room:
                raise NotFoundException(message="Room not found")

            if room.status != "OPEN":
                raise BadRequestException(message="Room is not open")

            # 참여자인지 확인
            participant = self.participant_repository.get_by_room_and_user(db, room_id, user_id)
            if not participant or participant.state != "JOINED":
                raise BadRequestException(message="Not a participant")

            # 레디하려는 경우 정원 체크 (락이 걸린 상태에서 카운트)
            if is_ready and not participant.is_ready:
                ready_count = self.participant_repository.count_ready(db, room_id)
                if ready_count >= room.max_participants:
                    raise BadRequestException(message="Ready slots are full")

            # 레디 상태 변경 (commit 없이 flush만)
            participant.is_ready = is_ready
            db.flush()

            # 정원이 다 찼는지 확인 후 자동 시작
            game_result = None
            payer_user_ids = None
            if is_ready:
                ready_count = self.participant_repository.count_ready(db, room_id)
                if ready_count >= room.max_participants:
                    # 방 상태를 DONE으로 변경 (이미 락이 걸려있음)
                    room.status = "DONE"
                    db.flush()
                    game_result, payer_user_ids = self._start_ladder_game_internal(db, room)

            # 모든 작업 완료 후 커밋
            db.commit()
            db.refresh(participant)

            return ParticipantResponse.model_validate(participant), game_result, payer_user_ids

        except (NotFoundException, BadRequestException, ForbiddenException):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise BadRequestException(message="Failed to update ready status") from e

    def _start_ladder_game_internal(self, db: Session, room: Room) -> Tuple[GameResult, Optional[List[int]]]:
        """사다리타기 게임 시작 및 결과 생성 (트랜잭션 내부용 - commit 없음)"""
        # 레디한 참여자 목록
        participants = self.participant_repository.list_by_room(db, room.id, state="JOINED")
        ready_participants = [p for p in participants if p.is_ready]

        # Game 생성 (commit 없이)
        game = self._create_game_internal(db, room.id)

        if room.room_type == "WISHLIST_GIFT":
            # WISHLIST_GIFT: 랜덤으로 당첨자(payer) 선정, recipient는 방장
            payer = random.choice(ready_participants)
            game_result = self._create_game_result_internal(
                db,
                game_id=game.id,
                product_id=room.product_id,
                recipient_user_id=room.gift_owner_user_id,
                payer_user_id=payer.user_id,
            )
            return game_result, None
        else:
            # PRODUCT_LADDER: 랜덤으로 당첨자(recipient) 선정, 나머지는 payer
            winner = random.choice(ready_participants)
            game_result = self._create_game_result_internal(
                db,
                game_id=game.id,
                product_id=room.product_id,
                recipient_user_id=winner.user_id,
                payer_user_id=None,
            )
            # 당첨자 제외 나머지를 payer로 등록
            payer_user_ids = [p.user_id for p in ready_participants if p.user_id != winner.user_id]
            self._create_game_payers_internal(db, game_result.id, payer_user_ids)

            return game_result, payer_user_ids

    def _create_game_internal(self, db: Session, room_id: int) -> Game:
        """Game 생성 (트랜잭션 내부용 - commit 없음)"""
        now = datetime.utcnow()
        game = Game(
            room_id=room_id,
            status="DONE",
            started_at=now,
            ended_at=now,
            seed=secrets.token_hex(32),
        )
        db.add(game)
        db.flush()
        return game

    def _create_game_result_internal(
        self,
        db: Session,
        game_id: int,
        product_id: int,
        recipient_user_id: int,
        payer_user_id: Optional[int] = None,
    ) -> GameResult:
        """GameResult 생성 (트랜잭션 내부용 - commit 없음)"""
        result = GameResult(
            game_id=game_id,
            product_id=product_id,
            recipient_user_id=recipient_user_id,
            payer_user_id=payer_user_id,
            payment_status="PENDING",
        )
        db.add(result)
        db.flush()
        return result

    def _create_game_payers_internal(self, db: Session, game_result_id: int, user_ids: list[int]) -> None:
        """GamePayer 벌크 생성 (트랜잭션 내부용 - commit 없음)"""
        for user_id in user_ids:
            payer = GamePayer(
                game_result_id=game_result_id,
                user_id=user_id,
                payment_status="PENDING",
            )
            db.add(payer)
        db.flush()

    def leave_room(self, db: Session, user_id: int, room_id: int) -> None:
        """방 나가기 (레디 여부 상관없이 가능, 게임 진행/완료 시 불가)"""
        room = self.room_repository.get_by_id(db, room_id)
        if not room:
            raise NotFoundException(message="Room not found")

        if room.status in ("RUNNING", "DONE"):
            raise BadRequestException(message="Cannot leave after game started")

        # 참여자인지 확인
        participant = self.participant_repository.get_by_room_and_user(db, room_id, user_id)
        if not participant or participant.state != "JOINED":
            raise BadRequestException(message="Not a participant")

        # 나가기 (레디 상태였으면 is_ready=False로 변경됨 → 레디 카운트 자동 감소)
        self.participant_repository.leave(db, participant)

    def delete_room(self, db: Session, user_id: int, room_id: int) -> None:
        """방 삭제 (방장만 가능)"""
        room = self.room_repository.get_by_id(db, room_id)
        if not room:
            raise NotFoundException(message="Room not found")

        if room.owner_user_id != user_id:
            raise ForbiddenException(message="Only the owner can delete the room")

        if room.status == "RUNNING":
            raise BadRequestException(message="Cannot delete a running room")

        self.room_repository.soft_delete(db, room)
