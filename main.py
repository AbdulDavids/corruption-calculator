import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI  # New SDK interface

app = FastAPI()

# Set up the OpenAI client using your API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Root endpoint serving a basic HTML page with JavaScript and markdown formatting
@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <!DOCTYPE html>
<html>
  <head>
    <title>AI Corruption Breakdown</title>
    <!-- Load Marked.js from CDN to render markdown -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 2rem;
      }
      #result {
        margin-top: 1.5rem;
        background: #f9f9f9;
        padding: 1rem;
        border-radius: 5px;
      }
    </style>
  </head>
  <body>
    <h1>AI Corruption Breakdown</h1>
    <form id="salaryForm">
      <label for="salary">Enter your monthly salary (in R):</label>
      <input type="number" id="salary" name="salary" step="any" required>
      <button type="submit">Submit</button>
    </form>
    <div id="result"></div>
    <script>
      document.getElementById("salaryForm").addEventListener("submit", async function(e) {
        e.preventDefault();
        const salary = document.getElementById("salary").value;
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = "<p>Loading...</p>";
        try {
          const response = await fetch(`/ai_corruption_breakdown?salary=${salary}`);
          if (response.ok) {
            const data = await response.json();
            // Use marked.parse() to convert markdown to HTML
            const html = marked.parse(data.ai_breakdown);
            resultDiv.innerHTML = `<div>${html}</div>`;
          } else {
            const errorData = await response.json();
            resultDiv.innerHTML = `<p>Error: ${errorData.detail}</p>`;
          }
        } catch (error) {
          resultDiv.innerHTML = `<p>Error: ${error}</p>`;
        }
      });
    </script>
  </body>
</html>
    """
    return HTMLResponse(content=html_content)

# Endpoint to generate AI-driven corruption breakdown text
@app.get("/ai_corruption_breakdown")
def ai_corruption_breakdown(salary: float):
    if salary <= 0:
        raise HTTPException(status_code=400, detail="Salary must be a positive number.")

    corruption_percentage = 6.1  # Estimated % of tax revenue lost to corruption (based on SAICA's R1.5T report)

    system_prompt = """
You are an AI assistant specializing in South African economics, taxation, and corruption analysis. 
Your goal is to take a user's salary and break down **exactly** how much of it is lost to **taxes** and **corruption**.
Use **real** South African tax brackets and research-backed corruption data. Keep the response **brutally honest**, 
**sarcastic**, and **humorous**, but ensure all numbers are accurate.

### **Rules for Response:**
1️⃣ **Step 1:** Calculate **total income tax** based on official South African tax brackets.  
2️⃣ **Step 2:** Estimate **corruption loss** using a **fixed 15** of total tax paid.  
3️⃣ **Step 3:** Provide **a clear take-home pay** after tax and corruption deductions.  
4️⃣ **Step 4:** End with a **snarky remark** about where the lost money might be going.  
5️⃣ **Format the response using markdown**, with **headings, bullet points, and bold text** for clarity.  

### **South African Tax Brackets (2025):**
- **Up to R226,000/year** → 18%
- **R226,001 – R353,100** → 26%
- **R353,101 – R488,700** → 31%
- **R488,701 – R641,400** → 36%
- **R641,401 – R817,600** → 39%
- **R817,601 – R1,731,600** → 41%
- **Over R1,731,600** → 45%

### **Corruption Loss Estimate:**
- **15% of all tax revenue is lost to corruption** (based on SAICA: R1.5T over 5 years).
- Apply **15% of total tax paid** as the corruption loss.

🚀 **Respond with only the markdown-formatted breakdown.**
"""

    user_prompt = f"""
Yo! So, I'm pulling in **R{salary:,.2f}** per month.  
Break it down for me: **after taxes, how much of my hard-earned cash is getting swiped by corruption?**  
Keep it **real, snarky, and formatted in markdown**.  
I want **exact numbers** and **clear calculations**. No fluff.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        result_text = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"salary": salary, "ai_breakdown": result_text})

# Run the FastAPI application with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)