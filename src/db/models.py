from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True, index=True)
    board = Column(JSON, nullable=False)
    current_player = Column(String, default="X", nullable=False)
    winner = Column(String, nullable=True)
    is_draw = Column(Boolean, default=False, nullable=False)
    player_x = Column(String, nullable=True)
    player_o = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    @property
    def players(self):
        """Вычисляемое свойство для совместимости с Pydantic схемой"""
        return {"X": self.player_x, "O": self.player_o}

    def to_dict(self):
        """Конвертирует модель в словарь для Pydantic"""
        return {
            "id": self.id,
            "board": self.board,
            "current_player": self.current_player,
            "winner": self.winner,
            "is_draw": self.is_draw,
            "players": self.players,
            "is_active": self.is_active
        }