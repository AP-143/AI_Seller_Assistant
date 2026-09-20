"""Self-check for the fragile bit: Telegram caption format parsing.
Run: python tests/test_parsing.py"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_caption(caption: str):
    parts = [p.strip() for p in caption.split("|")]
    if len(parts) != 3:
        return None
    name, category, cost_raw = parts
    digits = "".join(ch for ch in cost_raw if ch.isdigit())
    return name, category, int(digits) if digits else None


def demo():
    assert parse_caption("Tas Rajut Mini | Tas Wanita | 45000") == ("Tas Rajut Mini", "Tas Wanita", 45000)
    assert parse_caption("Rp 45.000 | x | y")[0] == "Rp 45.000"
    assert parse_caption("cuma dua | bagian") is None
    assert parse_caption("A | B | mahal")[2] is None

    print("ok")


if __name__ == "__main__":
    demo()
