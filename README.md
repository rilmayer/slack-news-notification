# slack-news-notifications
News notification to slack by AWS Lambda

## Install Modules
```
# If the folder not exists
mkdir lib

# install modules
pip install -r requirements.txt -t ./lib
```

## Test
### Unit test (TODO)
```
python -m unittest tests
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
lambda_deploy.sh -f [fuction-name] \
                 -c [channel-url] \
```

