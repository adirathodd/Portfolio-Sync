from resume_parser import ResumeParser

filepath = "/Users/adirathodd/Documents/GitHub/Portfolio-Sync/resumes/Resume-2.pdf"
engine = ResumeParser()
summary = engine.parse(filepath)

print(summary)