FROM python:3.8-slim-buster

RUN python3 -m venv /opt/venv

# Install dependencies:
COPY . .
RUN . /opt/venv/bin/activate && pip install flask && pip install flask_socketio && pip install fxcmpy==1.2.10

# Run the application:
COPY app.py .
CMD . /opt/venv/bin/activate && exec python app.py

EXPOSE 8000