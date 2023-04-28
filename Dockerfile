FROM python:3.9-slim-buster
ADD hello.py /
COPY . /app
WORKDIR /app
RUN pip3 install Flask
EXPOSE 12345
CMD [ "python3", "./hello.py" ]
