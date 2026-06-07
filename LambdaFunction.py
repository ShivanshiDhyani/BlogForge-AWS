import boto3
import botocore.config
import json
import time
import random
from datetime import datetime

def blog_bedrock(blogtopic: str) -> str:
    max_retries = 5
    models = [
        {
            "modelId": "us.amazon.nova-micro-v1:0",
            "body": {
                "messages": [{"role": "user", "content": f"Write a 200 word blog on the topic of {blogtopic}"}],
                "inferenceConfig": {"maxTokens": 512, "temperature": 0.7}
            },
            "responseKey": "nova"
        },
        {
            "modelId": "amazon.nova-micro-v1:0",
            "body": {
                "messages": [{"role": "user", "content": f"Write a 200 word blog on the topic of {blogtopic}"}],
                "inferenceConfig": {"maxTokens": 512, "temperature": 0.7}
            },
            "responseKey": "nova"
        },
        {
            "modelId": "amazon.titan-text-express-v1",
            "body": {
                "inputText": f"Write a 200 word blog on the topic of {blogtopic}",
                "textGenerationConfig": {"maxTokenCount": 512, "temperature": 0.7}
            },
            "responseKey": "titan"
        },
        {
            "modelId": "amazon.titan-text-lite-v1",
            "body": {
                "inputText": f"Write a 200 word blog on the topic of {blogtopic}",
                "textGenerationConfig": {"maxTokenCount": 512, "temperature": 0.7}
            },
            "responseKey": "titan"
        }
    ]

    bedrock = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        config=botocore.config.Config(
            read_timeout=300,
            retries={'max_attempts': 1}
        )
    )

    for model in models:
        print(f"Trying model: {model['modelId']}")
        for attempt in range(max_retries):
            try:
                response = bedrock.invoke_model(
                    body=json.dumps(model['body']),
                    modelId=model['modelId'],
                    contentType="application/json",
                    accept="application/json"
                )
                response_content = response['body'].read()
                response_data = json.loads(response_content)
                print("Full response:", response_data)

                if model['responseKey'] == "nova":
                    blog_details = response_data['output']['message']['content'][0]['text']
                elif model['responseKey'] == "titan":
                    blog_details = response_data['results'][0]['outputText']

                print(f"Success with: {model['modelId']}")
                return blog_details

            except Exception as e:
                error_str = str(e)
                if "ThrottlingException" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Throttled, attempt {attempt + 1}. Waiting {wait_time:.1f}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"Retries exhausted for {model['modelId']}, trying next...")
                        break
                else:
                    print(f"Error with {model['modelId']}: {e}")
                    break

    print("All models exhausted")
    return ""


def save_details_in_s3(s3_key, s3_bucket, generated_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generated_blog)
        print(f"Blog saved to S3: {s3_key}")
    except Exception as e:
        print(f"Error saving to S3: {e}")


def lambda_handler(event, context):
    try:
        event_body = json.loads(event['body'])
        blogtopic = event_body['blog_topic']

        generated_blog = blog_bedrock(blogtopic)

        if generated_blog:
            current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            s3_key = f"blog-output/{current_time}.txt"
            s3_bucket = 'bedrockbucketoutput'
            save_details_in_s3(s3_key, s3_bucket, generated_blog)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'message': 'Blog generated successfully!',
                    'blog': generated_blog
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Failed to generate blog post'})
            }

    except Exception as e:
        print(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }