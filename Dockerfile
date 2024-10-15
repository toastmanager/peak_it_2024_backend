FROM python:3.12-alpine


WORKDIR /backend


COPY ./requirements.txt /backend/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt


COPY . /backend


CMD ["fastapi", "run", "src/main.py", "--port", "80"]