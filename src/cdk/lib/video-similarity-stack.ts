import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigatewayv2';
import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as aoss from 'aws-cdk-lib/aws-opensearchserverless';
import { Construct } from 'constructs';

export class VideoSimilarityStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: cdk.StackProps) {
        super(scope, id, props);

        const sagemaker_endpoint = new cdk.CfnParameter(this, "sagemakerEndpoint", {
            type: "String",
            description: "Sagemaker endpoint for Resnet50.",
            default: "Resnet50"
        })

        if (sagemaker_endpoint === undefined || sagemaker_endpoint.valueAsString === '') {
            throw new Error('SageMaker endpoint is not defined, use: cdk deploy --parameters sagemakerEndpoint=Resnet50');
        }

        // Create OpenSearch Serverless Collection
        const collection = new aoss.CfnCollection(this, 'VideoSimilarityCollection', {
            name: 'video-similarity',
            description: 'Collection for video similarity search',
            type: 'VECTORSEARCH',
        });

        // Create Lambda function
        const lambdaFunction = new lambda.DockerImageFunction(this, 'VideoSimilarityFunction', {
            code: lambda.DockerImageCode.fromImageAsset('../lambda'),
            memorySize: 4096,
            timeout: cdk.Duration.minutes(5),
            ephemeralStorageSize: cdk.Size.mebibytes(4096),
            environment: {
                SAGEMAKER_ENDPOINT: sagemaker_endpoint.valueAsString,
                OPENSEARCH_HOST: collection.attrCollectionEndpoint.replace("https://", ""),
            },
        });

        // Create data access policy
        const cfnAccessPolicy = new aoss.CfnAccessPolicy(this, 'VideoSimilarityAccessPolicy', {
            name: 'video-similarity-access-policy',
            policy: JSON.stringify([{
                Rules: [{
                    ResourceType: "index",
                    Resource: ['index/video-similarity/*'],
                    Permission: ['aoss:*'],
                }],
                Principal: [lambdaFunction.role!.roleArn],
            }]),
            type: 'data'
        });

        // Create network security policy for OpenSearch
        const networSecurityPolicy = new aoss.CfnSecurityPolicy(this, 'NetworkSecurityPolicy', {
            name: 'video-similarity-network-policy',
            type: 'network',
            policy: JSON.stringify([{
                Rules: [{
                    ResourceType: "collection",
                    Resource: ['collection/video-similarity*'],
                }],
                "AllowFromPublic": true
            }]),
        });

        // Add Lambda permissions
        lambdaFunction.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                's3:GetObject',
                's3:PutObject',
                's3:ListBucket',
            ],
            resources: ['arn:aws:s3:::*'],
        }));

        lambdaFunction.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'sagemaker:InvokeEndpoint',
            ],
            resources: ['*'],
        }));

        lambdaFunction.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'aoss:*',
            ],
            resources: ['*'],
        }));

        // Create HTTP API
        const api = new apigateway.HttpApi(this, 'VideoSimilarityApi', {
            apiName: 'Video Similarity API',
            corsPreflight: {
                allowHeaders: ['Content-Type', 'Authorization'],
                allowMethods: [apigateway.CorsHttpMethod.POST, apigateway.CorsHttpMethod.GET, apigateway.CorsHttpMethod.OPTIONS],
                allowOrigins: ['*'],
            },
        });

        // Define API routes
        const routes = [
            { path: 'get_video_vector', method: apigateway.HttpMethod.POST },
            { path: 'insert_video_vector', method: apigateway.HttpMethod.POST },
            { path: 'search_similarity_videos', method: apigateway.HttpMethod.POST },
            { path: 'video_similarity', method: apigateway.HttpMethod.POST },
            { path: 'create_opensearch_index', method: apigateway.HttpMethod.POST },
        ];

        const lambdaIntegration = new integrations.HttpLambdaIntegration('LambdaIntegration', lambdaFunction);

        routes.forEach(route => {
            api.addRoutes({
                path: `/${route.path}`,
                methods: [route.method],
                integration: lambdaIntegration,
            });
        });

        // Output the API URL
        new cdk.CfnOutput(this, 'ApiUrl', {
            value: api.url!,
            description: 'HTTP API Gateway URL',
        });
    }
}