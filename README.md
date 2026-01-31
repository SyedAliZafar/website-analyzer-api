Website Analyzer API

A production-ready FastAPI backend for automated website analysis, combining performance metrics, SEO evaluation, content quality analysis, and AI-powered insights.

✨ Features

🚀 Performance Analysis

Google PageSpeed Insights (with graceful fallback)

Mobile & desktop support

🔍 SEO Analysis

Title & meta evaluation

Heading structure

Canonical & Open Graph tags

Image alt-tag coverage

Structured data detection

📝 Content Analysis

Word & paragraph counts

Flesch Reading Ease readability score

Keyword density

Internal / external link analysis

Content gap detection

🤖 AI Insights

Executive summary

Strengths & weaknesses

Quick wins & strategic recommendations

Graceful fallback when AI keys are missing

⚙️ Clean Architecture

Pydantic Settings

Stateless utility functions

Isolated external services

Async-first design


🧱 Project Structure

app/
├── core/
│   ├── config.py
│   └── logging.py
├── models/
│   └── schemas.py
├── services/
│   ├── pagespeed.py
│   └── gemini.py
├── utils/
│   ├── seo.py
│   └── content.py
├── api/
│   └── routes.py
└── main.py
