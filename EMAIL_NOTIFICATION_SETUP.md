# Email Notification Setup Guide

## Overview

The GitHub Actions workflow has been updated to send detailed email notifications to **mimx85@msn.com** when the pipeline runs, with complete job status and results.

---

## Email Details

### On Success ✅
- Status: SUCCESS
- Lists all passed steps
- Shows where results are stored (S3 paths)
- Provides execution metrics
- Shows next scheduled run time

### On Failure ❌
- Status: FAILED
- Identifies which step failed
- Lists common failure causes
- Provides troubleshooting steps
- Links to detailed logs

---

## Email Secrets Required

You need to add **5 new GitHub Secrets** for email functionality.

### Which Email Provider?

The workflow uses SMTP (standard email protocol). Choose one:

#### Option 1: Gmail (Recommended) 📧
**Steps:**
1. Go to: myaccount.google.com → Security
2. Enable 2-Factor Authentication
3. Create App Password: myaccount.google.com/apppasswords
4. Use these values:
   - `EMAIL_SERVER` = `smtp.gmail.com`
   - `EMAIL_PORT` = `587`
   - `EMAIL_USERNAME` = your Gmail address
   - `EMAIL_PASSWORD` = app password (16-char code)
   - `EMAIL_FROM` = your Gmail address

**Example:**
```
EMAIL_SERVER: smtp.gmail.com
EMAIL_PORT: 587
EMAIL_USERNAME: your.email@gmail.com
EMAIL_PASSWORD: xxxx xxxx xxxx xxxx
EMAIL_FROM: your.email@gmail.com
```

#### Option 2: Outlook/Microsoft 365 🔵
**Steps:**
1. Use your Outlook.com or Microsoft account
2. If 2FA enabled, create an app password

**Values:**
```
EMAIL_SERVER: smtp-mail.outlook.com
EMAIL_PORT: 587
EMAIL_USERNAME: your.email@outlook.com
EMAIL_PASSWORD: your password
EMAIL_FROM: your.email@outlook.com
```

#### Option 3: Yahoo Mail 💛
**Values:**
```
EMAIL_SERVER: smtp.mail.yahoo.com
EMAIL_PORT: 587
EMAIL_USERNAME: your.email@yahoo.com
EMAIL_PASSWORD: app password (16-char)
EMAIL_FROM: your.email@yahoo.com
```

#### Option 4: Custom SMTP Server
Use your own mail server settings.

---

## Setup Steps

### Step 1: Choose Your Email Provider
Pick Gmail, Outlook, or Yahoo above.

### Step 2: Get Your Email Credentials

**For Gmail:**
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character app password

**For Outlook:**
1. Create app password if 2FA enabled
2. Use your regular password otherwise

**For Yahoo:**
1. Go to: Account Security
2. Generate app password
3. Copy the 16-character code

### Step 3: Add GitHub Secrets

Go to: **GitHub.com** → Your Repo → **Settings** → **Secrets and variables** → **Actions**

Click **"New repository secret"** and add these 5 secrets:

#### Secret 1: EMAIL_SERVER
```
Name: EMAIL_SERVER
Value: smtp.gmail.com (or your provider's SMTP)
```

#### Secret 2: EMAIL_PORT
```
Name: EMAIL_PORT
Value: 587
```

#### Secret 3: EMAIL_USERNAME
```
Name: EMAIL_USERNAME
Value: your.email@gmail.com (your email)
```

#### Secret 4: EMAIL_PASSWORD
```
Name: EMAIL_PASSWORD
Value: xxxx xxxx xxxx xxxx (app password, 16 char)
```

#### Secret 5: EMAIL_FROM
```
Name: EMAIL_FROM
Value: your.email@gmail.com (same as username)
```

---

## What The Emails Will Look Like

### Success Email ✅

