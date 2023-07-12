tar --owner="arx" --group="arx" \
    --exclude challenge/flag.html \
    --exclude challenge/Dockerfile \
    --transform 's|Dockerfile.handout|Dockerfile|' \
    --transform 's|flag.html.handout|flag.html|' \
    --transform 's|challenge|run|' \
    -czvf handout.tar.gz challenge sources
