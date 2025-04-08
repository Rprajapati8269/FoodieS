from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# Llama API Config
LLAMA_API_URL = "https://api.together.xyz/v1/chat/completions"
LLAMA_API_KEY = "1bc02c0ec24b4b824bbb3fd674e5135a81eaf47a9d03ac222362524e76aa4d89"

headers = {
    "Authorization": f"Bearer {LLAMA_API_KEY}",
    "Content-Type": "application/json"
}

# Sample data with 20 restaurants
restaurant_data = [
    {"id": i+1, "name": f"Restaurant {i+1}", "cuisine": cuisine, "seats": 20 + (i % 5) * 10, "booked": 0}
    for i, cuisine in enumerate(
        ["Indian", "Italian", "Japanese", "Mexican", "Chinese", "French", "Thai", "American", "Korean", "Spanish",
         "Greek", "Turkish", "Vietnamese", "Brazilian", "German", "Ethiopian", "Russian", "Lebanese", "Moroccan", "British"]
    )
]

class ChatRequest(BaseModel):
    message: str

class BookRequest(BaseModel):
    restaurant_name: str
    tables: int

@app.get("/recommend/{cuisine}")
def recommend(cuisine: str):
    recs = [r for r in restaurant_data if r["cuisine"].lower() == cuisine.lower() and r["seats"] >= 4]
    if recs:
        best = sorted(recs, key=lambda x: -x["seats"])[0]
        return {"message": f"We recommend {best['name']} for {best['cuisine']} cuisine."}
    raise HTTPException(status_code=404, detail="No available restaurants.")

@app.post("/book")
def book(req: BookRequest):
    for r in restaurant_data:
        if r["name"].lower() == req.restaurant_name.lower():
            required_seats = req.tables * 4
            if r["seats"] >= required_seats:
                r["seats"] -= required_seats
                r["booked"] += req.tables
                return {"message": f"Booked {req.tables} table(s) at {r['name']}!"}
            else:
                raise HTTPException(status_code=400, detail="Not enough seats available.")
    raise HTTPException(status_code=404, detail="Restaurant not found.")

@app.get("/metrics")
def get_metrics():
    total_bookings = sum(r["booked"] for r in restaurant_data)
    return {"total_bookings": total_bookings, "total_restaurants": len(restaurant_data)}

@app.post("/chat")
def chat_ai(req: ChatRequest):
    user_question = req.message
    context = "\n".join([
        f"{r['name']} serves {r['cuisine']} and has {r['seats']} seats remaining." for r in restaurant_data
    ])

    system_prompt = (
        "You are a helpful restaurant reservation assistant. "
        "Use the provided data to recommend or book based on user's intent. "
        "Keep your replies short and relevant.\n\n"
        f"Restaurant data:\n{context}"
    )

    payload = {
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        "temperature": 0.5
    }

    try:
        res = requests.post(LLAMA_API_URL, headers=headers, json=payload)
        if res.ok:
            return {"ai_response": res.json()["choices"][0]["message"]["content"]}
        else:
            raise HTTPException(status_code=res.status_code, detail=res.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")
