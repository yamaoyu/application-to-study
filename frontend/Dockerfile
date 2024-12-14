FROM node:20.15.1

WORKDIR /frontend

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "bash", "vue_settings.sh" ]