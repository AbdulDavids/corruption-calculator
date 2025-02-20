import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI

app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Set up the OpenAI client using your API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Root endpoint serving the HTML template
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r") as file:
        return HTMLResponse(content=file.read())

# Endpoint to generate AI-driven corruption breakdown text
@app.get("/ai_corruption_breakdown")
def ai_corruption_breakdown(salary: float):
    if salary <= 0:
        raise HTTPException(status_code=400, detail="Salary must be a positive number.")

    corruption_percentage = 6.1  # Estimated % of tax revenue lost to corruption (based on SAICA's R1.5T report)

    system_prompt = """
You are an AI assistant analyzing South African tax and corruption impact on salaries.
Use real South African tax brackets and provide a sarcastic, honest breakdown.

Tax Brackets (2025):
- Up to R226,000/year: 18%
- R226,001 – R353,100: 26%
- R353,101 – R488,700: 31%
- R488,701 – R641,400: 36%
- R641,401 – R817,600: 39%
- R817,601 – R1,731,600: 41%
- Over R1,731,600: 45%

Calculate total tax, estimate 15% corruption loss from tax paid, and show take-home pay.
Format response in markdown with bold text for key numbers. End with a snarky comment. Try and slot an ANC joke, a Maserati reference, or a "load shedding" pun in there.
"""

    user_prompt = f"Calculate tax and corruption breakdown for my R{salary:,.2f} monthly salary. Keep it snarky and use markdown formatting."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
            temperature=0.5,
        )
        result_text = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"salary": salary, "ai_breakdown": result_text})

# Run the FastAPI application with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)