cd container-maker
python3 container-maker.py
cd ..
docker compose build --no-cache 
docker compose up -d 
docker images
docker ps
bash container-maker/nftables.sh