docker build -t kaiser-app .
docker run --rm \
  -e DISPLAY=$DISPLAY \
  -v $(pwd)/host-saves:/app/host-saves \
  kaiser-app