# futuredisk

Same nginx server hosts both futuredisk and futuredisk2.

See `challenge/docker-compose.yml` for how I've been running it locally. Basically, after installing requirements.txt (in a venv maybe) and using `mount.py` to mount the FUSE FS onto `./fuse` with `python3 mount.py -f -o allow-others fuse`, outside Docker, the directory is then bind mounted to `/var/www` for nginx to serve.

Having the fuse mount be inside the docker container is a little fiddly, and less secure. I haven't attempted to do that.

No solve script / healthcheck yet.

No RCE is intended. The only intentional attacker-controlled input to mount.py via FUSE is the read offset + size, and it should return a consistent view of the extremely large virtual file for all such windows.
