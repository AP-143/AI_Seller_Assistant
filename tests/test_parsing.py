"""Self-check for the fragile bit: Telegram caption format parsing.
Run: python tests/test_parsing.py"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.handlers import _parse_caption_fast


def demo():
    assert _parse_caption_fast("Tas Rajut Mini | Tas Wanita | 45000") == ("Tas Rajut Mini", "Tas Wanita", 45000)
    assert _parse_caption_fast("Rp 45.000 | x | y") is None  # no digits in price part -> falls through to Gemini
    assert _parse_caption_fast("cuma dua | bagian") is None
    assert _parse_caption_fast("A | B | mahal") is None
    assert _parse_caption_fast("nama produk bebas kategori gaming modal 400rb") is None

    print("ok")


if __name__ == "__main__":
    demo()
