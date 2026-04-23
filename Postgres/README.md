docker network create mynet  
  
docker run -d --name mydb --network mynet -e POSTGRES_DB=parse -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=gsx13_528ll -p 5432:5432 postgres:16  
  
docker build -t myapp .  
  
docker run -d --name app --network mynet -p 7777:7777 myapp  

docker run -d --name nginx --network mynet -p 80:80 -v C:\Users\bazdi\Desktop\GO\Networks\Postgres\nginx.conf:/etc/nginx/conf.d/default.conf nginx  
    
http://localhost:7777/parse  
  
http://localhost:7777/data