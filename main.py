import csv
import asyncio
import aiohttp


OPENAI_API_TOKEN = "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"
CSV_FILE_NAME = "data.csv"


async def main() -> None:
    
    # read data
    csv_data = []
    with open(CSV_FILE_NAME, encoding="UTF-8") as f:
        csv_reader = csv.reader(f, delimiter=",")
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue
            
            csv_data.append({
                "email": row[0],
                "review": row[1],
                "date": row[2],
                "rating": "",
                "response": ""
            })
    
    
    # get openai responses
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_TOKEN}"
        }
        
        for i, review in enumerate(csv_data):
            model_max_length = 4_097
            prompt = f"""
                How positive is review from 1 to 10. Format answer as "rating/10, description". Rating should be integer
                
                {i + 1}. {review["email"]}
                {review["review"]}
            """
            body = {
                "model": "text-davinci-003",
                "prompt": prompt,
                "max_tokens": model_max_length - len(prompt)
            }
            
            res = await session.post("https://api.openai.com/v1/completions", headers=headers, json=body)
            print(res.raise_for_status())
            res = await res.json()
            
            res_text: str = res["choices"][0]["text"].replace("\n", "")
            review["rating"] = res_text[:res_text.find(",")]
            review["response"] = res_text
    
    
    # sort csv_data
    def sort_by_rating(review: dict) -> int:
        rating: str = review["rating"]
        return int(rating[:rating.find("/")])
    csv_data = sorted(csv_data, key=sort_by_rating, reverse=True)
    
    
    # write results
    dot_index = CSV_FILE_NAME.rfind(".")
    new_file_name = CSV_FILE_NAME[:dot_index] + "_analyzed" + CSV_FILE_NAME[dot_index:]
    with open(new_file_name, "w", newline="", encoding="UTF-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=["email", "review", "date", "rating", "response"])
        csv_writer.writeheader()
        csv_writer.writerows(csv_data)
    

if __name__ == "__main__":
    asyncio.run(main())
