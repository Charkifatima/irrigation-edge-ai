#!/bin/sh
set -eu

authorized_keys_source=/run/secrets/authorized_keys
host_keys_dir=/var/lib/jenkins-agent/hostkeys

if [ ! -s "$authorized_keys_source" ]; then
    echo "Missing Jenkins agent public keys at $authorized_keys_source" >&2
    exit 1
fi

mkdir -p /run/sshd /run/jenkins-agent "$host_keys_dir"
chmod 0755 /run/sshd /run/jenkins-agent
chmod 0700 "$host_keys_dir"
install -m 0644 "$authorized_keys_source" /run/jenkins-agent/authorized_keys

if [ ! -s "$host_keys_dir/ssh_host_ed25519_key" ]; then
    ssh-keygen -q -t ed25519 -N '' -f "$host_keys_dir/ssh_host_ed25519_key"
fi

chmod 0600 "$host_keys_dir/ssh_host_ed25519_key"
chmod 0644 "$host_keys_dir/ssh_host_ed25519_key.pub"

exec /usr/sbin/sshd -D -e -f /etc/ssh/sshd_config
