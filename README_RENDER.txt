# WENBNB Cloud Bot (V1) â€” Render Deployment Guide

1. Go to https://render.com and login (or sign up with Google).
2. Dashboard â†’ New â†’ Web Service â†’ Upload Folder.
3. Select 'wenbnb_stage1_render' and upload it.
4. Build Command: pip install -r requirements.txt
5. Start Command: python wenbot.py
6. Add Environment Variables (copy from .env.template)
7. Click Deploy â†’ Wait for logs: INFO WENBNB Cloud Bot started.
8. Test on Telegram: /start, /help, /meme, /price
