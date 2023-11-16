python3 ./container-maker/container-maker.py
docker compose build --no-cache 
docker compose up -d 
docker images
docker ps