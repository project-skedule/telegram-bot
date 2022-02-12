FROM python:3.9-slim-buster

# == Update system ==
RUN apt-get update
RUN apt-get install --no-install-recommends -y curl build-essential iputils-ping

# Timezone
ENV TZ="Europe/Moscow"
# Python, Pip and Poetry configuration

ENV PIP_DISABLE_PIP_VERSION_CHECK=on 
ENV PIP_DEFAULT_TIMEOUT=100 
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create App folder 
RUN mkdir /skedule-telegram
WORKDIR /skedule-telegram
# copy all files
COPY . /skedule-telegram/
# compile texts
RUN python3 compile_texts.py
# Run app
CMD ["python3", "main.py"]