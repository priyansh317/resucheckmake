# AI Resume–Job Matching System

## Problem Statement
Recruiters receive resumes and job descriptions in highly inconsistent formats.
Existing systems often fail when skills are misspelled, missing, or poorly structured.

## Solution
This project is a robust backend system that intelligently matches resumes with job descriptions,
even when inputs are noisy, incomplete, or inconsistent.

The system focuses on:
- Resume parsing
- Skill normalization
- Fuzzy matching
- Graceful error handling
-most appropriate scoring scheme.

## Key Features
- PDF resume upload
- Section-wise resume parsing
- Skill extraction and normalization
- Fuzzy matching for spelling errors
- Honest match scoring
- Edge-case handling for vague inputs

## Architecture Overview
1. Resume uploaded as PDF
2. Text extracted using PyPDF2
3. Resume divided into logical sections
4. Skills extracted and normalized
5. Job description skills extracted
6. Matching engine compares skills
7. Match score and insights returned

## API Endpoints

### POST /upload-resume
Uploads resume and extracts structured data.

### POST /match-job
Compares resume skills with job description skills and returns:
- Match score
- Matched skills
- Missing skills

## Edge Case Handling
- Resume without skills section
- Job description without clear skill requirements
- Misspelled skills (e.g. pythn → python)
- Empty or invalid inputs

## Tech Stack
- Python
- FastAPI
- Operating system (OS)
- List
- Basemodel
- PyPDF2
- Regex
- Difflib
- corsmiddleware

## Future Improvements
- NLP-based semantic matching
- Database integration
- Frontend UI
- Role-based scoring
- Give suggestions according to the requirements 

## Author
Priyansh Garg
