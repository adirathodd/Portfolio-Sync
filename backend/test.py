from resume_parser import ResumeParser

filepath = "../resumes/Resume-1.pdf"
engine = ResumeParser()
summary = engine.parse(filepath)

print(summary)