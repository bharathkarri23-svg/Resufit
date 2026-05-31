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
            model="openai/gpt-oss-120b",
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

        return "Upload another resume, the current one is not parsable by the AI or does not contain enough information."


def analyze_job_fit(resume_text, job_description):

    prompt = f"""
You are an advanced ATS Resume Analyzer.

Compare this resume with the job description.

Resume:
{resume_text}

Job Description:
{job_description}

Rules:
1. Compare the resume strictly with the provided job description.
2. Extract only the information present in the resume and job description.
3. Do NOT guess skills, experience, certifications, or technologies.
4. Identify matching skills between the resume and the job description.
5. Identify missing skills that are required in the job description but not found in the resume.
6. Calculate an overall Job Fit Score based on skills, projects, experience, certifications, and relevance to the role.
7. If the resume strongly matches the job description with minimal missing skills, increase the score.
8. If important required skills are missing, reduce the score accordingly.
9. Analyze the candidate’s projects and compare the technologies used with the technologies required for the role.
10. Suggest relevant technologies, tools, or frameworks that can improve the candidate’s fit for the job.
11. Detect certifications relevant to the job role from the resume.
12. Suggest certifications that can improve the candidate’s profile for the target role.
13. Give actionable suggestions to improve the Job Fit Score above 90%.
14. Check whether the resume includes role-relevant keywords for ATS optimization.
15. If ATS keywords are missing, mention them in missing skills or suggestions.
16. Detect whether the candidate’s experience level matches the job requirements.
17. Evaluate the relevance of projects to the target job role.
18. Return ONLY valid JSON.
19. Do NOT return markdown.
20. Keep suggestions concise and practical.

Return JSON in this exact format:

{{
    "score": "85%",
    "skill": ["Python", "Flask", "SQL"],
    "missing_skills": ["Docker", "AWS"],
    "Certifications_Suggestions": [
        {{
            "name": "AWS Cloud Practitioner",
            "reason": "Helps demonstrate cloud fundamentals and improves eligibility for modern backend and deployment-focused roles."
        }},
        {{
            "name": "Docker Essentials",
            "reason": "Shows containerization skills which are highly required for DevOps and scalable application deployment."
        }}
    ],
    "Suggestions": [
        "Add cloud projects",
        "Mention deployment experience",
        "Improve ATS keywords"
    ]
}}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a strict ATS resume analyzer that only returns valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        result = response.choices[0].message.content.strip()

        print("RAW GROQ RESPONSE:")
        print(result)

        # Remove markdown if model adds it
        result = result.replace("```json", "").replace("```", "").strip()

        # Extract JSON safely
        match = re.search(r"\{.*\}", result, re.DOTALL)

        if not match:
            return {
                "score": "0%",
                "skill": [],
                "missing_skills": [],
                "Certifications_Suggestions": [],
                "Suggestions": [],
                "error": "No valid JSON returned"
            }

        json_text = match.group()

        data = json.loads(json_text)

        return data

    except Exception as e:

        print("JOB FIT ERROR:", str(e))

        return {
            "score": "0%",
            "skill": [],
            "missing_skills": [],
            "Certifications_Suggestions": [],
            "Suggestions": [],
            "error": str(e)
        }


def optimize_text(text, context_type="experience"):
    prompt = f"""
You are an expert professional resume writer and ATS optimization specialist.
Enhance and rewrite the following {context_type} text to make it sound highly professional, results-oriented, and ATS-friendly.

Guidelines:
1. Start with strong action verbs (e.g., Developed, Orchestrated, Optimized, Spearheaded).
2. Incorporate standard industry terms and keywords.
3. Quantify achievements where possible (e.g., emphasize numbers, metrics, or percent improvements).
4. Keep it concise, readable, and perfectly formatted as bullet points if it's experience/projects.
5. Do NOT invent fake companies, names, or dates. Only polish the phrasing and impact.

Original Text:
{text}

Output ONLY the enhanced text. Do not add intro, explanations, or quotes.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional resume optimizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OPTIMIZE ERROR:", str(e))
        return text


def tailor_resume(resume_data, job_description):
    prompt = f"""
You are an expert ATS Resume Tailoring AI.
Your job is to rewrite parts of the candidate's resume data to optimize and tailor it for a specific job description.

Target Job Description:
{job_description}

Original Resume Data (JSON format):
{json.dumps(resume_data, indent=2)}

Rules for Tailoring:
1. **Executive Summary**: Rewrite the summary to align directly with the key qualifications and requirements of the target job description. Focus on matching the tone and objectives.
2. **Work Experience Bullet Points**: For each experience entry, rewrite its `description` (retaining the bullet points structure if present) to highlight achievements, metrics, technologies, and duties that are highly relevant to the target job description. Do NOT invent new achievements, companies, dates, or titles. Only rewrite the phrasing to emphasize matching skills.
3. **Projects**: For each project, rewrite its `description` to emphasize technical achievements or results matching the job description's tech stack and objectives.
4. **Skills**: Look at the skill lists. Re-order or append relevant keywords/skills from the target job description to match their respective categories. Do not add skills that the candidate has absolutely no background in, but do optimize and list the matching ones.
5. **No Hallucinations**: Do not invent fake companies, school names, dates, GPA, titles, or links. Keep all dates, links, names, and titles exactly as they are.

IMPORTANT:
Return ONLY a valid JSON object matching the input structure exactly. Do not include markdown code block formats (e.g., no ```json), no intro text, and no explanation.

JSON output structure:
{json.dumps(resume_data, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a strict ATS resume tailoring assistant that only outputs valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        
        result = response.choices[0].message.content.strip()
        print("RAW TAILOR RESPONSE:", result)

        # Extract JSON safely
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            json_text = match.group()
            return json.loads(json_text)
        else:
            # Try to parse raw response directly if regex fails
            return json.loads(result)
            
    except Exception as e:
        print("TAILOR ERROR:", str(e))
        return resume_data


def analyze_keywords(resume_data, job_description):
    prompt = f"""
You are an advanced ATS Keyword Analyzer.
Compare the candidate's resume data JSON with the target job description.
Extract the core technical skills, programming languages, databases, tools, frameworks, and methodologies required in the job description.
Classify each keyword into:
1. "matched": Present in the candidate's resume data.
2. "missing": Required in the job description but not found in the candidate's resume.

Resume Data:
{json.dumps(resume_data, indent=2)}

Job Description:
{job_description}

Rules:
1. Be strict but reasonable (e.g. if "React.js" is in JD and "React" is in resume, classify as matched).
2. Extract only real tools, technologies, and technical skills (no generic soft skills like "communication").
3. Limit the lists to a maximum of 10 matched and 10 missing key terms.
4. Return ONLY valid JSON. Do NOT return markdown or explanation.

JSON format:
{{
  "matched": ["Python", "Flask", "PostgreSQL"],
  "missing": ["Docker", "Kubernetes", "AWS"]
}}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a strict ATS keyword analyzer that only outputs valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        result = response.choices[0].message.content.strip()
        print("RAW KEYWORD ANALYSIS RESPONSE:", result)

        # Extract JSON safely
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            json_text = match.group()
            return json.loads(json_text)
        else:
            return json.loads(result)
            
    except Exception as e:
        print("KEYWORD ANALYSIS ERROR:", str(e))
        return {"matched": [], "missing": [], "error": str(e)}