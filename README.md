# Job API Aggregator 🚀

A production-grade Flask-based job aggregation system that fetches and normalizes jobs from multiple public job APIs into one unified stream.

## ✨ Features

- **Multi-API Integration**: Aggregates jobs from 6+ public job APIs
- **Unified Format**: Normalizes heterogeneous API responses into a standard format
- **Smart Deduplication**: Removes duplicate listings across different sources
- **Auto-Categorization**: Intelligently categorizes jobs (Software Engineering, Data Science, AI/ML, Internships)
- **Real-time Updates**: Fetches fresh jobs on every request
- **Production-Ready**: Clean, modular code with comprehensive error handling

## 🔌 Integrated APIs

1. **Remotive** - Remote tech jobs (No API key required)
2. **Adzuna** - Global job listings (Free API key)
3. **JSearch** - Multi-source aggregator via RapidAPI
4. **Careerjet** - Global job search engine
5. **The Muse** - Startup and tech-focused companies
6. **USAJobs** - US government positions

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd job-api-aggregator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Create a `.env` file for additional APIs:
```env
# Adzuna API
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

# JSearch via RapidAPI
RAPIDAPI_KEY=your_rapidapi_key

# Careerjet
CAREERJET_AFFID=your_affiliate_id

# The Muse
THEMUSE_API_KEY=your_api_key

# USAJobs (optional, uses default if not set)
USAJOBS_EMAIL=your_email@example.com
USAJOBS_API_KEY=your_api_key
```

4. Run the application:
```bash
python app.py
```

5. Open your browser to `http://127.0.0.1:5000`

## 📋 Standard Job Format

All jobs are normalized into this unified format:

```python
{
    "id": "unique_job_id",
    "title": "Job Title",
    "company": "Company Name",
    "location": "Location or Remote",
    "url": "Original job application link",
    "category": "Software Engineering | Data Science | AI/ML | Internship",
    "source": "API name",
    "published": "ISO date string"
}
```

## 🏗️ Architecture

- **Modular Design**: Each API has its own fetch function for easy maintenance
- **Error Handling**: Graceful failures - if one API fails, others continue working
- **Environment-Based Config**: API keys loaded from `.env` file (never hardcoded)
- **Type Safety**: Full type hints throughout the codebase

## 📁 Project Structure

```
job-api-aggregator/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Frontend template
├── static/
│   └── style.css       # Styling
└── .env                # API keys (create this file)
```

## 🔧 API Setup Guides

### Remotive
- **Status**: ✅ Works immediately (no setup needed)
- **Docs**: https://remotive.com/api-documentation

### Adzuna
- **Get API Key**: https://developer.adzuna.com/overview
- **Free tier**: Available

### JSearch (RapidAPI)
- **Get API Key**: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/
- **Free tier**: Available

### Careerjet
- **Get Affiliate ID**: https://www.careerjet.com/partners/api/
- **Free**: Yes

### The Muse
- **Get API Key**: https://www.themuse.com/developers/api/v2
- **Free tier**: Limited access

### USAJobs
- **Get API Key**: https://developer.usajobs.gov/
- **Free**: Yes (email required)

## 🎯 Usage

The application automatically:
1. Fetches jobs from all configured APIs
2. Normalizes them into a unified format
3. Removes duplicates (same title + company)
4. Categorizes jobs using keyword matching
5. Sorts by publication date (newest first)
6. Limits to 50 most recent jobs

## 🛠️ Technologies Used

- **Flask** - Web framework
- **Requests** - HTTP library for API calls
- **python-dotenv** - Environment variable management
- **Python 3.7+** - Programming language

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add more job APIs
- Improve categorization logic
- Enhance error handling
- Add new features

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for job seekers everywhere**


