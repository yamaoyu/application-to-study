FROM python:3.12-slim
WORKDIR /backend
RUN apt update && apt install -y curl
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD [ "bash", "backend_settings.sh" ]