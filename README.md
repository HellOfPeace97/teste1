# backend_pd24
# cria network no docker para a api comunicar com a base de dados
docker network create -d bridge mongo-network
# da pull e poe a correr a db no porto definido, dá bind do volume a usar e a network que permitirá receber da api
docker run -d --network mongo-network --name mongo -p 27017:27017 -v MongoDB:/data/db mongo
# da pull e poe a correr a api mapeia os portos, bind da diretoria para a app (para ficar com as alterações de código, necessário apenas para dev) usa a network para conectar a bd e linka ao mongo container
docker run -d --network mongo-network --name backend1 -p 8000:8000 -v "$(pwd):/app" --link mongo api