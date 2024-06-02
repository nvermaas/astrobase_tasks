FROM python:3.7.2
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

WORKDIR /
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

COPY . /

# build the image like this:
# docker build -t astrobase_tasks:latest .

# run the container like this:
# docker run -d --name astrobase_tasks --mount type=bind,source=$HOME/shared,target=/shared -p 8008:8000 --restart always astrobase_tasks:latest
