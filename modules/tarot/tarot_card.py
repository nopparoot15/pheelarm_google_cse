from dataclasses import dataclass
from typing import Optional

@dataclass
class TarotCard:
    name: str
    upright_meaning: str
    reversed_meaning: str
    arcana: str  # "Major" หรือ "Minor"
    suit: Optional[str] = None  # เฉพาะ Minor Arcana
    number: Optional[int] = None

    def get_meaning(self, is_reversed: bool) -> str:
        return self.reversed_meaning if is_reversed else self.upright_meaning
