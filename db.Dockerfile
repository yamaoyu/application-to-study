FROM mysql:8.0-debian

RUN apt-get update && apt-get install -y gettext

COPY entrypoint.sh /entrypoint.sh
COPY backend/db/init.template.sql /backend/db/init.template.sql

RUN chmod +x /entrypoint.sh
RUN chmod 644 /etc/mysql/my.cnf
RUN chmod 644 /etc/mysql/conf.d/docker.cnf

ENTRYPOINT ["/bin/bash","-c", "/entrypoint.sh"]