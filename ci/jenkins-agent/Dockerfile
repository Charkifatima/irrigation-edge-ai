FROM python:3.11-slim-bookworm@sha256:a83ba18aef0f865b1a4a611c2cf460fe446f2795673bbb9fe43be570439e3b39

ENV PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u3 \
        openjdk-17-jre-headless=17.0.21.1+2-1~deb12u1 \
        openssh-server=1:9.2p1-2+deb12u10 \
    && rm -rf /var/lib/apt/lists/*

# SSH rejects locked accounts even when public-key authentication is used.
RUN groupadd --system --gid 10001 ci \
    && useradd --system --uid 10001 --gid ci --create-home --home-dir /home/ci --shell /bin/sh ci \
    && usermod --password x ci \
    && install -d -o root -g root -m 0755 /run/sshd \
    && install -d -o root -g root -m 0700 /var/lib/jenkins-agent/hostkeys \
    && install -d -o root -g root -m 0755 /run/jenkins-agent \
    && install -d -o ci -g ci -m 0750 /home/ci/agent

COPY sshd_config /etc/ssh/sshd_config
COPY --chmod=0755 entrypoint.sh /usr/local/sbin/jenkins-agent-entrypoint

WORKDIR /home/ci/agent
EXPOSE 2222
ENTRYPOINT ["/usr/local/sbin/jenkins-agent-entrypoint"]
