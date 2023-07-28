# Lambda Functions Playbook

Allows to create a lambda function in AWS

- Package code with all required libraries
- Upload zip file to S3
- Create IAM role and load policies from file (not possible with CF)
- Create Lambda function

Only the python language is handled for now (not java or node.js).

## Requirements

File structure of code for playbook

├── functions
│   └── `deleteUnusedVolumes`
│       ├── `deleteUnusedVolumes_policy.json`
│       ├── delete_unused_volumes.py
│       ├── info.yml
│       └── requirements.txt

Directory name will be the lambda function's name, code is in that directory
IAM policies required for the function needs to be in a JSON file with the naming `function_policy.json`
Description and handler of the lambda function need to be set in `info.yml`


## Deployment

 To deploy this stack:

 ```ansible-playbook -e 'profile=PROFILE function=FUNCTION_NAME' local.yml -vv```

 - FUNCTION_NAME is `deleteUnusedVolumes`

**NOTE:** - there seems to be a timing bug when deploying a Lambda function
for the first time. The first run will probably fail because the playbook
doesn't wait long enough for the IAM role to be usable. Just run it again.


