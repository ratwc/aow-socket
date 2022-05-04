FROM python:3.8.12-slim-buster

RUN python3 -m venv /opt/venv

# Install dependencies:
COPY . .
RUN . /opt/venv/bin/activate && pip install -r requirements.txt

# Run the application:
COPY app.py .
CMD . /opt/venv/bin/activate && exec python app.py

EXPOSE 8000