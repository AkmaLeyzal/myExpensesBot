import os
import telebot

import config
from parser import parse_expense, format_rupiah
import sheets_helper
from report_generator import generate_report

bot = telebot.TeleBot(config.BOT_API_TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def cmd_start(message):
    name = message.from_user.first_name or "kamu"
    text = (
        f"👋 <b>Halo, {name}!</b>\n\n"
        f"Saya adalah <b>💰 Expense Tracker Bot</b> — asisten pencatat pengeluaranmu.\n\n"
        f"📝 <b>Cara pakai:</b>\n"
        f"Cukup kirim pesan seperti:\n"
        f"<code>25k naspad rendang - tambah telur</code>\n"
        f"<code>150rb sepatu nike</code>\n"
        f"<code>5000 air mineral</code>\n\n"
        f"📊 <b>Lihat ringkasan:</b>\n"
        f"/today — Hari ini\n"
        f"/week — Minggu ini\n"
        f"/month — Bulan ini\n"
        f"/year — Tahun ini\n"
        f"/q1 /q2 /q3 /q4 — Per kuartal\n\n"
        f"📄 /report — Download laporan PDF\n"
        f"🗑 /delete — Hapus entri terakhir\n"
        f"❓ /help — Panduan lengkap"
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=["help"])
def cmd_help(message):
    text = (
        "📖 <b>Panduan Lengkap</b>\n\n"
        "━━━ <b>📝 Cara Catat Pengeluaran</b> ━━━\n"
        "Kirim pesan dengan format:\n"
        "<code>[harga] [nama item] - [deskripsi]</code>\n\n"
        "<b>Shorthand harga:</b>\n"
        "• <code>k</code> atau <code>rb</code> = ribu (×1.000)\n"
        "• <code>jt</code> = juta (×1.000.000)\n"
        "• Desimal OK: <code>2.5jt</code>, <code>1,5k</code>\n\n"
        "<b>Contoh:</b>\n"
        "• <code>25k naspad rendang - tambah telur</code>\n"
        "  → Rp 25.000 | naspad rendang | tambah telur\n"
        "• <code>150rb sepatu nike</code>\n"
        "  → Rp 150.000 | sepatu nike\n"
        "• <code>2.5jt laptop bekas</code>\n"
        "  → Rp 2.500.000 | laptop bekas\n\n"
        "<b>Separator deskripsi:</b> <code> - </code> atau <code>, </code>\n\n"
        "━━━ <b>📋 Daftar Command</b> ━━━\n\n"
        "<b>📊 Ringkasan:</b>\n"
        "/today — Pengeluaran hari ini\n"
        "/week — Pengeluaran minggu ini\n"
        "/month — Pengeluaran bulan ini\n"
        "/year — Pengeluaran tahun ini\n"
        "/q1 — Kuartal 1 (Jan-Mar)\n"
        "/q2 — Kuartal 2 (Apr-Jun)\n"
        "/q3 — Kuartal 3 (Jul-Sep)\n"
        "/q4 — Kuartal 4 (Okt-Des)\n\n"
        "<b>📄 Laporan:</b>\n"
        "/report — Download laporan PDF bulan ini\n\n"
        "<b>🛠 Lainnya:</b>\n"
        "/delete — Hapus entri terakhir\n"
        "/help — Tampilkan panduan ini\n\n"
        "━━━ <b>🏷 Kategori Otomatis</b> ━━━\n"
        "🍔 Makanan · ☕ Minuman · 🚗 Transportasi\n"
        "🛒 Belanja · 🏥 Kesehatan · 🎮 Hiburan\n"
        "💡 Utilitas · 📦 Lainnya"
    )
    bot.reply_to(message, text)


def _format_summary(expenses: list[dict], title: str) -> str:
    if not expenses:
        return f"📭 <b>{title}</b>\n\nBelum ada pengeluaran tercatat."

    total = sum(e["price"] for e in expenses)

    categories = {}
    for e in expenses:
        cat = e.get("category", "📦 Lainnya")
        categories[cat] = categories.get(cat, 0) + e["price"]

    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    lines = [
        f"📊 <b>{title}</b>\n",
        f"💳 Total: <b>{format_rupiah(total)}</b>",
        f"📝 Transaksi: <b>{len(expenses)}</b>\n",
        "─── Per Kategori ───",
    ]

    for cat_name, cat_total in sorted_cats:
        pct = (cat_total / total * 100) if total > 0 else 0
        lines.append(f"  {cat_name}: {format_rupiah(cat_total)} ({pct:.0f}%)")

    lines.append("\n─── Transaksi Terbaru ───")
    recent = expenses[-5:]
    for e in reversed(recent):
        desc = f" <i>({e['description']})</i>" if e.get("description") else ""
        try:
            ts = e["timestamp"].split(" ")[0]
        except (KeyError, IndexError):
            ts = ""
        lines.append(f"  • {format_rupiah(e['price'])} — {e['item']}{desc} [{ts}]")

    if len(expenses) > 5:
        lines.append(f"  <i>...dan {len(expenses) - 5} transaksi lainnya</i>")

    return "\n".join(lines)


@bot.message_handler(commands=["today"])
def cmd_today(message):
    bot.send_chat_action(message.chat.id, "typing")
    user_id = message.from_user.id
    expenses = sheets_helper.get_today_expenses(user_id)
    text = _format_summary(expenses, "Pengeluaran Hari Ini")
    bot.reply_to(message, text)


@bot.message_handler(commands=["week"])
def cmd_week(message):
    bot.send_chat_action(message.chat.id, "typing")
    user_id = message.from_user.id
    expenses = sheets_helper.get_week_expenses(user_id)
    text = _format_summary(expenses, "Pengeluaran Minggu Ini")
    bot.reply_to(message, text)


@bot.message_handler(commands=["month"])
def cmd_month(message):
    bot.send_chat_action(message.chat.id, "typing")
    user_id = message.from_user.id
    expenses = sheets_helper.get_month_expenses(user_id)
    text = _format_summary(expenses, "Pengeluaran Bulan Ini")
    bot.reply_to(message, text)


@bot.message_handler(commands=["year"])
def cmd_year(message):
    bot.send_chat_action(message.chat.id, "typing")
    user_id = message.from_user.id
    expenses = sheets_helper.get_year_expenses(user_id)
    text = _format_summary(expenses, "Pengeluaran Tahun Ini")
    bot.reply_to(message, text)


@bot.message_handler(commands=["q1", "q2", "q3", "q4"])
def cmd_quarter(message):
    bot.send_chat_action(message.chat.id, "typing")
    user_id = message.from_user.id
    quarter_num = int(message.text.strip("/qQ"))
    quarter_labels = {1: "Q1 (Jan-Mar)", 2: "Q2 (Apr-Jun)", 3: "Q3 (Jul-Sep)", 4: "Q4 (Okt-Des)"}
    expenses = sheets_helper.get_quarter_expenses(quarter_num, user_id)
    label = quarter_labels.get(quarter_num, f"Q{quarter_num}")
    text = _format_summary(expenses, f"Pengeluaran {label}")
    bot.reply_to(message, text)


@bot.message_handler(commands=["report"])
def cmd_report(message):
    bot.send_chat_action(message.chat.id, "typing")
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "User"
    expenses = sheets_helper.get_month_expenses(user_id)

    from datetime import datetime
    now = datetime.now()
    period = now.strftime("%B %Y")

    if not expenses:
        bot.reply_to(message, f"📭 Tidak ada data pengeluaran untuk <b>{period}</b>.")
        return

    bot.send_chat_action(message.chat.id, "upload_document")

    try:
        filepath = generate_report(expenses, f"Periode: {period} — {user_name}")
        total = sum(e["price"] for e in expenses)

        caption = (
            f"📄 <b>Laporan Pengeluaran — {period}</b>\n"
            f"👤 {user_name}\n"
            f"💳 Total: <b>{format_rupiah(total)}</b> ({len(expenses)} transaksi)"
        )

        with open(filepath, "rb") as f:
            bot.send_document(
                message.chat.id,
                f,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=message.message_id,
                visible_file_name=f"Laporan_{user_name}_{now.strftime('%Y_%m')}.pdf",
            )

        os.remove(filepath)

    except Exception as e:
        bot.reply_to(message, f"❌ Gagal membuat laporan: <code>{e}</code>")


@bot.message_handler(commands=["delete"])
def cmd_delete(message):
    bot.send_chat_action(message.chat.id, "typing")
    user_id = message.from_user.id

    deleted = sheets_helper.delete_last_entry(user_id)
    if deleted:
        text = (
            "🗑 <b>Entri terakhir dihapus:</b>\n\n"
            f"  📅 {deleted['timestamp']}\n"
            f"  💰 {format_rupiah(deleted['price'])}\n"
            f"  🏷 {deleted['item']}\n"
            f"  {deleted['category']}"
        )
    else:
        text = "📭 Tidak ada entri untuk dihapus."

    bot.reply_to(message, text)


@bot.message_handler(func=lambda msg: msg.text and not msg.text.startswith("/"))
def handle_expense(message):
    bot.send_chat_action(message.chat.id, "typing")

    parsed = parse_expense(message.text)

    if not parsed:
        bot.reply_to(
            message,
            "❌ <b>Format tidak dikenali.</b>\n\n"
            "Gunakan format:\n"
            "<code>[harga] [nama item] - [deskripsi]</code>\n\n"
            "Contoh: <code>25k naspad rendang - tambah telur</code>\n"
            "Ketik /help untuk panduan lengkap.",
        )
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "User"

    try:
        result = sheets_helper.add_expense(
            user_id=user_id,
            user_name=user_name,
            price=parsed["price"],
            item=parsed["item"],
            description=parsed["description"],
            category=parsed["category"],
        )

        desc_line = f"\n  📝 {parsed['description']}" if parsed["description"] else ""

        text = (
            "✅ <b>Pengeluaran tercatat!</b>\n\n"
            f"  👤 {user_name}\n"
            f"  💰 {format_rupiah(parsed['price'])}\n"
            f"  🏷 {parsed['item']}{desc_line}\n"
            f"  {parsed['category']}\n"
            f"  📅 {result['timestamp']}\n"
        )

        today_expenses = sheets_helper.get_today_expenses(user_id)
        today_total = sum(e["price"] for e in today_expenses)

        text += f"\n📊 Total hari ini: <b>{format_rupiah(today_total)}</b> ({len(today_expenses)} transaksi)"

        bot.reply_to(message, text)

    except Exception as e:
        bot.reply_to(message, f"❌ Gagal menyimpan: <code>{e}</code>")


if __name__ == "__main__":
    print("Bot berjalan dalam mode polling...")
    print("Tekan Ctrl+C untuk berhenti.\n")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
