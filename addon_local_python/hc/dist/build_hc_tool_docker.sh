#!/bin/bash
#Function get current date time
function getTime() {
  date +"%Y-%m-%d %H:%M:%S"
} # end getTime
# echo "[$(getTime) -- INFO]: Chuẩn bị..."

# build HC tool mới
echo "[$(getTime) -- INFO]: Build HC tool mới..."

# git clone git@bitbucket.org:javisco/18_ha_tool.git
cd ~/18_ha_tool
git checkout .
echo "[$(getTime) -- INFO]: Lấy code mới nhất của HC tool từ web"
git pull

echo "[$(getTime) -- INFO]: Xoá các bản build cũ"
rm -rf dist/*
rm -rf build/*

echo "[$(getTime) -- INFO]: Bắt đầu build HC tool ra file main"
pyinstaller --onefile main.py

echo "[$(getTime) -- INFO]: Chuyển đến thư mục HC tool addons"
#git clone git@bitbucket.org:javisco/55_hc_tool_addon.git
cd ~/55_hc_tool_addon/
git checkout .
git pull
echo "[$(getTime) -- INFO]: Xoá các file binary cũ trong hc tool addons..."
rm -rf hc/* 

echo "[$(getTime) -- INFO]: Copy các file binary mới..."
cp -r ~/18_ha_tool/data hc
cp -r ~/18_ha_tool/dist hc
cp -r ~/18_ha_tool/static hc
cp -r ~/18_ha_tool/templates hc
chmod +x ~/55_hc_tool_addon/hc/dist/main

# cp -r ~/18_ha_tool/yaml_util.pyc .
echo "[$(getTime) -- INFO]: Đẩy các file binary mới lên git..."
git add .
git config --global user.email "chinhnd@javisco.vn"
git config --global user.name "chinhnd"
git commit -m "$(getTime)"
git push
echo "[$(getTime) -- INFO]: Đã hoàn thành push file lên git. Hãy vào bitbucket để tạo tag build lên docker..."
