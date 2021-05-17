#!/bin/bash
#Function get current date time
function getTime() {
  date +"%Y-%m-%d %H:%M:%S"
} # end getTime
# echo "[$(getTime) -- INFO]: Chuẩn bị..."
# rm -rf hatool_docker
# git clone git@bitbucket.org:javisco/hatool_docker.git

# build HC tool mới
echo "[$(getTime) -- INFO]: Bắt đầu cập nhật HC tool mới..."

# git clone git@bitbucket.org:javisco/18_ha_tool.git
# cd 18_ha_tool
# mv 18_ha_tool/ hatool
sudo systemctl stop hatool
rm -rf /usr/share/hassio/hatool/dist/main
rm -rf /usr/share/hassio/hatool/build/main
cd /usr/share/hassio/hatool
git checkout .
echo "[$(getTime) -- INFO]: Bắt đầu lấy code mới nhất từ git..."
git pull
echo "[$(getTime) -- INFO]: Bắt đầu build bản mới..."
pyinstaller main.py
# pyinstaller test_mqtt.py
# pyinstaller update_hatool.py
sudo systemctl start hatool
echo "[$(getTime) -- INFO]: Đã start HC tool phiên bản mới..."