

FROM python:3.10-slim
WORKDIR /TryCodeApp
RUN apt-get update && apt-get install -y \
    g++ \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /TryCodeApp/temp

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=oj_project.settings
ENV PYTHONUNBUFFERED=1
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


