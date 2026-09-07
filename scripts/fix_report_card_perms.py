import boto3
import os

# --- Configuration ---
# Your Space's region (e.g., 'nyc3', 'ams3', 'sgp1')
REGION = "nyc3"
# The name of your Space (bucket)
SPACE_NAME = "sprocket-image-gen-main-1"
# DigitalOcean Spaces API credentials
ACCESS_KEY = os.getenv("SPACES_ACCESS_KEY")
SECRET_KEY = os.getenv("SPACES_SECRET_KEY")


def make_files_public():
    # Initialize the S3 client pointing to DigitalOcean
    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=REGION,
        endpoint_url=f"https://{REGION}.digitaloceanspaces.com",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )

    try:
        # Paginator ensures we catch all files if there are > 1000
        paginator = client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=SPACE_NAME)

        print(f"Starting to update permissions in Space: {SPACE_NAME}...")

        file_count = 0
        for page in pages:
            if "Contents" not in page:
                print("The Space is empty.")
                return

            for obj in page["Contents"]:
                file_key = obj["Key"]

                # Update the ACL to 'public-read'
                client.put_object_acl(
                    Bucket=SPACE_NAME, Key=file_key, ACL="public-read"
                )

                print(f" [DONE] Set public: {file_key}")
                file_count += 1

        print(f"\nFinished! Total files updated: {file_count}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    make_files_public()
