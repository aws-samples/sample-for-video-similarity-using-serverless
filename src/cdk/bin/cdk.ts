#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { CfnParameter } from 'aws-cdk-lib';
import { VideoSimilarityStack } from '../lib/video-similarity-stack';

const app = new cdk.App();

new VideoSimilarityStack(app, 'VideoSimilarityStack', {});

app.synth();