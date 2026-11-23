"""
Telegram Faucet Bot - 0.05 ETH Sepolia per claim
Tugas: follow X @kapa3896, kirim bukti screenshot + username X + alamat wallet.
Verifikasi: manual (admin approve) karena API X berbayar / terbatas.
JANGAN taruh private key wallet utama di sini. Pakai wallet baru khusus faucet.
JANGAN kirim private key / token bot ke siapa pun, dan jangan commit file .env ke GitHub.
"""
import os, time, json
from web3 import Web3

# --- Config dari environment ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
FAUCET_PRIVATE_KEY = os.getenv("FAUCET_PRIVATE_KEY", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Telegram user id admin, untuk approve
RPC_URL = os.getenv("RPC_URL", "https://rpc.sepolia.org")
AMOUNT_ETH = 0.05
COOLDOWN_SECONDS = 24 * 60 * 60
X_ACCOUNT = "@kapa3896"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
faucet = w3.eth.account.from_key(FAUCET_PRIVATE_KEY) if FAUCET_PRIVATE_KEY else None

# Simpan sederhana: user_id -> {"last_claim": ts, "wallet": str, "x": str}
STATE_FILE = "claims.json"
state = {}
if os.path.exists(STATE_FILE):
    state = json.load(open(STATE_FILE))

def save():
    json.dump(state, open(STATE_FILE, "w"), indent=2)

def send_eth(to_address):
    """Kirim 0.05 ETH Sepolia, return tx hash atau None."""
    if not faucet:
        return None
    tx = {
        "to": Web3.to_checksum_address(to_address),
        "value": w3.to_wei(AMOUNT_ETH, "ether"),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(faucet.address),
        "chainId": 11155111,  # Sepolia
    }
    signed = w3.eth.account.sign_transaction(tx, FAUCET_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()

# --- Telegram bot (python-telegram-bot v20) ---
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Halo! Faucet 0.05 ETH Sepolia.\n"
        f"Tugas: follow X {X_ACCOUNT} dulu.\n\n"
        f"Cara claim:\n"
        f"1. Follow {X_ACCOUNT} di X\n"
        f"2. Kirim: /claim <alamat_wallet> <username_X>\n"
        f"   Contoh: /claim 0x1234... abcd\n"
        f"3. Kirim screenshot bukti follow di chat ini\n"
        f"4. Tunggu admin approve, lalu 0.05 ETH dikirim.\n"
        f"Cooldown: 24 jam per user."
    )

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if len(context.args) < 2:
        await update.message.reply_text("Pakai: /claim <alamat_wallet> <username_X>")
        return
    wallet, x_user = context.args[0], context.args[1]
    if not Web3.is_address(wallet):
        await update.message.reply_text("Alamat wallet tidak valid.")
        return
    now = time.time()
    last = state.get(uid, {}).get("last_claim", 0)
    if now - last < COOLDOWN_SECONDS:
        sisa = int((COOLDOWN_SECONDS - (now - last)) / 3600)
        await update.message.reply_text(f"Masih cooldown, coba lagi sekitar {sisa} jam lagi.")
        return
    state[uid] = {"last_claim": 0, "wallet": wallet, "x": x_user, "status": "menunggu_screenshot"}
    save()
    await update.message.reply_text(
        f"Dicatat.\nWallet: {wallet}\nX: {x_user}\n"
        f"Sekarang kirim screenshot bukti follow {X_ACCOUNT} di chat ini."
    )
    if ADMIN_ID:
        await context.bot.send_message(
            ADMIN_ID,
            f"Claim baru dari {update.effective_user.id}\nWallet: {wallet}\nX: {x_user}\n"
            f"Balas /approve {update.effective_user.id} setelah cek screenshot."
        )

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = context.args[0]
    data = state.get(uid)
    if not data:
        await update.message.reply_text("User itu belum claim.")
        return
    tx = send_eth(data["wallet"])
    if not tx:
        await update.message.reply_text("Gagal kirim: cek saldo faucet / private key / RPC.")
        return
    data["last_claim"] = time.time()
    data["status"] = "selesai"
    save()
    await update.message.reply_text(f"Terkirim! Tx: https://sepolia.etherscan.io/tx/{tx}")
    await context.bot.send_message(
        int(uid),
        f"Berhasil! 0.05 ETH Sepolia dikirim.\nTx: https://sepolia.etherscan.io/tx/{tx}"
    )

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Screenshot diterima, tunggu admin cek dulu ya.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.run_polling()

if __name__ == "__main__":
    main()
