FROM python:3.11-slim

# Create a non-root user as required by Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

# Copy requirements and install dependencies
COPY --chown=user:user requirements.txt $HOME/app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r $HOME/app/requirements.txt

# Copy the full application code
COPY --chown=user:user . $HOME/app

# Create exports directory with correct permissions
RUN mkdir -p $HOME/app/backend/app/exports

# Hugging Face Spaces exposes port 7860
EXPOSE 7860

# Launch FastAPI on port 7860
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
