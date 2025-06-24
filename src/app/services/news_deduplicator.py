import re
from datetime import timedelta
import time
from urllib.parse import parse_qs, urlparse, urlunparse

from redis import Redis
from simhash import Simhash


class Deduplicator:
    def __init__(self, redis: Redis):
        self.redis = redis

        self.url_ttl = timedelta(hours=48).total_seconds()
        self.simhash_ttl = timedelta(hours=24).total_seconds()
        self.title_threshold = 3
        self.description_threshold = 5
        self.min_description_length = 50

        self.local_url_cache = set()

    def normalize_url(self, url):

        parsed = urlparse(url)

        query_params = parse_qs(parsed.query)
        clean_params = {
            k: v
            for k, v in query_params.items()
            if not k.startswith(("utm_", "fbclid", "yclid", "_openstat"))
        }

        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc.lower(),
                parsed.path,
                parsed.params,
                "&".join(f"{k}={v[0]}" for k, v in clean_params.items()),
                "",
            )
        )

    def calculate_simhash(self, text, hash_bits=64):

        if not text:
            return 0

        tokens = re.findall(r"\b\w{3,}\b", text.lower())
        return Simhash(tokens, f=hash_bits).value

    def is_duplicate(self, news_item):
        canonical_url = self.normalize_url(news_item["url"])
        url_key = f"url:{canonical_url}"

        if self._is_url_duplicate(url_key):
            return True

        title_hash = self.calculate_simhash(news_item["title"])
        if self._is_simhash_duplicate("title", title_hash, self.title_threshold):
            return True

        if (
            news_item.get("description")
            and len(news_item["description"]) > self.min_description_length
        ):
            description_hash = self.calculate_simhash(news_item["description"])
            if self._is_simhash_duplicate(
                "description", description_hash, self.description_threshold
            ):
                return True

        self._store_fingerprints(news_item, canonical_url, title_hash)
        return False

    def _is_url_duplicate(self, url_key):
        if url_key in self.local_url_cache:
            return True

        if self.redis.exists(url_key):
            self.local_url_cache.add(url_key)
            return True

        return False

    def _is_simhash_duplicate(self, hash_type, target_hash, threshold):
        set_key = f"simhash:{hash_type}"

        min_score = time.time() - self.simhash_ttl
        candidates = self.redis.zrangebyscore(
            set_key, min=min_score, max="+inf", withscores=False
        )

        for candidate_bytes in candidates:
            candidate_hash = int(candidate_bytes)
            distance = self._hamming_distance(target_hash, candidate_hash)
            if distance <= threshold:
                return True

        return False

    def _store_fingerprints(self, news_item, canonical_url, title_hash):
        url_key = f"url:{canonical_url}"
        self.redis.set(url_key, news_item["id"], ex=int(self.url_ttl))
        self.local_url_cache.add(url_key)

        title_set_key = "simhash:title"
        self.redis.zadd(title_set_key, {str(title_hash): time.time()})

        if "description" in news_item:
            description_hash = self.calculate_simhash(news_item["description"])
            description_set_key = "simhash:description"
            self.redis.zadd(description_set_key, {str(description_hash): time.time()})

        self.redis.expire(title_set_key, int(self.simhash_ttl))
        if "description" in news_item:
            self.redis.expire(description_set_key, int(self.simhash_ttl))

    def _hamming_distance(self, hash1, hash2, bits=64):
        x = (hash1 ^ hash2) & ((1 << bits) - 1)
        distance = 0
        while x:
            distance += 1
            x &= x - 1
        return distance

    def cleanup_old_entries(self):
        cursor = "0"
        while cursor != 0:
            cursor, keys = self.redis.scan(cursor=cursor, match="url:*", count=1000)
            for key in keys:
                ttl = self.redis.ttl(key)
                if ttl < 0:
                    self.redis.delete(key)

        self.local_url_cache = {
            url for url in self.local_url_cache if self.redis.exists(url)
        }


