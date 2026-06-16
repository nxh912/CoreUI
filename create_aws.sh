## 

export BUCKETNAME=mroprompt
export URL=s3://ai.endeavourx.${BUCKETNAME}
# Create the S3 Bucket
### aws s3 mb s3://ai.endeavourx.${BUCKETNAME}

# ngailam.ho@endeavourx.ai

#aws s3 website   ${URL} --index-document index.html --error-document index.html
#aws s3 ls        s3://ai.endeQavourx.${BUCKETNAME} 

#aws s3 sync dist/ ${URL}  --acl public-read
aws s3 sync dist/ ${URL}

### aws s3 sync dist/ s3://ai.endeavourx.${BUCKETNAME}/dist≈ --acl public-read
aws s3 ls $URL --recursive --human-readable --summarize

## STATIC WEB -- Enable Static Website Hosting
aws s3 website s3://ai.endeavourx.mroprompt/ --index-document index.html --error-document index.html

### Remove the Public Access Block
aws s3api put-public-access-block \
    --bucket  ${URL/s3:\/\//} \
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

## apply polcy.json
aws s3api put-bucket-policy --bucket ai.endeavourx.mroprompt --policy file://policy.json

policy.json

DISALBE--
aws s3api delete-bucket-policy --bucket ai.endeavourx.mroprompt

ENABLE --
aws s3api put-bucket-policy --bucket ai.endeavourx.mroprompt --policy file://policy.json

