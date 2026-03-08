import boto3, os
c = boto3.client('bedrock', region_name='us-east-1',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID',''),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY',''))
models = c.list_foundation_models(byOutputModality='TEXT')['modelSummaries']
for m in models:
    mid = m['modelId']
    if 'titan' in mid.lower() or 'nova' in mid.lower():
        print(mid)
