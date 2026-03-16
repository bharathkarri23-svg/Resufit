import os
import json
import re
from groq import Groq

client = Groq(api_key=os.getenv("groq_api_key"))


def analyze_resume(text):

    prompt = f"""
You are an advanced ATS Resume Analyzer.

Analyze the resume deeply.

Rules:
1. Detect job title from the resume header.
2. If job title is missing, evaluate overall resume strength.
3. Do NOT guess information.
4. Extract only information present in the resume.
5. Detect the summary of the candidate based on the resume content.
6. Add Suggestions on to improve the scores to above 90%.
7. If there are no missings fields increase the score.
8. for links LinkedIn, GitHub, Portfolio, check strictly for www.linkedin.com, github.com, and portfolio keywords in the resume otherwise give missing information for those fields. Do NOT guess or infer links.
9. Give suggesstions on skills that can be added.
10. Analyze the technologies used in the projects and suggest any missing technologies that are relevant to the job title.

IMPORTANT:
Return ONLY valid JSON.
Do not include explanations.
Do not include markdown.

JSON format:

{{
 "Candidate_Information": {{
  "Name": "",
  "job_title": "",
  "Email": "",
  "Phone": "",
  "Location": "",
  "LinkedIn": "",
  "GitHub": "",
  "Portfolio": ""
 }},

 "Skills": [],

 "education":[
  {{
   "degree":"",
   "university":"",
   "year":""
  }}
 ],

 "Experience":[
  {{
   "Job_Title":"",
   "Company":"",
   "Duration":""
  }}
 ],

 "Projects":[
  {{
   "name":"",
   "description":"",
   "technologies":[]
  }}
 ],

 "Certifications": [
 {{
    "name":""
 }}
 ],

 "Missing_Information": [],

 "Resume_Strengths": [],

 "Resume_Weaknesses": [],

 "Suggestions": [],

 "summary":"",
}}

Resume:
{text}
"""
    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an ATS resume analyzer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            top_p=1
        )

        result = response.choices[0].message.content

        print("RAW GROQ RESPONSE:", result)

        # Extract JSON safely
        match = re.search(r"\{.*\}", result, re.DOTALL)

        if match:

            json_text = match.group()
            data = json.loads(json_text)
            return data

        return {"error": "AI did not return valid JSON"}

    except Exception as e:

        return {"error": str(e)}