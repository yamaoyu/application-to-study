FROM node:20.19

WORKDIR /frontend

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "bash", "vue_settings.sh" ]