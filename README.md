# Telegram Faucet Bot — 0,05 ETH Sepolia

Tugas claim: follow X **@kapa3896**
Hadiah: **0,05 ETH Sepolia** per claim, cooldown 24 jam per user.

## Cara kerja
1. User `/start`, lalu `/claim <alamat_wallet> <username_X>`
2. User kirim screenshot bukti follow @kapa3896
3. Admin cek screenshot, lalu `/approve <user_id>` di bot
4. Bot kirim 0,05 ETH Sepolia, kasih link Etherscan Sepolia

Verifikasi follow X otomatis tidak dipakai, karena API X berbayar / terbatas. Jadi pakai bukti screenshot + approve admin.

## Yang harus disiapkan
- Bot Telegram dari @BotFather → `BOT_TOKEN`
- Wallet baru khusus faucet di Sepolia, isi ETH testnet → `FAUCET_PRIVATE_KEY`
  - Jangan pakai wallet utama. Jangan kirim private key ke siapa pun.
- Telegram user id admin → `ADMIN_ID`
- RPC Sepolia, contoh: `https://rpc.sepolia.org`

## Jalankan
```
pip install python-telegram-bot web3
BOT_TOKEN=... FAUCET_PRIVATE_KEY=... ADMIN_ID=... python bot.py
```

## Hosting
Bot harus jalan terus, dari HP saja tidak bisa 24 jam.
Pilihan gratis / murah: Render, Railway, atau VPS kecil. Upload `bot.py` + isi environment di sana, jangan commit `.env`.

## Cek saldo faucet
Saldo harus cukup: 0,05 ETH × jumlah claim. Kalau habis, bot gagal kirim.
