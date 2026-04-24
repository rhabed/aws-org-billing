import boto3
import subprocess
import os

def check_aws_session(profile=None):
    """Check if the current AWS session is valid."""
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        return True, f"Logged in to {profile or 'default'} as {identity.get('Arn')}"
    except Exception as e:
        return False, str(e)

