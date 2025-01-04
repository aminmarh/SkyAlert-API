FROM python:3.9-slim

RUN apt-get -q -y update && apt-get install -y dos2unix
RUN apt-get install -y gcc

ENV USERNAME=skyalert-app
ENV WORKING_DIR=/home/skyalert-app

WORKDIR ${WORKING_DIR}

COPY app app
COPY requirements.txt .
COPY service_entrypoint.sh .

RUN groupadd ${USERNAME} && \
    useradd -g ${USERNAME} ${USERNAME}

RUN chown -R ${USERNAME}:${USERNAME} ${WORKING_DIR}
RUN chmod -R u=rwx,g=rwx ${WORKING_DIR}

USER ${USERNAME}
ENV PATH "$PATH:/home/${USERNAME}/.local/bin"
ENV PYTHONPATH="${PYTHONPATH}:/home/skyalert-app"

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV FLASK_APP=app:create_app
RUN dos2unix service_entrypoint.sh
RUN chmod +x service_entrypoint.sh

EXPOSE 5000

ENTRYPOINT [ "./service_entrypoint.sh" ]