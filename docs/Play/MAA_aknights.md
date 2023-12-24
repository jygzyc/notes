# 

```bash
docker run -itd --rm --privileged \
    --pull always \
    -v ~/AppData/redroidData:/data \
    -p 5555:5555 \
    --name redroid11 \
    redroid/redroid:11.0.0-latest \
    redroid.gpu.mode=host
```

```yml
version: '3'
services:
  redroid11:
    image: redroid/redroid:11.0.0-latest
    command: redroid.gpu.mode=host
    ports:
      - "5555:5555"
    volumes:
      - "~/workspace/redroid/data:/data"
    privileged: true
```
