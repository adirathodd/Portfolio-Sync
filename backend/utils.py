sections = {
    'personal_info': {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": ""
    },
    'education': [
        {
            "institute_name": "",
            "year_of_passing": "",
            "degree": "",
            "major": "",
            "minor": "",
            "score": ""
        }
    ],
    'experience': [
        {
            "organisation_name": "",
            "location": "",
            "start_date": "",  # MM/YYYY format
            "end_date": "",    # MM/YYYY format
            "position": "",
            "description": ""
        }
    ],
    'projects': [
        {
            "project_name": "",
            "description": ""
        }
    ]
}

def split_resume_prompt(resumeText, section):
    prompt = f'''
You are given the following things -
1. Resume text
2. Section Name

These are your Goals -
1. Carefully examine the entirety of the given resume text.
2. Retrieve only the section from the resume text indicated from the given section name.
3. IMPORTANT: Respond ONLY with a valid JSON string with no extra text, explanations, or markdown formatting (do not include any code fences or additional commentary).

Resume Text -
{resumeText}

Section Name -
{section}

Respond only with the text from the resume with no additional text or summary.
    '''

    return prompt

def parse_section_prompt(resume_text, template):
    prompt = f'''
Your goals:
1. Carefully examine the entirety of the provided text.
2. Extract all relevant information and fill in the JSON template exactly as provided.
3. For any field (like 'description'), summarize if needed, but do not copy large text verbatim.
4. For any date fields, provide a response in MM/DD/YYYY or MM/YYYY format
5. Make sure to use double quotes in your JSON response not and NOT single quotes.
6. IMPORTANT: Respond ONLY with a valid JSON string with no extra text, explanations, or markdown formatting (do not include any code fences or additional commentary).

If any information is missing, leave the respective fields blank.

Text:
{resume_text}

JSON Template:
{template}

Respond with only the valid JSON string.
'''

    return prompt