# 🌐 Google Cloud Platform Setup for AgriMind

## 🚀 Quick Setup (15 minutes)

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" or use an existing one
3. Note your **Project ID** (e.g., `agrimind-demo-2024`)

### Step 2: Enable Required APIs
Run these commands in Google Cloud Shell or local terminal:

```bash
# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com  
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### Step 3: Create Service Account
```bash
# Create service account
gcloud iam service-accounts create agrimind-service \
    --display-name="AgriMind Hackathon Service Account"

# Generate key file
gcloud iam service-accounts keys create agrimind-service-key.json \
    --iam-account=agrimind-service@YOUR-PROJECT-ID.iam.gserviceaccount.com

# Grant required permissions
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:agrimind-service@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:agrimind-service@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/ml.developer"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:agrimind-service@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:agrimind-service@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

### Step 4: Update Environment Variables
Edit your `.env` file:

```bash
# Replace with your actual values
GOOGLE_CLOUD_PROJECT=your-actual-project-id
GOOGLE_APPLICATION_CREDENTIALS=./agrimind-service-key.json
VERTEX_AI_LOCATION=us-central1
BIGQUERY_DATASET=agrimind_analytics
CLOUD_STORAGE_BUCKET_PREFIX=agrimind
```

### Step 5: Test GCP Integration
```bash
# Run the GCP-enhanced demo
python agrimind_demo_gcp.py

# Or test GCP services specifically
python -c "
from google.cloud import aiplatform, vision, bigquery
print('✅ Google Cloud services imported successfully')
"
```

## 💡 Free Tier Limits (Perfect for Demo)

- **Vertex AI**: 20 prediction hours/month FREE
- **Vision API**: 1,000 requests/month FREE  
- **BigQuery**: 1TB queries/month FREE
- **Cloud Storage**: 5GB/month FREE
- **Firestore**: 50K reads, 20K writes/day FREE
- **Cloud Monitoring**: FREE tier available

## 🎯 Demo Features with GCP

With GCP enabled, your AgriMind demo will showcase:

1. **🤖 Vertex AI Predictions**: Industry-grade ML models
2. **👁️ Vision API**: Real crop image analysis
3. **📊 BigQuery Analytics**: Enterprise data processing
4. **☁️ Cloud Storage**: Scalable data storage
5. **🔥 Firestore**: Real-time agent messaging
6. **📈 Cloud Monitoring**: Production-ready monitoring

## 🔒 Security Best Practices

1. **Never commit** `agrimind-service-key.json` to git
2. **Use IAM roles** with minimal permissions
3. **Set budget alerts** at $10, $25, $50
4. **Delete resources** after demo to avoid charges

## 🚨 Troubleshooting

### Common Issues:

**"google.auth.exceptions.DefaultCredentialsError"**
- Make sure `GOOGLE_APPLICATION_CREDENTIALS` points to your key file
- Check file permissions and path

**"Access Denied" errors**
- Verify service account has correct IAM roles
- Check if APIs are enabled

**"Billing Required" errors**
- Some GCP services require billing enabled
- You can still use the demo without GCP (mock mode)

## 🎮 Running Without GCP

Don't have GCP set up yet? **No problem!**

The AgriMind system works perfectly without GCP:
```bash
# Run standard demo (no GCP required)
python agrimind_demo.py hybrid

# Uses intelligent fallbacks and mock data
```

## 💰 Cost Estimation

For a **30-minute hackathon demo**:
- **Vertex AI**: ~$0.50
- **Vision API**: ~$1.00 
- **BigQuery**: FREE (under 1GB)
- **Storage**: FREE (under 5GB)
- **Total**: ~$1.50 for impressive demo!

---

**Ready to supercharge your AgriMind demo with Google Cloud? 🚀**

Questions? Check the [GCP_INTEGRATION.md](GCP_INTEGRATION.md) for detailed examples!