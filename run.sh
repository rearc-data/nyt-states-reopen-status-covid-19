export REARC_DATA_PLATFORM_ROLE_ARN='arn:aws:iam::412981388937:role/CrossAccountRole-796406704065-796406704065'
export REARC_DATA_PLATFORM_EXTERNAL_ID='Rearc-Data-Platform-796406704065'
export ASSET_BUCKET='rearc-data-provider'
export MANIFEST_BUCKET='rearc-control-plane-manifest'
export CUSTOMER_ID='796406704065'
export DATASET_NAME='nyt-states-reopen-status-covid-19-platform'
export DATASET_ARN='arn:aws:dataexchange:us-east-1:796406704065:data-sets/0ed4f7cd215d115d0fe37fd3109bd49d'
export PRODUCT_NAME='COVID-19 United States Reopen and Shut Down Status by State | NY Times'
export PRODUCT_ID='prod-csznmknbjsrn6'
export SCHEDULE_CRON="cron(0 9 ? * 3 *)"
export REGION='us-east-1'
export PROFILE='adx'

echo "------------------------------------------------------------------------------"
echo "RearcDataPlatformRoleArn: $REARC_DATA_PLATFORM_ROLE_ARN"
echo "RearcDataPlatformExternalId: $REARC_DATA_PLATFORM_EXTERNAL_ID"
echo "CustomerId: $CUSTOMER_ID"
echo "AssetBucket: $ASSET_BUCKET"
echo "ManifestBucket: $MANIFEST_BUCKET"
echo "DataSetName: $DATASET_NAME"
echo "DataSetArn: $DATASET_ARN"
echo "ProductName: $PRODUCT_NAME"
echo "ProductID: $PRODUCT_ID"
echo "ScheduleCron: $SCHEDULE_CRON"
echo "Region: $REGION"
echo "PROFILE: $PROFILE"
echo "------------------------------------------------------------------------------"


# python pre-processing/pre-processing-code/source_data.py

./init.sh \
    --rdp-role-arn "${REARC_DATA_PLATFORM_ROLE_ARN}" \
    --rdp-external-id "${REARC_DATA_PLATFORM_EXTERNAL_ID}" \
    --customer-id "${CUSTOMER_ID}" \
    --schedule-cron "${SCHEDULE_CRON}" \
    --asset-bucket "${ASSET_BUCKET}" \
    --manifest-bucket "${MANIFEST_BUCKET}" \
    --dataset-name "${DATASET_NAME}" \
    --product-name "${PRODUCT_NAME}" \
    --product-id "${PRODUCT_ID}" \
    --region "${REGION}" \
    --first-revision "false" \
    --profile "${PROFILE}"