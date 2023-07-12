tar --owner="arx" --group="arx" \
    --exclude challenge/flag.txt \
    --transform 's|flag.txt.handout|flag.txt|' \
    --transform 's|challenge|pwnykey|' \
    -czvf handout.tar.gz challenge
