Sorry, i didnt have time to make a good writeup, but TL;DR:

1. lfi via file:/// -> read & render arbitrary file on disk
2. log injection -> can injection HTML into logs via username
3. exfiltration: via meta refresh tag!

so, the steps are:

1. inject meta refresh tag start via controlled username
2. get admin SID to be logged
3. inject end of meta refresh tag
4. have admin bot visit logfile

