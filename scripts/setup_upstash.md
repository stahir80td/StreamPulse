# Upstash Kafka Setup Guide

Complete guide to setting up free Kafka cluster on Upstash for StreamPulse.

---

## 📋 Prerequisites

- Email address for account creation
- Credit card (for verification only - won't be charged on free tier)

---

## 🚀 Step-by-Step Setup

### Step 1: Create Upstash Account

1. Go to [https://upstash.com](https://upstash.com)
2. Click **"Start Free"** or **"Sign Up"**
3. Sign up with:
   - Email + Password, OR
   - GitHub OAuth, OR
   - Google OAuth
4. Verify your email address

---

### Step 2: Create Kafka Cluster

1. After logging in, click **"Create Cluster"** or navigate to **Kafka → Create Cluster**

2. **Configure Cluster:**
   ```
   Name: streampulse-kafka
   Type: Free (Single Replica)
   Region: Choose closest to you
           - US East (Virginia)
           - US West (Oregon)
           - EU (Frankfurt)
           - Asia Pacific (Singapore)
   ```

3. Click **"Create Cluster"**

4. Wait 30-60 seconds for cluster creation

---

### Step 3: Create Kafka Topic

1. Select your cluster from the dashboard

2. Click **"Topics"** tab

3. Click **"Create Topic"**

4. **Configure Topic:**
   ```
   Topic Name: content-downloads
   Partitions: 3
   Retention Time: 7 days (604800000 ms)
   Retention Size: 10 MB (free tier limit)
   Max Message Size: 1 MB
   ```

5. Click **"Create"**

---

### Step 4: Get Connection Credentials

1. Go to your cluster details page

2. Click **"Connect"** or scroll to **"REST API"** section

3. **Copy the following:**
   ```
   Bootstrap Servers: xxx-xxx.upstash.io:9092
   Username: (shown in dashboard)
   Password: (shown in dashboard)
   ```

4. **Security Settings:**
   ```
   Security Protocol: SASL_SSL
   SASL Mechanism: SCRAM-SHA-256
   ```

---

### Step 5: Test Connection (Optional)

**Using Upstash Console:**

1. Go to **"Console"** tab in your cluster

2. Click **"Produce"**

3. Enter test message:
   ```json
   {
     "test": "hello from upstash"
   }
   ```

4. Click **"Send"**

5. Go to **"Consume"** tab

6. Click **"Start Consuming"**

7. You should see your test message ✅

---

### Step 6: Configure StreamPulse

**For Event Generator:**

Create `.env` file in `event-generator/`:
```bash
KAFKA_BOOTSTRAP_SERVERS=xxx-xxx.upstash.io:9092
KAFKA_USERNAME=your-username-from-upstash
KAFKA_PASSWORD=your-password-from-upstash
KAFKA_TOPIC=content-downloads
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
```

**For Flink Processor:**

Create `.env` file in `flink-processor/`:
```bash
KAFKA_BOOTSTRAP_SERVERS=xxx-xxx.upstash.io:9092
KAFKA_USERNAME=your-username-from-upstash
KAFKA_PASSWORD=your-password-from-upstash
KAFKA_TOPIC=content-downloads
KAFKA_GROUP_ID=flink-processor
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
```

---

## 📊 Free Tier Limits

```
✅ Messages per day: 10,000
✅ Message size: 1 MB max
✅ Retention: 7 days
✅ Storage: 10 MB total
✅ Partitions: Unlimited
✅ Topics: Unlimited
✅ Throughput: Shared (sufficient for demo)
```

**Staying Under Limits:**

Event generator configured to produce ~7 events/minute = **10,080 events/day**
- Slightly under 10K limit ✅
- Each event ~320 bytes (Avro) = **3.2 MB/day** ✅

---

## 🔍 Monitoring Your Cluster

### Dashboard Metrics

1. Go to your cluster dashboard

2. View real-time metrics:
   - **Messages/sec**: Current throughput
   - **Total Messages**: Messages produced today
   - **Storage Used**: Current storage consumption
   - **Active Connections**: Connected clients

### Alerts

Upstash will email you if:
- You approach 80% of daily message limit
- You approach 80% of storage limit
- Connection errors occur

---

## 🛠️ Troubleshooting

### Issue: "Authentication failed"
```
Solution:
1. Verify KAFKA_USERNAME and KAFKA_PASSWORD are correct
2. Check if you copied the full credentials (no spaces)
3. Ensure SASL mechanism is SCRAM-SHA-256
4. Try regenerating credentials in Upstash dashboard
```

### Issue: "Topic not found"
```
Solution:
1. Verify topic name is exactly "content-downloads"
2. Check topic exists in Upstash dashboard
3. Wait 30 seconds after topic creation
```

### Issue: "Connection timeout"
```
Solution:
1. Check firewall allows outbound connections to port 9092
2. Verify your IP isn't blocked (Upstash dashboard shows IPs)
3. Try from different network
4. Check Upstash status page: https://status.upstash.com
```

### Issue: "Message size too large"
```
Solution:
1. Upstash free tier: 1 MB max message size
2. Our Avro events are ~320 bytes - should never hit limit
3. If custom events, ensure they're < 1 MB
```

### Issue: "Daily limit reached"
```
Solution:
1. Free tier: 10K messages/day
2. Check current usage in dashboard
3. Reduce event generation rate (increase sleep time)
4. Wait until midnight UTC for reset
5. Consider upgrading to paid tier ($10/month for 100K/day)
```

---

## 🔐 Security Best Practices

1. **Never commit credentials to Git:**
   ```bash
   # .env files are in .gitignore
   # Never share .env files publicly
   ```

2. **Rotate credentials regularly:**
   - Upstash dashboard → Settings → Regenerate Password
   - Update all services with new credentials

3. **Use environment variables:**
   - In Railway/Vercel, set as environment variables
   - Never hardcode credentials in source code

4. **Restrict IP access (paid feature):**
   - Upstash Pro: Whitelist only your server IPs
   - Free tier: Public access (secure via SASL authentication)

---

## 📈 Scaling Beyond Free Tier

When you need more than 10K messages/day:

### Upstash Pro ($10/month)
```
- 100,000 messages/day
- 100 MB storage
- IP whitelisting
- Longer retention (30 days)
- Priority support
```

### Upstash Enterprise
```
- Custom limits
- Dedicated clusters
- SLA guarantees
- Multi-region replication
```

---

## 🎯 Verification Checklist

Before moving to next step, verify:

- [ ] Kafka cluster created and running
- [ ] Topic "content-downloads" created with 3 partitions
- [ ] Connection credentials copied
- [ ] Test message sent and received in Upstash console
- [ ] `.env` files configured in event-generator and flink-processor
- [ ] Security protocol set to SASL_SSL

---

## 📚 Additional Resources

- [Upstash Documentation](https://docs.upstash.com/kafka)
- [Kafka Quickstart](https://kafka.apache.org/quickstart)
- [Upstash Status Page](https://status.upstash.com)
- [Upstash Discord Community](https://discord.gg/upstash)

---

## 🎉 Next Steps

After completing Upstash setup:

1. ✅ Set up Neon PostgreSQL → See `setup_neon.md`
2. ✅ Deploy services to Railway → See `deploy_railway.ps1`
3. ✅ Deploy frontend to Vercel → See `deploy_vercel.ps1`

---

**Upstash Kafka is ready for StreamPulse! 🚀**