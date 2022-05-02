FROM python:3.8-slim-buster

RUN python3 -m venv /opt/venv

# Install dependencies:
COPY . .
RUN . /opt/venv/bin/activate && pip install flask==2.0.3 && pip install flask_socketio==5.1.1 && pip install fxcmpy==1.2.10 && pip install pymongo && pip install dnspython && pip install ta

# Run the application:
COPY app.py .
CMD . /opt/venv/bin/activate && exec python app.py

EXPOSE 8000