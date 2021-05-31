#!/bin/bash
echo "=== HC Tool by JAVISCO ==="
DEST=/share/hatool/data
SRC=/data_hc

if [ -d "$DEST" ]
then
echo "Directory $DEST exist"
else
`mkdir -p $DEST`
echo "Directory $DEST created"
fi

if [ -f "$DEST/ircode.json" ]
then
echo "File ircode.json exists, skipping"
else
echo "File ircode.json does not exist, copying $SRC/ircode.json to $DEST"
cp -f "$SRC/ircode.json" "$DEST"
fi

echo "Overwrite the latest configuration files"
cp -f "$SRC/climate_code.json" "$DEST"
cp -f "$SRC/api.json" "$DEST"
cp -f "$SRC/config_mqtt.json" "$DEST"
cp -f "$SRC/data.json" "$DEST"
cp -f "$SRC/device_template.json" "$DEST"
cp -f "$SRC/mqtt.json" "$DEST"
cp -f "$SRC/template_media_ir.json" "$DEST"
cp -f "$SRC/code.txt" "$DEST"
cp -f "$SRC/configuration_template.yaml" "$DEST"
cp -f "$SRC/list_channel.csv" "$DEST"

echo "Clean the temporary folder"
rm -rf $SRC

echo "Starting Javis HC Tool..."
/dist/main
