"""Tavily wrapper: competitor price lookup."""
from tavily import TavilyClient
import config

_client = TavilyClient(api_key=config.TAVILY_API_KEY)


def search_competitor_prices(product_name: str, category: str) -> str:
    """Return raw search snippets mentioning prices; Claude parses these later."""
    query = f"harga {product_name} {category} Shopee Tokopedia"
    result = _client.search(query=query, max_results=5, search_depth="basic")
    snippets = [f"{r['title']}: {r['content']}" for r in result.get("results", [])]
    return "\n".join(snippets) if snippets else "no competitor data found"
