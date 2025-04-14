from pdfminer.high_level import extract_text
from openai import AzureOpenAI
import json
from utils import *
from dotenv import load_dotenv
import os
import concurrent.futures

load_dotenv()

class ResumeParser:
    def __init__(self):
        endpoint = "https://synced-ai.openai.azure.com/"
        subscription_key = os.getenv("AZURE_OPENAI_KEY")
        api_version = "2024-12-01-preview"

        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=subscription_key,
        )
    
    def get_response(self, prompt):
        response = self.client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a highly intelligent assistant. Your response MUST be a single valid JSON string with no additional text, commentary, or formatting. Use the provided JSON template exactly as given.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0,
        model="gpt-4o"
    )
        res = str(response.choices[0].message.content).strip("`json")
        return res


    def parse(self, filepath):
        # Extract all text from the resume PDF
        try:
            resumeText = extract_text(filepath)
        except Exception as e:
            raise ValueError(f"Error extracting text from resume: {e}")

        max_retries = 5
        parsed_resume = {}

        # Process each section in parallel using ThreadPoolExecutor
        def process_section(section):
            retries = 0
            success = False
            while retries < max_retries and not success:
                try:
                    # 1. Extract the specified section text from the resume
                    extracted_text = self.get_response(split_resume_prompt(resumeText, section))

                    # 2. Parse the extracted section according to JSON template
                    response = self.get_response(parse_section_prompt(extracted_text, sections[section]))
                    result = json.loads(response)
                    success = True
                    return section, result
                except json.JSONDecodeError as e:
                    retries += 1
                    print(f"JSON parsing error for section {section}. Retrying {retries}/{max_retries}...")
                except Exception as e:
                    print(f"Unexpected error for section {section}: {e}")
                    retries += 1

            if not success:
                print(f"Failed to parse section - {section} - after {max_retries} retries. Setting it to an empty dictionary.")
                return section, {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_section = {executor.submit(process_section, section): section for section in sections}
            for future in concurrent.futures.as_completed(future_to_section):
                sec, result = future.result()
                parsed_resume[sec] = result
                print(f"Parsing {sec} completed!")

        return json.dumps(parsed_resume, indent=2)