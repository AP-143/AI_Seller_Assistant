import logging
from io import BytesIO
from telegram import InputMediaPhoto, Update
from telegram.ext import ContextTypes
from graph.workflow import run as run_graph

logger = logging.getLogger(__name__)

CAPTION_HELP = (
    "Kirim foto produk dengan caption format:\n"
    "Nama Produk | Kategori | Harga Modal\n\n"
    "Contoh: Tas Rajut Mini | Tas Wanita | 45000"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Aku bantu bikin foto + listing produk kamu.\n\n" + CAPTION_HELP
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    caption = update.message.caption or ""
    parts = [p.strip() for p in caption.split("|")]
    if len(parts) != 3:
        await update.message.reply_text(CAPTION_HELP)
        return

    product_name, category, cost_price_raw = parts
    try:
        cost_price = int("".join(ch for ch in cost_price_raw if ch.isdigit()))
    except ValueError:
        await update.message.reply_text("Harga modal harus angka. " + CAPTION_HELP)
        return

    await update.message.reply_text("Diterima, lagi diproses... (~30-60 detik)")

    photo = update.message.photo[-1]  # highest resolution
    file = await context.bot.get_file(photo.file_id)
    photo_url = file.file_path  # already a public https URL from Telegram

    try:
        result = run_graph(photo_url, product_name, category, cost_price)
    except Exception:
        logger.exception("graph run failed")
        await update.message.reply_text("Ada error pas proses. Coba lagi ya.")
        return

    media = [
        InputMediaPhoto(BytesIO(photo_bytes), caption=f"Foto studio-look: {product_name}" if i == 0 else None)
        for i, photo_bytes in enumerate(result["enhanced_photo_urls"])
    ]
    await update.message.reply_media_group(media=media)
    await update.message.reply_text(
        f"*JUDUL*\n{result['listing_title']}\n\n"
        f"*DESKRIPSI*\n{result['listing_description']}\n\n"
        f"*RANGE HARGA*\n{result['price_range']}",
        parse_mode="Markdown",
    )
    for i, caption_text in enumerate(result["captions"], 1):
        await update.message.reply_text(f"*Caption {i}*\n{caption_text}", parse_mode="Markdown")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(CAPTION_HELP)
