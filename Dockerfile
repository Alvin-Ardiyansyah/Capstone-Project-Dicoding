FROM python:3.10-slim

WORKDIR /app

# Install torch CPU-only first (to avoid huge CUDA version from sentence-transformers)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project (respecting .dockerignore)
COPY . .

# Switch to modeling directory (so "from services import ..." works)
WORKDIR /app/modeling

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
