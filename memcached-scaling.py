import json,boto3,os

REGION_NAME = os.getenv("AWS_REGION")
CACHE_NAME = 'prod-default'

def lambda_handler(event, context):
    
    message_json = (event['Records'][0])['Sns']['Message']
    message = json.loads(message_json)
    
    client = boto3.client('elasticache',region_name=REGION_NAME)
    
    response = client.describe_cache_clusters(
        CacheClusterId=CACHE_NAME,
    )
    cache_nodes = (response['CacheClusters'][0])['NumCacheNodes']
    
    if message['AlarmName'] == 'scaleout-memcache' and cache_nodes < 20 :

        cache_nodes += 1
        response = client.modify_cache_cluster(
            CacheClusterId=CACHE_NAME,
            NumCacheNodes=cache_nodes,
            ApplyImmediately=True,
        )
        print(response)
        
    elif message['AlarmName'] == 'scalein-memcache' and cache_nodes > 2:

        new_cache_nodes = cache_nodes - 1
        response = client.modify_cache_cluster(
            CacheClusterId=CACHE_NAME,
            NumCacheNodes=new_cache_nodes,
            ApplyImmediately=True,
            CacheNodeIdsToRemove=[ str(cache_nodes).zfill(4)]
        )
        print(response)
            
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
