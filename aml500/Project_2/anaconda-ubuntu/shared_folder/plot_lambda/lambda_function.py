import matplotlib
matplotlib.use('Agg')  # Headless backend for Lambda
import matplotlib.pyplot as plt
import boto3

def lambda_handler(event, context):
    plt.figure()
    plt.plot([1, 2, 3], [4, 5, 6])
    plt.title("Simple Plot")
    plot_path = "/tmp/plot.png"
    plt.savefig(plot_path)

    # Upload to your S3 bucket
    s3 = boto3.client('s3')
    bucket = 'mlops-13afe8ab-a794-4f8f-80b6-e210e18b4990'
    key = 'lambda-plot.png'

    s3.upload_file(plot_path, bucket, key)

    return {
        'statusCode': 200,
        'body': f'Plot saved to s3://{bucket}/{key}'
    }

