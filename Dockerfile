FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

# Default: run the FastAPI service. Override CMD in docker-compose for Streamlit.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
