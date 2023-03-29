FROM ubuntu:18.04 as prod

MAINTAINER Luis Bastiao <luis.kop@gmail.com>

RUN apt update \
 && apt -y -q install build-essential libssl-dev libffi-dev python3-dev cargo \
                          libjpeg-dev libpq-dev postgresql-client curl git python-pip \
                          vim libcurl4-openssl-dev uwsgi uwsgi-plugin-python \
                          python-dev libxml2-dev libxslt1-dev libyaml-dev

RUN mkdir -p /var/log/ && mkdir -p /opt/local && mkdir -p /opt/mongodb/db-catalogue

# Install nodejs
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install -y nodejs

# Copy requirements.txt and install dependencies
COPY ./requirements.txt /requirements.txt

RUN pip install -U pip==20.3.4 \
    # the step below is IMPORTANT so uwsgi is able to start (production)
    && mkdir -p /opt/local && cd /opt/local \
    # install required packages before pip build step: django is required by django-ace
    && pip install $(grep -i "^django==" /requirements.txt) \
    && pip install -r /requirements.txt --ignore-installed

RUN apt-get purge -y --auto-remove build-essential libssl-dev cargo python3-dev \
 && apt-get clean && rm -rf /var/lib/apt/lists/* \
 && rm -rf ~/.cache/pip /requirements.txt

VOLUME /deploy/catalogue/

# Add uwsgi files
COPY ./uwsgi-prod.ini /etc/uwsgi/apps-enabled/catalogue.ini

COPY ./start_catalogue.sh /

ENTRYPOINT ["/start_catalogue.sh"]

FROM prod as dev

COPY ./requirements-dev.in /requirements-dev.in
RUN pip install -r /requirements-dev.in \
 && rm -rf ~/.cache/pip /requirements-dev.in

# Things used to just run the tests
FROM prod as tests

RUN apt update \
 && apt -y -q install unzip wget chromium-browser

RUN cd tmp \
 && CHROMIUM_VERSION=$(chromium-browser --version | awk '{print $2}' | cut -d"." -f1-3) \
 && CHROMEDRIVER_VERSION=$(curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMIUM_VERSION) \
 && wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
 && unzip -j chromedriver_linux64.zip -d /usr/local/bin \
 && rm chromedriver_linux64.zip

COPY ./requirements-tests.txt /requirements-tests.txt
RUN pip install -r /requirements-tests.txt

RUN apt-get purge -y --auto-remove unzip wget \
 && apt-get clean \
 && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*
