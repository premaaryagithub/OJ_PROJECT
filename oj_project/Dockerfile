FROM debian:bullseye

# Install Python manually
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    openjdk-17-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /TryCodeApp

COPY . .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN mkdir -p /TryCodeApp/temp

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=oj_project.settings
ENV PYTHONUNBUFFERED=1

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
