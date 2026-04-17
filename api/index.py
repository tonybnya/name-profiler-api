"""
Script Name : api/index.py
Description : ASGI entry point for Vercel serverless deployment
Author : @tonybnya
"""

from asgiref.wsgi import WsgiToAsgi

from app import app

# Wrap Flask WSGI app with ASGI adapter for Vercel
asgi_app = WsgiToAsgi(app)
