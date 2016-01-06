FROM alpine:3.3

# install common packages
RUN apk add --update-cache curl bash openssl sudo && rm -rf /var/cache/apk/*

# install etcdctl and confd
RUN apk add --update-cache curl tar \
    && curl -sSL https://github.com/coreos/etcd/releases/download/v2.2.1/etcd-v2.2.1-linux-amd64.tar.gz \
    | tar -vxz -C /usr/local/bin --strip=1 etcd-v2.2.1-linux-amd64/etcdctl \
    && chown root:root /usr/local/bin/etcdctl \
    && curl -sSL -o /usr/local/bin/confd https://github.com/kelseyhightower/confd/releases/download/v0.10.0/confd-0.10.0-linux-amd64 \
    && chmod +x /usr/local/bin/confd \
    && apk del --purge curl tar \
    && rm -rf /var/cache/apk/*

# define execution environment
CMD ["/app/bin/boot"]
EXPOSE 8000

# define work environment
WORKDIR /app

ADD build.sh /app/tmp/build.sh

ADD requirements.txt /app/requirements.txt

RUN DOCKER_BUILD=true /app/tmp/build.sh && rm -rf /app/*

ADD . /app

RUN ./manage.py collectstatic --settings=deis.settings --noinput  # create static resources

ENV DEIS_RELEASE 2.0.0-dev
