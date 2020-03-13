FROM python:3.8

# install requirements
ADD requirements*.txt setup.cfg ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /tmp/build/put/ \
 && echo 'super_hostname' > /tmp/build/put/hostname \
 && echo '{"foo":"bar"}' > /tmp/build/put/test.json

# install assets
ADD assets/ /opt/resource/
ADD test/ /opt/resource-tests/

RUN /opt/resource-tests/test.sh

FROM python:3.8-alpine

# install requirements
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# install assets
ADD assets/ /opt/resource/
