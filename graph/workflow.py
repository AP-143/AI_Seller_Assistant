from langgraph.graph import StateGraph, START, END
from graph.state import SellerState
from graph.nodes import enhance_photo, check_competitor_price, generate_listing, generate_captions

_builder = StateGraph(SellerState)
_builder.add_node("enhance_photo", enhance_photo)
_builder.add_node("check_competitor_price", check_competitor_price)
_builder.add_node("generate_listing", generate_listing)
_builder.add_node("generate_captions", generate_captions)

# photo enhance + price check run independent of each other, both feed listing gen
_builder.add_edge(START, "enhance_photo")
_builder.add_edge(START, "check_competitor_price")
_builder.add_edge("enhance_photo", "generate_listing")
_builder.add_edge("check_competitor_price", "generate_listing")
_builder.add_edge("generate_listing", "generate_captions")
_builder.add_edge("generate_captions", END)

graph = _builder.compile()


def run(photo_url: str, product_name: str, category: str, cost_price: int) -> SellerState:
    return graph.invoke(
        {
            "photo_url": photo_url,
            "product_name": product_name,
            "category": category,
            "cost_price": cost_price,
        }
    )
