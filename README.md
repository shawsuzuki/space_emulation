# space_emulator

現在shawが作成中です。

## ファイルの説明

- README.md  
- contactgraph  
  - contact-revised.json  
  - contact_revise.py  
- container_maker  
  - Dockerfile  
  - container-maker.py  
- delay_insertion  
  - insert_direction.sh  
  - insert_do.py  
- docker-compose.yml  
- docker-remove.sh  
- input  
  - contact-graph.json  
  - emulation.config  
main-deploy.sh  
main-start.sh  

/input/emulation.config：このファイルに衛星の種類と数を入力します。
/input/contact-graph.json：json形式でコンタクトグラフを挿入します。
docker_maker.py：emulation_configure.configの内容に応じたdocker-compose.ymlファイルを生成します。
docker-compose.yml：自動で生成
dockerfile：もともとION動かすように作ったものを流用しているので、現在はION関係の部分などはコメントアウトさせています。

## 使い方

①emulation_configure.configの、セクションと、衛星数を決める。
②main-deploy.shを走らせる。コンテナが生成される。また、nftables.shによりコンテナ内の転送を許可する。
③main-start.shを走らせる。コンタクトグラフに基づく遅延がスタートする。
（④docker-remove.shを走らせる。全dockerコンテナ、イメージ、ボリューム、ネットワークを消去。）