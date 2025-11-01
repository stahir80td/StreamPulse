# Redpanda Cloud Setup Guide

Complete guide to setting up free Kafka cluster on Redpanda Cloud for StreamPulse.

---

## 📋 Prerequisites

- Email address for account creation
- **NO credit card required** for 14-day trial
- After trial: Credit card needed to continue (or data is deleted after 7-day grace period)

---

## ⚠️ Important Trial Information

**Free Trial Details:**
- **$100 in free credits** (valid for 14 days)
- **No credit card required** during trial
- After 14 days: 7-day grace period to add payment
- Without payment: Cluster suspended, data deleted after grace period

**Best for:**
- Active job search (deploy when applying to jobs)
- Live demos during interview process
- Portfolio showcasing (can redeploy anytime)

---

## 🚀 Step-by-Step Setup

### Step 1: Create Redpanda Cloud Account

1. Go to [https://redpanda.com/try-redpanda](https://redpanda.com/try-redpanda)

2. Click **"Sign up and get your 14-day free trial"**

3. Sign up with:
   - Email + Password, OR
   - Google OAuth, OR
   - GitHub OAuth

4. **No credit card required!** ✅

5. Redpanda creates your organization and sends welcome email

---

### Step 2: Create Serverless Cluster

1. After logging in, you'll see a **"Welcome Cluster"** already created
   - Redpanda automatically provisions this for you
   - Includes a "hello-world" demo topic with sample data

2. **Or create a new cluster:**
   - Click **"Create Cluster"**
   - Select **"Serverless"**
   - Choose configuration:
     ```
     Cluster Name: streampulse-kafka
     Cloud Provider: AWS (recommended)
     Region: Choose closest to you
             - us-east-1 (N. Virginia)
             - us-west-2 (Oregon)
             - eu-west-1 (Ireland)
             - ap-southeast-1 (Singapore)
     ```

3. Click **"Create"**

4. Cluster is ready **instantly** (< 30 seconds) ⚡

---

### Step 3: Create Kafka Topic

1. In your cluster dashboard, click **"Topics"**

2. Click **"Create Topic"**

3. **Configure Topic:**
   ```
   Topic Name: content-downloads
   Partitions: 3
   Replication Factor: 3 (automatic)
   Retention: 7 days (604800000 ms)
   Cleanup Policy: delete
   ```

4. Click **"Create"**

---

### Step 4: Get Connection Credentials

1. Go to your cluster **"Overview"** page

2. Click **"How to connect"** or find the **"Kafka API"** section

3. You'll see:
   ```
   Bootstrap Server: xxx.xxx.xxx.cloud.redpanda.com:9092
   Security Protocol: SASL_SSL
   SASL Mechanism: SCRAM-SHA-256
   ```

4. **Create API Credentials:**
   - Click **"Security"** tab
   - Click **"Create API Key"** or **"Add User"**
   - Or use the **default credentials** shown in the UI
   
5. **Copy the following:**
   ```
   Username: (your username)
   Password: (your password - save immediately, won't show again!)
   Bootstrap Server: xxx.xxx.xxx.cloud.redpanda.com:9092
   ```

---

### Step 5: Test Connection (Optional)

**Using Redpanda Console (Built-in UI):**

1. Go to **"Topics"** tab in your cluster

2. Click on **"content-downloads"** topic

3. Click **"Actions"** → **"Produce Message"**

4. Enter test message:
   ```json
   {
     "test": "hello from redpanda",
     "timestamp": "2025-01-01T12:00:00Z"
   }
   ```

5. Click **"Produce"**

6. Scroll down to **"Messages"** section

7. You should see your test message ✅

---

### Step 6: Configure StreamPulse

**For Event Generator:**

Create `.env` file in `event-generator/`:
```bash
KAFKA_BOOTSTRAP_SERVERS=xxx.xxx.xxx.cloud.redpanda.com:9092
KAFKA_USERNAME=your-username-from-redpanda
KAFKA_PASSWORD=your-password-from-redpanda
KAFKA_TOPIC=content-downloads
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
```

**For Flink Processor:**

Create `.env` file in `flink-processor/`:
```bash
KAFKA_BOOTSTRAP_SERVERS=xxx.xxx.xxx.cloud.redpanda.com:9092
KAFKA_USERNAME=your-username-from-redpanda
KAFKA_PASSWORD=your-password-from-redpanda
KAFKA_TOPIC=content-downloads
KAFKA_GROUP_ID=flink-processor
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
```

---

## 📊 Free Tier Limits

```
✅ Trial Duration: 14 days
✅ Free Credits: $100
✅ Message Size: 1 MB max
✅ Partitions: Generous limits
✅ Topics: Unlimited
✅ Throughput: Usage-based (scales automatically)
✅ Storage: Usage-based
✅ Connectors: 300+ available
```

**Staying Under Limits:**

Event generator configured to produce ~7 events/minute = **10,080 events/day**
- Each event ~320 bytes (Avro)
- Daily usage: ~3.2 MB/day
- Well under $100 credit limit for 14 days ✅

**Estimated Credit Usage:**
- Based on low-volume demo traffic
- $100 should last full 14 days easily
- Serverless scales to zero when not in use

---

## 🔍 Monitoring Your Cluster

### Dashboard Metrics

1. Go to your cluster **"Overview"** page

2. View real-time metrics:
   - **Throughput**: Current ingress/egress
   - **Partition Count**: Number of partitions
   - **Consumer Lag**: How far behind consumers are
   - **Storage Used**: Current storage consumption

### Redpanda Console

Built-in web UI for managing your cluster:
- **Topics**: View, create, delete topics
- **Messages**: Produce and consume messages
- **Consumer Groups**: Monitor consumer lag
- **ACLs**: Manage access control

---

## 🛠️ Troubleshooting

### Issue: "Authentication failed"
```
Solution:
1. Verify KAFKA_USERNAME and KAFKA_PASSWORD are correct
2. Ensure you copied the password immediately after creation
3. Check SASL mechanism is SCRAM-SHA-256
4. Try creating new credentials in Security tab
```

### Issue: "Topic not found"
```
Solution:
1. Verify topic name is exactly "content-downloads"
2. Check topic exists in Topics tab
3. Ensure topic creation completed successfully
```

### Issue: "Connection timeout"
```
Solution:
1. Verify bootstrap server address is correct
2. Check KAFKA_SECURITY_PROTOCOL=SASL_SSL
3. Ensure firewall allows outbound connections to port 9092
4. Try different network (corporate firewalls may block)
```

### Issue: "Cluster suspended"
```
Solution:
1. Trial has expired (after 14 days)
2. Add credit card to continue using cluster
3. Or: Accept data loss and create new trial (new account)
4. Alternative: Deploy Kafka locally with Docker
```

### Issue: "Message size too large"
```
Solution:
1. Redpanda serverless: 1 MB max message size
2. Our Avro events are ~320 bytes - should never hit limit
3. If custom events, ensure they're < 1 MB
```

---

## 🔐 Security Best Practices

1. **Never commit credentials to Git:**
   ```bash
   # .env files are in .gitignore
   # Never share .env files publicly
   ```

2. **Save credentials securely:**
   - Password is shown only once during creation
   - Store in password manager
   - Update all services if you regenerate credentials

3. **Use environment variables:**
   - In Railway/Vercel, set as environment variables
   - Never hardcode credentials in source code

4. **Manage ACLs:**
   - Create separate users for different services
   - Grant minimum required permissions
   - Use Security tab to manage access

---

## 📈 After Trial Expires

### Option 1: Add Payment Method (Continue Using)
**Cost: ~$5-15/month for demo traffic**
```
- Pay-as-you-go pricing
- Only charged for actual usage
- No minimum commitment
- Can cancel anytime
```

**To add payment:**
1. Go to **"Billing"** in dashboard
2. Click **"Add Payment Method"**
3. Enter credit card details
4. Continue using cluster seamlessly

---

### Option 2: Let Trial Expire (Temporary Demo)
**Timeline:**
```
Day 14:  Trial expires → Cluster suspended
Day 15-21: 7-day grace period
Day 22:  Data permanently deleted
```

**Use this if:**
- You only need demo for active job search
- You'll redeploy with new account later
- You want to avoid costs

---

### Option 3: Alternative Solutions

**A) New Redpanda Account**
- Create new account with different email
- Get another 14 days free
- ⚠️ Against terms of service (use sparingly)

