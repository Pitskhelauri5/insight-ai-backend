import json
import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI(title="Insight AI - Logistics & B2B SaaS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.get("/")
def root():
    return {"message": "Insight AI Backend is Live and Ready!"}

@app.post("/api/parse-document/")
async def parse_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="ფაილი ცარიელია ან ტექსტის წაკითხვა ვერ მოხერხდა.")

        prompt = f"""
        შენ ხარ B2B ლოგისტიკის AI ასისტენტი. გააანალიზე დოკუმენტი და დააბრუნე მკაცრად JSON ფორმატით შემდეგი ზუსტი ველებით:
        - document_type (სტრიქონი)
        - r_l_number (სტრიქონი, ბლ/ნომერი)
        - shipper (სტრიქონი, გამგზავნი კომპანია)
        - consignee (სტრიქონი, მიმღები კომპანია)
        - vessel_voyage (სტრიქონი, გემი/რეისი)
        - port_of_loading (სტრიქონი)
        - port_of_discharge (სტრიქონი)
        - total_freight_cost (სტრიქონი ან რიცხვი, მაგ: "$3,850.00 USD")
        - items (მასივი, სადაც თითოეულ ობიექტს აქვს: item_description, hs_code, qty_weight, decl_value)

        დოკუმენტის ტექსტი:
        {text_content}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content
        parsed_data = json.loads(raw_content)

        # ვუბრუნებთ პირდაპირ დაპარსულ ობიექტს ყოველგვარი დამატებითი შეფუთვის გარეშე
        return parsed_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
