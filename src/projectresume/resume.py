import os
import time
from pathlib import Path
from pydantic import BaseModel,Field 
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
  raise ValueError("API key not found")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"

job_description="""
Software Development Engineer 6 months Internship – 2027 (In-Person)

Introduction
At Amazon, we hire the best minds in technology to innovate and build on behalf of our customers. The intense focus we have on our customers is why we are one of the world’s most beloved brands – customer obsession is part of our company DNA. Our interns write real software and collaborate with a select group of experienced software development engineers (SDEs) who guide interns on projects that matter to our customers. As an intern, you will be matched to a manager and a mentor. You will have the opportunity to influence the evolution of Amazon technology and lead mission critical projects early in your career. Your design, code, and raw smarts will contribute to solving some of the most complex technical challenges in the areas of distributed systems, data mining, automation, optimization, scalability, and security – just to name a few. In addition to working on an impactful project, you will have the opportunity to engage with Amazonians for both personal and professional development, expand your network, and participate in activities with other interns throughout your internship. No matter the location of your internship, we give you the tools to own your project and learn in a real-world setting. Many of our technologies overlap, and you would be hard pressed to find a team that is not using Amazon Web Services (AWS), touching the catalogue, or iterating services to better personalize for customers. If this opportunity interests you, apply and come chart your own path at Amazon.

Job location
By applying to this position your application will be considered for all locations we hire for in India. This includes but is not limited to Bengaluru, Chennai, Hyderabad, Delhi, Mumbai and Pune.

Duration and Timelines
Amazon internships are full-time (40 hours/week) for 24 - 26 consecutive weeks (six months) with start dates between January - June 2027

Please note that Amazon internships require full-time commitment during the duration of the internship. During the course of internship, interns should not have any conflicts including but not limited to academic projects, classes or other internships/employment. Any exam related details must be shared with the hiring manager to plan for absence during those days. Specific team norms around working hours will be communicated by the hiring/ reporting manager at the time of commencement of internship. Candidates receiving internship will be required to submit declaration of their availability to complete the entire duration of internship duly signed by a competent authority at their University. Internship offer will be subjected to successful submission of the declaration.

Key job responsibilities
• Collaborate with experienced cross-disciplinary Amazonians to conceive, design, and bring innovative products and services to market.
• Design and build innovative technologies in a large distributed computing environment, and help lead fundamental changes in the industry.
• Create solutions to run predictions on distributed systems with exposure to innovative
technologies at incredible scale and speed.
• Build distributed storage, index, and query systems that are scalable, fault-tolerant, low cost, and easy to manage/use.
• Ability to design and code the right solutions starting with broadly defined problems.
• Work in an agile environment to deliver high-quality software.

Basic Qualifications
- Knowledge of computer science fundamentals such as object-oriented design, operating systems, algorithms, data structures, and complexity analysis
- Knowledge of programming languages such as C/C++, Python, Java or Perl
- Currently enrolled in a Bachelor’s or Master’s Degree in Computer Science, Computer Engineering, or related field at time of application -Year of Graduation 2027

Preferred Qualifications
- Previous technical internship(s).
- Experience with distributed, multi-tiered systems, algorithms, and relational databases.
- Experience in optimization mathematics such as linear programming and nonlinear optimization.
- Effectively articulate technical challenges and solutions.
- Adept at handling ambiguous or undefined problems as well as ability to think abstractly.

Our inclusive culture empowers Amazonians to deliver the best results for our customers. If you have a disability and need a workplace accommodation or adjustment during the application and hiring process, including support for the interview or onboarding process, please visit https://amazon.jobs/content/en/how-we-hire/accommodations for more information. If the country/region you’re applying in isn’t listed, please contact your Recruiting Partner.
"""
class JobDes(BaseModel):
  role:str
  required_skills:list[str]
  preferred_skills:list[str]
  minimum_experience:float | None
  education_requirements:list[str]
  responsibilities:list[str]

job_Schema=JobDes.model_json_schema()

system_prompt=f"""
you are an expert Hr assistant

your job is to analyze job description and extract structured information from them.

Return ONLY valid matching this schema:{job_Schema}
Important:
Do not return the schema itself
Do not return fields like "properties","title" or "type"
Fill the schema with actual information extracted from the job description

If minimum experience is not mentioned,return null
If inforation for a list is missing,return empty list
Do not invent information
"""

user_prompt=f"""
Analzye the following job descripton :
{job_description}
"""

systemMessage={
  "role":"system",
  "content":system_prompt
}

message={
  "role":"user",
  "content":user_prompt
}

