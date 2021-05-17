#!/bin/bash
#Function get current date time
function getTime() {
  date +"%Y-%m-%d %H:%M:%S"
} # end getTime
# echo "[$(getTime) -- INFO]: Chuẩn bị..."
# rm -rf hatool_docker
# git clone git@bitbucket.org:javisco/hatool_docker.git

# build HC tool mới
echo "[$(getTime) -- INFO]: Build HC tool mới..."

# git clone git@bitbucket.org:javisco/18_ha_tool.git
# cd 18_ha_tool
# mv 18_ha_tool/ hatool
sudo systemctl stop hatool
sudo systemctl disable hatool
rm -rf /usr/share/hassio/hatool/dist/main
rm -rf /usr/share/hassio/hatool/build/main
cd /usr/share/hassio/hatool
git checkout .
git pull
pyinstaller main.py
# pyinstaller test_mqtt.py
# pyinstaller update_hatool.py
#sudo systemctl start hatool

cd ../hatool_docker
git pull
echo "[$(getTime) -- INFO]: Xoá các file binary cũ trong hatool_docker..."
rm -rf data
rm -rf dist
rm -rf static
rm -rf templates
rm -rf const.pyc
rm -rf yaml_util.pyc
echo "[$(getTime) -- INFO]: Copy các file binary mới..."
cp -r /usr/share/hassio/hatool/data .
mkdir dist
cp -r /usr/share/hassio/hatool/dist/main dist
cp -r /usr/share/hassio/hatool/static .
cp -r /usr/share/hassio/hatool/templates .
cp -r /usr/share/hassio/hatool/const.pyc .
# cp -r /usr/share/hassio/hatool/yaml_util.pyc .
echo "[$(getTime) -- INFO]: Đẩy lên git..."
git add .
git config --global user.email "chinhnd@javisco.vn"
git config --global user.name "chinhnd"
git commit -m "$(getTime)"
git push
