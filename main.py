@app.post("/api/parse-document/")
async def parse_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")

        if not text_content.strip():
            raise HTTPException(
                status_code=400, detail="ფაილი ცარიელია ან ტექსტის წაკითხვა ვერ მოხერხდა."
            )

        # ზუსტი ველები, რასაც ფრონტენდის დიზაინი ელის
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

        # პირდაპირ ვაბრუნებთ დაპარსულ ობიექტს, რომ ფრონტენდმა უპრობლემოდ წაიკითხოს
        return parsed_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
