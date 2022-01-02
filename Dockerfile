FROM python:3.7.2-alpine
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1
RUN pip install --upgrade pip

RUN adduser -D worker
USER worker
WORKDIR /home/worker
# WORKDIR /

COPY --chown=worker:worker requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt
# RUN rm requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"
COPY --chown=worker:worker . .

COPY . /
#WORKDIR /app