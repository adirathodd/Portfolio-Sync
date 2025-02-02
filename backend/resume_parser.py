from pdfminer.high_level import extract_text
from langchain_ollama import OllamaLLM
import json
from utils import *
import multiprocessing

class ResumeParser:
    def __init__(self):
        self.llm = OllamaLLM(model="llama3")

    def parse(self, filepath):
        # Extract all text from the resume PDF
        try:
            resumeText = extract_text(filepath)
        except Exception as e:
            raise ValueError(f"Error extracting text from resume: {e}")

        max_retries = 3
        parsed_resume = {}

        # Parse each section seperately for improved accuracy
        for section in sections:
            retries = 0
            success = False

            # Given a maximum of 3 attempts
            while retries < max_retries and not success:
                try:
                    # 1. Extract the specified section text from the resume
                    extracted_text = self.llm.invoke(self.split_resume_prompt(resumeText, section))

                    # 2. Parse the extracted section according to JSON template
                    response = self.llm.invoke(self.parse_section_prompt(extracted_text, sections[section]))
                    parsed_resume[section] = json.loads(response)
                    success = True

                except json.JSONDecodeError as e:
                    retries += 1
                    print(f"JSON parsing error for section {section}. Retrying {retries}/{max_retries}...")
                except Exception as e:
                    print(f"Unexpected error for section {section}: {e}")
                    retries += 1

            if not success:
                print(f"Failed to parse section - {section} - after {max_retries} retries. Setting it to an empty dictionary.")
                parsed_resume[section] = {}

            print(f"Parsing {section} completed!")

        return parsed_resume

    def parse_section_prompt(self, resume_text, template):
        prompt = f'''
You are a highly intelligent assistant and are tasked to extract important information from a given text and fill in the given JSON template accordingly.

Your goals:
1. Carefully examine the entirety of the given text.
2. Extract all relevant information and fill in the JSON template accordingly.
3. For the 'description' field, summarize the experience or project. Don't just copy from the resume text.
4. Respond ONLY with valid JSON that matches the provided template. No additional text, summaries, or comments.

If any information is missing from the text, leave the corresponding fields blank.

Text -
{resume_text}

JSON Template -
{template}

Respond only with valid JSON, strictly following the format of the provided template.
'''

        return prompt

    def split_resume_prompt(self, resumeText, section):
        prompt = f'''
You are a highly intelligent assistant and are tasked to extract a specific section from an individual's resume.

You are given the following things -
    1. Resume text
    2. Section Name

These are your Goals -
    1. Carefully examine the entirety of the given resume text.
    2. Retrieve only the section from the resume text indicated from the given section name.

Resume Text -
{resumeText}

Section Name -
{section}

Respond only with the text from the resume with no additional text or summary.
        '''

        return prompt