```
Subject: ✅ Super Agent Trader Pipeline - SUCCESS

🎯 SUPER AGENT TRADER - PIPELINE EXECUTION REPORT
================================================

Status: ✅ SUCCESS
Date: 2025-11-28 08:15:32 UTC

JOB DETAILS:
✓ Step 1: Code Checkout - PASSED
✓ Step 2: Python Setup (3.10) - PASSED
✓ Step 3: Dependency Installation - PASSED
✓ Step 4: Config Creation - PASSED
✓ Step 5: Pipeline Execution - PASSED
  - Data Agent: Fetched OHLC data (AAPL, MSFT, TSLA)
  - ML Agent: Models trained successfully
  - Predict Agent: Predictions generated
✓ Step 6: Logs Uploaded to S3 - PASSED

RESULTS LOCATION:
S3 Bucket: stock-trade-data-2025
Paths:
  • raw/AAPL/ - Raw OHLC data
  • raw/MSFT/ - Raw OHLC data
  • raw/TSLA/ - Raw OHLC data
  • features/ - Processed features
  • model/ - Trained models
  • predictions/ - Generated predictions
  • logs/ - Pipeline logs

NEXT RUN:
Tomorrow at 8:00 AM UTC (3:00 AM EST / 12:00 AM PST)
```

### Failure Email ❌

```
Subject: ❌ Super Agent Trader Pipeline - FAILED

⚠️ SUPER AGENT TRADER - PIPELINE EXECUTION REPORT
================================================

Status: ❌ FAILED

FAILURE LIKELY CAUSES:
• IBKR Connection Error
• AWS Credentials Invalid
• S3 Upload Failed
• Python Module Error

TROUBLESHOOTING STEPS:
1. Check GitHub Actions logs
2. Verify EC2 instance status
3. Verify TWS Gateway running
4. Check GitHub secrets
```

---

## Testing Email Notifications

### Test Email Before Full Setup

Once you add the email secrets, you can test by:

1. Go to GitHub → Actions
2. Select **"Daily Super Agent Trading Pipeline"**
3. Click **"Run workflow"** button
4. Check your email in a few minutes

**You should receive an email with detailed status!**

---

## Troubleshooting Email Issues

### ❌ "Email not received"

**Solution 1: Check spam folder**
- Gmail, Outlook, Yahoo sometimes put automated emails in spam
- Add `noreply@github.com` to contacts

**Solution 2: Verify secrets are correct**
- Re-check EMAIL_SERVER, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD
- For Gmail, use the app password, not your regular password

**Solution 3: Check GitHub Actions logs**
- Go to Actions → Latest run → Expand "Send Email" step
- Look for error message

**Solution 4: Gmail app password issue**
- Make sure you created app password in myaccount.google.com/apppasswords
- Not the regular Gmail password

**Solution 5: 2-Factor Authentication**
- Gmail requires app password (not regular password)
- Outlook might need 2FA enabled first

### ❌ "SMTP Connection Failed"

**Check:**
- Is EMAIL_SERVER correct for your provider?
- Is EMAIL_PORT correct (usually 587)?
- Is your email/password correct?
- Check GitHub Actions logs for exact error

---

## Email Secret Summary

| Secret | Example | Where to Get |
|--------|---------|---|
| EMAIL_SERVER | smtp.gmail.com | Provider's SMTP settings |
| EMAIL_PORT | 587 | Provider's SMTP port |
| EMAIL_USERNAME | your@gmail.com | Your email address |
| EMAIL_PASSWORD | xxxx xxxx xxxx xxxx | Gmail app password or your password |
| EMAIL_FROM | your@gmail.com | Your email address |

---

## Security Notes

✅ **Secure:**
- Secrets are encrypted in GitHub
- Email password is never exposed in logs
- Only visible to repo admins

❌ **NOT secure:**
- Don't commit secrets to code
- Don't share secret values
- Don't use regular password with 2FA enabled (use app password)

---

## Next Steps

1. **Choose email provider** (Gmail recommended)
2. **Get your credentials** (app password if needed)
3. **Add 5 GitHub secrets** (EMAIL_SERVER, etc.)
4. **Test manually** (click "Run workflow" button)
5. **Verify email received**

---

## Recommended Email Flow

```
8:00 AM UTC: Pipeline starts
    ↓
5-10 min: Pipeline completes
    ↓
Email sent to mimx85@msn.com
    ↓
Check email for:
  • Job status (✓ or ✗)
  • S3 file locations
  • Error messages if any
  • Troubleshooting tips
```

---

## More Help

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Email Server Settings:** https://emailproviders.com/

---

**Ready to set up email notifications?**

Follow the setup steps above and test with the manual trigger!