**B) Switch to Docker (Local/Cloud VM)**
- Deploy Kafka locally or on free cloud VM
- No ongoing costs
- More complex setup
- See `setup_docker_kafka.md` (create separately)

**C) Switch to Different Provider**
- Confluent Cloud: $400 credits (30 days, credit card required)
- AWS MSK: No free tier
- Self-host on Railway/Render: ~$5-10/month

---

## 🎯 Verification Checklist

Before moving to next step, verify:

- [ ] Redpanda Cloud account created
- [ ] Serverless cluster created and running
- [ ] Topic "content-downloads" created with 3 partitions
- [ ] Connection credentials copied and saved securely
- [ ] Test message produced and consumed successfully
- [ ] `.env` files configured in event-generator and flink-processor
- [ ] Security protocol set to SASL_SSL
- [ ] Trial status checked (days remaining)

---

## 📚 Additional Resources

- [Redpanda Cloud Documentation](https://docs.redpanda.com/redpanda-cloud/)
- [Redpanda Serverless Guide](https://docs.redpanda.com/redpanda-cloud/get-started/cluster-types/serverless/)
- [Kafka Quickstart](https://kafka.apache.org/quickstart)
- [Redpanda Community Slack](https://redpanda.com/slack)
- [Redpanda Status Page](https://status.redpanda.com/)

---

## 🎉 Next Steps

After completing Redpanda setup:

1. ✅ Set up Neon PostgreSQL → See `setup_neon.md`
2. ✅ Deploy services to Railway → See `deploy_railway.ps1`
3. ✅ Deploy frontend to Vercel → See `deploy_vercel.ps1`

---

## 💡 Pro Tips

**Maximize Your Free Trial:**

1. **Deploy during active job search**
   - Don't waste trial days sitting idle
   - Deploy when you're ready to share portfolio

2. **Monitor credit usage**
   - Check billing dashboard regularly
   - Adjust event generation rate if needed

3. **Keep demo lightweight**
   - Lower event generation rate
   - Reduce data retention if needed
   - Stop services when not demoing

4. **Prepare for demo day**
   - Test everything before sharing link
   - Have backup plan (video/screenshots)
   - Consider extending trial via AWS Marketplace ($300 credits)

5. **Professional presentation**
   - Add "Live Demo" badge to README
   - Note "Trial version - limited time" in docs
   - Offer to redeploy for specific demo requests

---

## 🚨 Important Reminders

1. **Save credentials immediately** - Password shown only once
2. **14-day trial** - Plan your demo timeline accordingly
3. **7-day grace period** - Add payment before data deletion
4. **No credit card during trial** - True no-risk testing
5. **Can redeploy anytime** - Create new account if needed

---

## 📞 Support

**Need Help?**
- Redpanda Community Slack: [https://redpanda.com/slack](https://redpanda.com/slack)
- Documentation: [https://docs.redpanda.com](https://docs.redpanda.com)
- Support Email: support@redpanda.com

**Questions about billing after trial:**
- Check Billing page in dashboard
- Contact Redpanda sales for custom quotes
- Request annual commitment discounts

---

**Redpanda Cloud is ready for StreamPulse! 🚀**

**Trial begins as soon as you create your cluster - use it wisely!**