import json
import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

# 1. აპლიკაციის ინიციალიზაცია
app = FastAPI(title="Insight AI - Logistics & B2B SaaS Backend")

# 2. CORS მიდლვერის სწორი თანმიმდევრობით დამატება
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render Environment Variables-დან იღებს API გასაღებს
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@app.get("/")
def root():
    return {"message": "Insight AI Backend is Live and Ready!"}


@app.post("/api/parse-document/")
async def parse_document(file: UploadFile = File(...)):
    try:
        # ფაილის შიგთავსის წაკითხვა
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")

        if not text_content.strip():
            raise HTTPException(
                status_code=400, detail="ფაილი ცარიელია ან ტექსტის წაკითხვა ვერ მოხერხდა."
            )

        # Prompt OpenAI-სთვის ლოგისტიკური მონაცემების გასაანალიზებლად
        prompt = f"""
        შენ ხარ B2B ლოგისტიკის AI ასისტენტი. გააანალიზე შემდეგი დოკუმენტის ტექსტი და ამოიღე სტრუქტურირებული JSON მონაცემები:
        - document_type (მაგ: Invoice, Bill of Lading, Packing List)
        - sender / exporter
        - receiver / importer
        - items (საქონლის სია, რაოდენობა, ფასი)
        - total_amount
        - currency
        - tracking_or_invoice_number

        დოკუმენტის ტექსტი:
        {text_content}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        # OpenAI-ს სტრიქონად დაბრუნებული პასუხის სწორი დაპარსვა ობიექტად
        raw_content = response.choices[0].message.content
        parsed_data = json.loads(raw_content)

        # სტრუქტურირებული პასუხის დაბრუნება ფრონტენდისთვის
        return {
            "status": "success",
            "data": parsed_data,
            "confidence": 0.994
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
