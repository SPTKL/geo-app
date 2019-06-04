# The Littlest Web-GBAT

![](preview.gif)

## Instructions: 
- start redis service:
    - `docker run --name dash-cache -p 6379:6379 -d redis redis-server --appendonly yes`
- build docker container and run service
    - `docker build -t geo-app .`
    - `docker run geo-app python app.py`

## Core Architecture
- Note: currently under development, however we are testing out the following options
- __dash + redis + geosupport-api + csv streaming__
    - known issue: slow
- __dash + redis + geosupport-api + upload result to s3__
    - haven't tested
- __dash + redis + python-geosupport + upload result to s3__
    - haven't tested

## Resources
- spin up a local AWS like service --> [localstack](https://github.com/localstack/localstack) --> used for s3 upload testings
- plotly dash [documentation](https://dash.plot.ly/getting-started?_ga=2.234803990.923888503.1559487939-351445513.1559487939)
    - data-table [documentation](https://dash.plot.ly/datatable)
    - loading wheel [documentation](https://dash.plot.ly/dash-core-components/loading_component)