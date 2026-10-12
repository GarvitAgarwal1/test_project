# Centralized Student Activity Platform

A trust-and-verification layer for student achievements.

## Differentiators
- Each student claim is verified by a human.
- OCR cross-checks the certificate against submitted data.
- Rule-based anomaly detection flags suspicious claims.
- Generates accreditation-ready reports (NAAC/NIRF style).
- Auto-generates digital portfolio PDFs with QR verification.

## Tech Stack
- Frontend: React, Vite, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, PostgreSQL, Celery, Redis
- OCR: Tesseract (pytesseract)

## How to Run with Docker Compose
1. Ensure Docker and Docker Compose are installed.
2. Run `docker-compose up --build`
3. The backend starts at `http://localhost:8000`
4. The frontend starts at `http://localhost:5173`

## Database Seeding
To load demo data and default score rules, run this command in a separate terminal while docker is running:
```bash
docker-compose exec backend python -m scripts.seed
```

### Demo Credentials
- **Admin**: admin@demo.com / Admin@123
- **Faculty**: faculty1@demo.com / Faculty@123
- **Student**: student1@demo.com / Student@123
