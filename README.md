**Pre-cofig**

To use app, you should create creds.conf file in the root directory with the [Google] section and api_token field.
Use creds-example.conf as an example.

**Tokens**

To use GoogleV3 Geocoding, you should issue free access token: 
https://developers.google.com/maps/documentation/geocoding/get-api-key, create file creds.conf in the root of the project and paste
a token value into the api_token field. 

You can paste any value into api_token field, but using GoogleV3 is highly recommended for stable app work.

**Docker**

To build a docker image run:
```
sudo docker build -t geocoding-exercise .
```
To run a docker image run:
```
sudo docker run -t -i -p 80:80 geocoding-exercise
```

Possible issue while building Docker image may be problem with DNS. To solve it, follow next steps:

Open or create file daemon.json
```
sudo vim /etc/docker/daemon.json
```
Paste there next string:
```
{
    "dns": ["<your primary nameserver from /etc/resolv.conf>", "8.8.8.8"]
}
```
Save file and run:
```
sudo service docker restart
```


**API Usage**

To run geocoding process you should make request to the ``run`` enpoint. Example with CURL:
```
curl -X POST \http://127.0.0.1:80/run \-H 'cache-control: no-cache' \-H 'content-type: multipart/form-data;boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \-F "csv_file=@/home/user/test.csv" \-F 'columns=address_1,address_2,address_3,postcode'
```
If the process has been started successfully, you will see the message:
```
{'success': True, 'message': 'Task successfully started. Id: 5def4b17-9dfc-480c-91b5-414bf2567432'}
```
or, if it is already task running:
```
{"success":false,"error":"There is not finished task. Please wait until it will be finished."}
```
.
You may check individual task status with it id:
```
curl -X POST \http://127.0.0.1:80/status?task_id=5def4b17-9dfc-480c-91b5-414bf2567432
```
or all tasks statuses with:
```
curl -X GET \http://127.0.0.1:80/stats
```

After the process is finished, stats request will give you a name of resulted file:
```
{"id":"5def4b17-9dfc-480c-91b5-414bf2567432","geocoder_status":{"in_progress":false,"processed_items":23870,"total_items":23870,"api_found_items":16998},"filepath":"./csv/5def4b17-9dfc-480c-91b5-414bf2567432.csv"}
```
It means, you can download, for example using wget:
```
wget -O result.csv http://127.0.0.1/csv/5def4b17-9dfc-480c-91b5-414bf2567432.csv
```