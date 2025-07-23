import hashlib
import re


class HashService:
    @staticmethod
    def generate(content: str) -> str:
        normalized = re.sub(r"\s+", "", content.lower().strip())
        return hashlib.sha256(normalized.encode()).hexdigest()
