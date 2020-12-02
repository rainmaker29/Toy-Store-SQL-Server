echo "Stopping the running mssql server ......."
sudo systemctl stop mssql-server
echo "Stopping the running mongo server ......."
sudo systemctl stop mongod
echo "Removing existing containers ..."
sudo docker rm flaskserver sqlserver mongoserver 
echo "Starting sql-server container ......."
sudo docker run -e 'ACCEPT_EULA=Y' -e "MSSQL_SA_PASSWORD=AMAAN@123" -p 1433:1433 --network toy_store_net --name sqlserver -d toy_store_mssql
echo "Starting mongo server container ......."
sudo docker run -d -v /var/lib/mongodb:/data/db -p 27017:27017 --name mongoserver --network toy_store_net toy_store_mongo

c=0
while [ $c -lt 5 ]
do
    clear
    echo "Waiting for mssql to setup ."
    sleep 1
    clear
    echo "Waiting for mssql to setup .."
    sleep 1
    clear
    echo "Waiting for mssql to setup ..."
    sleep 1
    clear
    echo "Waiting for mssql to setup ...."
    sleep 1
    c=`expr $c + 1`
done

echo "Starting Flask server container ......."
sudo docker run -it -p 5000:5000 --name flaskserver --network toy_store_net toy_store_flask
