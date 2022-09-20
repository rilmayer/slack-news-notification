# slack-news-notifications
News notification to slack by (AWS Lambda, GCP Cloud Function)

## Install Modules
```sh
pip install -r requirements.txt
```

## Google Cloud Function
### Debug
```sh
# 起動
functions-framework --target sub --signature-type=event --port=8080 --debug

# サンプル
curl localhost:8080 \
  -X POST \
  -H "Content-Type: application/json" \
  -H "ce-id: 123451234512345" \
  -H "ce-specversion: 1.0" \
  -H "ce-time: 2020-01-02T12:34:56.789Z" \
  -H "ce-type: google.cloud.pubsub.topic.v1.messagePublished" \
  -H "ce-source: //pubsub.googleapis.com/projects/MY-PROJECT/topics/MY-TOPIC" \
  -d '{
        "message": {
          "data": "d29ybGQ=",
          "attributes": {
             "attr1":"attr1-value"
          }
        },
        "subscription": "projects/MY-PROJECT/subscriptions/MY-SUB"
      }'
    
```

### Deploy
```sh
# Cloud Function
export TOPIC_NAME=rhd-da-slack-news-notification
gcloud functions deploy slack-news-notification \
  --runtime=python310 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=subscribe \
  --trigger-topic=$TOPIC_NAME
# Test
gcloud pubsub topics publish $TOPIC_NAME --message="message"
```

### Cloud Scheduler Pub/Sub
Please set your schedule on the Cloud Shceduler.

Ex. `0 9 * * * (Asia/Tokyo)`

## Test
### Unit test (TODO)
```
python -m unittest tests
```

## Install Modules
```
# If the folder not exists
mkdir lib

# install modules
pip install -r requirements.txt -t ./lib
```

### Test (notify slack)
```
# install loacl development module
pip install python-lambda-local

# Set environment variable
export CHANNEL_URL=""

# Test
python-lambda-local -f lambda_handler -t 3 lambda_function.py event.json
```

## Deploy
```
# Set aws cli profile(option)
export AWS_DEFAULT_PROFILE=[profile-name]

# function-name and slack-channel-url are reqired
deploy.sh -f [fuction-name] \
                 -c [channel-url] \
```
