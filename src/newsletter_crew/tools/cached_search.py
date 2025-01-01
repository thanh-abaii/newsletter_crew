import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict
from exa_py import Exa
from crewai_tools import BaseTool

CACHE_FILE_PATH = "search_cache.json"
CACHE_TTL_SECONDS = 3600  # 1 giờ (3600 giây)


def load_cache() -> Dict:
    """Đọc cache từ file JSON, nếu có."""
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}


def save_cache(cache: Dict) -> None:
    """Ghi cache ra file JSON."""
    with open(CACHE_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(cache, file)


class CachedSearch(BaseTool):
    """
    Tool tìm kiếm (Search) kèm cơ chế caching.
    Nếu cùng một 'search_query' xuất hiện lần nữa
    và còn hạn TTL, sẽ trả về kết quả từ cache
    thay vì gọi lại Exa API.
    """
    name: str = "Cached Search Tool"
    description: str = (
        "Searches the web based on a search query. Results are only from the last week. "
        "Uses the Exa API and caches the results to avoid repeated calls."
    )

    def _run(self, search_query: str) -> str:
        # Bước 1: Tải cache hiện có
        cache = load_cache()

        # Bước 2: Kiểm tra xem query có trong cache và chưa hết TTL hay không
        if search_query in cache:
            entry = cache[search_query]
            if time.time() - entry["timestamp"] < CACHE_TTL_SECONDS:
                # Nếu còn hạn thì trả về dữ liệu cũ
                return entry["response"]

        # Bước 3: Nếu chưa có hoặc đã hết hạn, gọi API Exa để lấy dữ liệu mới
        one_week_ago = datetime.now() - timedelta(days=7)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")

        exa = Exa(os.getenv("EXA_API_KEY"))
        search_response = exa.search_and_contents(
            search_query,
            use_autoprompt=True,
            start_published_date=date_cutoff,
            text={"include_html_tags": False, "max_characters": 8000},
        )

        # Ép kiểu sang chuỗi để JSON có thể serialize
        search_response_str = str(search_response)

        # Bước 4: Ghi kết quả mới vào cache
        cache[search_query] = {
            "timestamp": time.time(),
            "response": search_response_str,
        }
        save_cache(cache)

        return search_response_str
