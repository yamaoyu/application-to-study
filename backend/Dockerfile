FROM python:3.12
WORKDIR /backend
COPY ./requirements-dev.txt requirements-dev.txt
RUN pip install --no-cache-dir --upgrade -r requirements-dev.txt
COPY . .
CMD [ "bash", "backend_settings.sh" ]