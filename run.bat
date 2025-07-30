docker build -t kaiser-app .
docker run --rm ^
  -e DISPLAY=host.docker.internal:0.0 ^
  -v %cd%\host-saves:/app/host-saves ^
  kaiser-app