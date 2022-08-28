FROM python:3.9

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install -r requirements.txt

ENTRYPOINT [ "python3", "-m", "example" ]