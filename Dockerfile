# syntax=docker/dockerfile:1

FROM python:3.9-bullseye

WORKDIR /mockingbird
RUN mkdir -p /container/warehouse/cache
RUN mkdir -p /container/warehouse/cache/lda_visualization
RUN mkdir -p /container/warehouse/cache/topic_model
RUN mkdir -p /container/warehouse/cache/text_and_token
RUN mkdir -p /container/warehouse/cache/trends
RUN mkdir -p /container/warehouse/cache/word_clouds
RUN mkdir -p /container/warehouse/cache/word_frequencies
RUN mkdir -p /container/warehouse/cache/trajectory
# RUN chmod 777 -R /container/warehouse
RUN apt-get update
RUN apt-get install -y git
RUN git clone https://github.com/shayanfazeli/fame.git
RUN pip3 install --upgrade pip
RUN pip3 install -e ./fame
RUN apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "app/scripts/preparation.py"]
CMD [ "python3", "application.py"]