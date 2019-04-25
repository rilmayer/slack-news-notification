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
  echo "set channel url: $VALUE_CURL"
  echo "upload function: $VALUE_FNAME"
  zip -r ./lambda_function.zip *

  # aws lambda update-function-code \
  #     --function-name $VALUE_CURL \
  #     --environment Variables={CHANNEL_URL=$CMDNAME}
  #     --zip-file fileb://lambda_function.zip \
  #     --region ap-northeast-1 \
  #     --publish

  rm ./lambda_function.zip
fi

exit 0