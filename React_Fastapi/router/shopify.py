import httpx
from fastapi import APIRouter, Request, HTTPException
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

# Credentials from your Partner Dashboard
CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")


@router.get("/api/auth/callback")
async def auth_callback(shop: str, code: str, state: str = None):
    """
    Shopify redirects here after the user clicks 'Install'.
    URL will look like: /auth/callback?code=xxx&shop=xxx.myshopify.com
    """

    # 1. Exchange the temporary code for a permanent access token
    auth_url = f"https://{shop}/admin/oauth/access_token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(auth_url, data=data)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to get token: {response.text}")

    result = response.json()
    access_token = result.get("access_token")

    # 2. SAVE THIS TOKEN SECURELY
    # In a real app, save 'access_token' to a database associated with 'shop'
    print(f"Permanent Token for {shop}: {access_token}")

    return {"message": "App installed successfully!", "token": access_token}



SHOP = "p1zp6f-8k.myshopify.com"
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")


@router.get("/api/draft-orders")
async def get_draft_orders():

    url = f"https://{SHOP}/admin/api/2026-01/draft_orders.json"

    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=response.text)

    return response.json()