messages=[systemMessage,message]
response_format={
  "type":"json_object"
}
response=client.chat.completions.create(model=model,messages=messages)
answer=response.choices[0].message.content
raw_json=answer

import json
job_data=json.loads(raw_json)
job=JobDes(**job_data)

print(job.minimum_experience)
print(job.preferred_skills)

class Experience(BaseModel):
  role:str | None= None
  duration:str | None= None
  description:str | None= None
  skills_used:str | None= None

class Resume(BaseModel):
  name:str | None = None
  email:str | None = None
  phone:str | None = None
  total_exp_years:float | None= None
  skills:list[str] = []
  experience:list[Experience] =[]
  projects:list[str] = []
  certifications:list[str]=[]


resume_Schema=Resume.model_json_schema()

def parse_resume(resume_text):
  system_prompt=f"""
  you are an expert resume parser/

  Extract information from the resume based on its meaning,
  not only based on exact section headings

  Different resumes may use different headings.

  for example:
  - Experience
  - Proffesional Experience
  - Work History
  - Employment
  - Internships

  These may all contain relevant experience.
  Skills may also appear in the skills section,work-experience,internships or projects
  Return ONLY valid json matching this schema:
  {resume_Schema}
  Important rukes:
    1. Do not invent information
    2. if a value is not available,return null
    3. if a list has no information return an empty list
    4. Include internships inside experience
    5. Extract skills mentioned across te entire resume.
  """

  user_prompt=f"""
  parse the following resume :
  {resume_text}
  """
  message_system={
    "role":"system",
    "content":system_prompt
  }

  message={
    "role":"user",
    "content":user_prompt
  }

  response_format={
    "type":"json_object"
  }
  messages=[message_system,message]
  response=client.chat.completions.create(model=model,messages=messages)
  raw_output=response.choices[0].message.content
  data=json.loads(raw_output)
  resume=Resume(**data)
  return resume


from pypdf import PdfReader
from docx import Document
def read_pdf(filepath):
  reader=PdfReader(filepath)
  text=""
  for page in reader.pages:
    page_text=page.extract_text()
    if page_text:
      text+=page_text+"\n"
  return text

def read_docs(filepath):
  reader=Document(str(filepath))
  text=""
  for paragraph in reader.paragraphs:
    if paragraph.text.strip():
      text+=paragraph.text+"\n"

  for table in reader.tables:
    for row in table.rows:
      for cell in row.cells:      
        if cell.text.strip():
          text+=cell.text+"\n"
  return text

class MatchResult(BaseModel):
  score:float
  details:dict


def final_score(job, resume):

    match_schema = MatchResult.model_json_schema()

    system_prompt = f"""
    You are an expert HR recruiter.

    Compare the candidate resume with the job description.

    Evaluate:
    1. Required skills
    2. Preferred skills
    3. Relevant experience
    4. Projects
    5. Education

    Give a score between 0 and 100.

    Explain the score in details.

    Do not invent information.
    Do not evaluate protected personal characteristics.

    Return valid JSON matching this schema:
    {match_schema}
    """

    user_prompt = f"""
    JOB DESCRIPTION:
    {job.model_dump_json(indent=2)}

    RESUME:
    {resume.model_dump_json(indent=2)}
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    raw_output = response.choices[0].message.content

    data = json.loads(raw_output)

    result = MatchResult(**data)

    return result


def read(filepath):
  if filepath.suffix.lower()==".pdf":
    return read_pdf(filepath)
  elif filepath.suffix.lower()==".docx":
    return read_docs(filepath)
  else:
    return None

BASE_DIR = Path(__file__).resolve().parent
resume_folder=resume_folder = BASE_DIR / "resumes"
all_resumes=[]
for filepath in resume_folder.iterdir():
  if filepath.suffix.lower() not in [".pdf",".docx"]:
    continue
  print(f"\n processing {filepath.name}")
  resume_text=read(filepath)
  parsed_resume=parse_resume(resume_text)
  time.sleep(5)
  result=final_score(job,parsed_resume)
  time.sleep(5)
  print( f"/n Score :{result.score}")
  all_resumes.append({
    "name":parsed_resume.name,
    "score":result.score,
    "details":result.details
  })

all_resumes.sort(
  key=lambda candidate:candidate["score"],
  reverse=True 
)

top_2=all_resumes[:2]
worst_2=all_resumes[-2:]

print("TOP 2 Candidate")
for candidate in top_2:
  print(
    candidate["name"],
    "-",
    candidate["score"],
    "%"
  )
  print(candidate["details"])


