#!/bin/bash

CMDNAME=`basename $0`

while getopts f:b:c: OPT
do
  case $OPT in
    "f" ) FLG_FNAME="TRUE" ; VALUE_FNAME="$OPTARG" ;;
    "c" ) FLG_CURL="TRUE" ; VALUE_CURL="$OPTARG" ;;
      * ) echo "Usage: $CMDNAME [-f function-name] [-c channel-url]" 1>&2
          exit 1 ;;
  esac
done

if [ "$FLG_FNAME" = "TRUE" ]; then
  echo "zip upload files"
  zip -r ./lambda_function.zip *

  echo "update function: $VALUE_FNAME"
  aws lambda update-function-code \
      --function-name $VALUE_FNAME \
      --zip-file fileb://lambda_function.zip \
      --region ap-northeast-1 \
      --publish

  echo "set channel url: $VALUE_CURL"
  aws lambda update-function-configuration \
      --function-name $VALUE_FNAME \
      --timeout 60 \
      --environment Variables={CHANNEL_URL=$VALUE_CURL}

  rm ./lambda_function.zip
  
  echo "update function is done!"
fi

exit 0