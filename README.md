# Lulu-Teaches-MVP

## Overview

**Lulu-Teaches-MVP** is an AI-powered virtual assistant designed for educational and mental health applications, leveraging state-of-the-art technologies such as Django, Docker, and Google Cloud Platform. The project is structured for scalability, ease of development, and rapid deployment. Core features include chat with generative AI, real-time sentiment analysis, Speech-to-Text integration, and a robust session management system.

---

## Key Features

* **Conversational AI:** Interactive chat assistant powered by advanced language models.
* **Sentiment Analysis:** Real-time detection of emotions and sentiments in conversations.
* **Speech-to-Text:** Seamless integration with Google Cloud Speech-to-Text API.
* **Admin Dashboard:** Full-featured session and user management via Django Admin.
* **Multi-environment Support:** Separate settings and scripts for development, testing, and production.
* **Containerized Deployment:** Ready-to-use Docker setup and continuous deployment on Google Cloud Run.

---

## Project Structure

```
happy-kids/
├── api/ 
├── fine_tuning/
├── frontend/
├── lulu_teaches/           # Main Django application for the assistant
├── static/                 # Static files (CSS, JS, Images)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image specification
├── compose.yml             # Local Docker orchestration
└── ...                     # Other project files
README.md                   # This file
```

---

## Getting Started

### 1. Set up the Virtual Environment

If this is your first time with the project, create a virtual environment:

```bash
python -m venv .venv
```

### 2. Activate the Virtual Environment

Depending on your terminal, run:

* **PowerShell:**

  ```bash
  .venv/Scripts/Activate
  ```
* **Command Prompt (CMD):**

  ```bash
  .venv\Scripts\activate.bat
  ```

### 3. Install Dependencies

Navigate to the project folder and install requirements:

```bash
cd happy-kids
pip install -r requirements.txt
```

---

## Database

### Local Migrations (Docker)

Run and apply migrations locally:

```bash
python manage.py makemigrations
python manage.py migrate
docker compose up --build
docker compose exec django-web python manage.py makemigrations
docker compose exec django-web python manage.py migrate
```

### Production Migrations (Google Cloud SQL)

After local testing, migrate to Cloud SQL:

1. Update the `settings.py` file with your production database credentials:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': '####',
           'USER': '####',
           'PASSWORD': '####',
           'HOST': 'localhost',
           'PORT': '5050',
       }
   }
   ```

2. Start the Cloud SQL Proxy:

   ```bash
   ./cloud-sql-proxy --credentials-file="full_path/lulu-mvp-service-account-key.json" --port 5050 lulu-mvp:europe-west3:db-lulu
   ```

3. Apply migrations:

   ```bash
   python manage.py migrate
   ```

---

## Deployment

### Local Testing with Docker

```bash
docker-compose up --build
```

### Deploy to Google Cloud Platform

After successful local tests, build and push the Docker image:

```bash
docker build -t gcr.io/lulu-mvp/lulu-teaches .
docker push gcr.io/lulu-mvp/lulu-teaches
```

#### Deploy on Google Cloud Run

* **With Redis:**

  ```bash
  gcloud run deploy lulu-teaches --image gcr.io/lulu-mvp/lulu-teaches --platform managed --region europe-west3 --vpc-connector lulu-vcp-network-serverle
  ```

* **Without Redis:**

  ```bash
  gcloud run deploy lulu-teaches --image gcr.io/lulu-mvp/lulu-teaches --platform managed --region europe-west3
  ```

---

## Technical Details & Best Practices

* **Environment Variables:**
  Use `.env` files or GCP Secret Manager for managing API keys and secrets securely.

* **Speech-to-Text Integration:**
  The project is ready for Google Cloud Speech-to-Text. Ensure proper credentials and endpoint configuration for the speech-to-text API.

* **Session Management:**
  User chat sessions are stored in the database and can be accessed and managed via the admin interface or API.

* **Extensibility:**
  Add new features such as analytics dashboards, custom model endpoints, or integrations (e.g., Power BI, external APIs) by extending the `lulu_teaches` Django app.

* **Continuous Integration:**
  Recommended to use GitHub Actions, GitLab CI/CD, or Google Cloud Build for automated testing and deployment.

* **Backups:**
  Consider adding database backup and restore scripts under the `/scripts` folder.

* **Security:**
  Never commit credentials or sensitive data to version control. Use IAM roles and least-privilege access for cloud resources.

---

## Roadmap

**Q1 2025**

* [x] Core chat and session management MVP
* [x] Dockerized local and production deployment
* [x] Speech-to-Text integration (OpenAi whisper-1 model)
* [x] Sentiment analysis integration
* [x] Fine-tuned LLMs for education & mental health
* [x] Multi-language support

**Q2 2025**

* [ ] Voice response (Text-to-Speech) support
* [ ] User analytics dashboard (Plotly/Dash)
* [ ] Mobile app (React Native or Flutter)

**Q3 2025**

* [ ] Real-time collaboration features
* [ ] Plugin system for custom modules
* [ ] Advanced reporting and exporting (PDF, XLSX)

**Future Ideas**

* [ ] API for third-party integration
* [ ] AI-powered recommendation engine
* [ ] Offline mode support

---

## References

* [Large Language Models in Context Learning (MIT)](https://news.mit.edu/2023/large-language-models-in-context-learning-0207)
* [How Generative AI is Changing Creative Work (HBR)](https://hbr.org/2022/11/how-generative-ai-is-changing-creative-work)
* [Google Cloud Artifact Registry Docs](https://cloud.google.com/artifact-registry/docs?hl=pt-br)
* [Google Cloud Build Docs](https://cloud.google.com/build/docs?hl=pt-br)
* Chan, W. et al., "SpeechStew: Simply mix all available speech recognition data to train one large neural network", arXiv:2104.02133, 2021.
* Galvez, D. et al., "The people’s speech: A large-scale diverse english speech recognition dataset for commercial usage", arXiv:2111.09344, 2021.
* Chen, G. et al., "Gigaspeech: An evolving, multi-domain asr corpus with 10,000 hours of transcribed audio", arXiv:2106.06909, 2021.
* Baevski, A. et al., "wav2vec 2.0: A framework for self-supervised learning of speech representations", arXiv:2006.11477, 2020.
* Baevski, A. et al., "Unsupervised speech recognition", NeurIPS 34:27826–27839, 2021.
* Zhang, Y. et al., "BigSSL: Exploring the frontier of large-scale semi-supervised learning for automatic speech recognition", arXiv:2109.13226, 2021.

---

## Contact

Questions, feedback, or interested in contributing?
Contact: **@lrsmello** or https://www.linkedin.com/in/lucasm65/
Or open an [issue](https://github.com/your-repo/lulu-teaches-mvp/issues) on the repository.

---