import requests
import os
from dotenv import load_dotenv
from typing import Dict, List
from datetime import datetime

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_SEARCH_URL = "https://openapi.naver.com/v1/search/shop.json"


class NaverShoppingService:
    # 네이버 쇼핑 검색 API 호출 및 결과 파싱

    @staticmethod
    def search_products(
        query: str,
        display: int = 10,
        start: int = 1,
        sort: str = "sim",
    ) -> Dict:
        """네이버 쇼핑 API로 상품 검색"""
        # 외부 API 호출
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        }

        params = {
            "query": query,
            "display": min(display, 100),  # 최대 100개 제한
            "start": start,
            "sort": sort,
        }

        try:
            response = requests.get(
                NAVER_SEARCH_URL,
                headers=headers,
                params=params,
                timeout=10,  # 10초 타임아웃
            )
            response.raise_for_status()  # 4xx, 5xx 에러 시 예외 발생
            return response.json()

        except requests.exceptions.Timeout:
            raise Exception("네이버 API 요청 시간 초과")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"네이버 API HTTP 에러: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"네이버 API 호출 실패: {str(e)}")

    @staticmethod
    def clean_html_tags(text: str) -> str:
        """HTML 태그 제거 (<b>, </b> 등)"""
        return text.replace("<b>", "").replace("</b>", "")

    @staticmethod
    def parse_product_item(item: Dict) -> Dict:
        """응답 필드를 Product 스키마로 변환"""
        return {
            "source": "NAVER",
            "source_product_id": item.get("productId", ""),
            "title": NaverShoppingService.clean_html_tags(item.get("title", "")),
            "image_url": item.get("image", ""),
            "link_url": item.get("link", ""),
            "mall_name": item.get("mallName", ""),
            "brand": item.get("brand", ""),
            "maker": item.get("maker", ""),
            "category1": item.get("category1", ""),
            "category2": item.get("category2", ""),
            "category3": item.get("category3", ""),
            "category4": item.get("category4", ""),
            "price": int(item.get("lprice", 0)),  # lprice = 최저가
            "last_fetched_at": datetime.utcnow(),
        }

    @staticmethod
    def parse_products(naver_response: Dict) -> List[Dict]:
        """네이버 API 전체 응답 파싱"""
        items = naver_response.get("items", [])
        return [NaverShoppingService.parse_product_item(item) for item in items]
