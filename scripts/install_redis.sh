#!/usr/bin/env bash
echo "Installing Redis 3.0.7"
cd ~vagrant
echo
wget http://download.redis.io/releases/redis-3.0.7.tar.gz
echo
tar xzf redis-3.0.7.tar.gz
echo
cd redis-3.0.7
echo
make
sudo make install
sudo echo utils/install_server.sh
echo "Done installing Redis"