from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-4826181726227802-051908-62f8e07c3ea1ad8d35b321f10ad4b201-3411676791"
MERCADO_PAGO_API_URL = "https://api.mercadopago.com/v1"

class CheckoutRequest(BaseModel):
    title: str
    price: float
    quantity: int
    description: str

@app.get("/")
async def root():
    return {"status": "LocaSeguro Backend Online ✅"}

@app.post("/checkout/preferences")
async def create_checkout_preference(request: CheckoutRequest):
    try:
        body = {
            "items": [{
                "title": request.title,
                "description": request.description,
                "quantity": request.quantity,
                "unit_price": request.price,
                "currency_id": "BRL",
            }],
            "payer": {
                "name": "Usuário LocaSeguro",
                "email": "usuario@locaseguro.com.br",
                "phone": {"area_code": "11", "number": "99999999"},
            },
            "back_urls": {
                "success": "https://www.locaseguro.com.br/success",
                "failure": "https://www.locaseguro.com.br/failure",
                "pending": "https://www.locaseguro.com.br/pending",
            },
            "auto_return": "approved",
            "external_reference": f"LOCA-{int(__import__('time').time())}",
        }

        headers = {
            "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MERCADO_PAGO_API_URL}/checkout/preferences",
                json=body,
                headers=headers,
                timeout=10.0,
            )

        if response.status_code == 201:
            data = response.json()
            return {
                "success": True,
                "preferenceId": data.get("id"),
                "initPoint": data.get("init_point"),
                "link": data.get("init_point"),
            }
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout ao conectar com Mercado Pago")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analisar")
async def analisar(body: dict):
    return {"veredicto": "SEGURO", "explicacao": "Analisado!", "dicas": ["Desconfie!"]}

@app.post("/assinar")
async def assinar(body: dict):
    return {"success": True, "link": "https://www.mercadopago.com.br"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "locaseguro-backend"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)