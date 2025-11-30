# ⚡ Email Notification Setup - Quick Checklist

## What You're Setting Up

Email notifications sent to **mimx85@msn.com** when pipeline runs:
- ✅ Success: All steps passed, S3 locations, next run time
- ❌ Failure: What failed, why it failed, how to fix it

---

## Quick Setup (5 minutes)

### Step 1: Choose Email Provider (1 min)

```
☐ Gmail (Recommended - easiest)
☐ Outlook/Microsoft 365
☐ Yahoo Mail
☐ Other SMTP server
```

### Step 2: Get Your Email Credentials (2 min)

**For Gmail:**
```
1. Go to: myaccount.google.com/apppasswords
2. Select: Mail → Windows Computer
3. Copy: 16-character app password
```

**For Outlook:**
```
1. Go to: account.microsoft.com
2. Security → App passwords (if 2FA enabled)
3. Copy: Your password or app password
```

**For Yahoo:**
```
1. Go to: Account Security
2. Generate app password
3. Copy: 16-character code
```

### Step 3: Add 5 GitHub Secrets (2 min)

Go to: **GitHub.com** → Your Repo → **Settings** → **Secrets and variables** → **Actions**

```
☐ EMAIL_SERVER = smtp.gmail.com (or your provider)
☐ EMAIL_PORT = 587
☐ EMAIL_USERNAME = your email address
☐ EMAIL_PASSWORD = your app password (16 char)
☐ EMAIL_FROM = your email address
```

---

## Email Provider Quick Reference

### Gmail 📧
```
EMAIL_SERVER: smtp.gmail.com
EMAIL_PORT: 587
EMAIL_USERNAME: your@gmail.com
EMAIL_PASSWORD: xxxx xxxx xxxx xxxx (app password from myaccount.google.com/apppasswords)
EMAIL_FROM: your@gmail.com
```

### Outlook 🔵
```
EMAIL_SERVER: smtp-mail.outlook.com
EMAIL_PORT: 587
EMAIL_USERNAME: your@outlook.com
EMAIL_PASSWORD: your password (or app password if 2FA)
EMAIL_FROM: your@outlook.com
```

### Yahoo 💛
```
EMAIL_SERVER: smtp.mail.yahoo.com
EMAIL_PORT: 587
EMAIL_USERNAME: your@yahoo.com
EMAIL_PASSWORD: app password from Account Security
EMAIL_FROM: your@yahoo.com
```

---

## Verification Checklist

- [ ] Email secrets added (5 total)
- [ ] All secrets values correct
- [ ] Email address is mimx85@msn.com in workflow
- [ ] Ready to test

---

## Testing

### Manual Test Run

1. Go to: **GitHub.com** → Your Repo → **Actions**
2. Click: **"Daily Super Agent Trading Pipeline"**
3. Click: **"Run workflow"** → **"Run workflow"**
4. Wait: 2-3 minutes for email

### Check Email

1. Open: **mimx85@msn.com** inbox
2. Look for: Email from "GitHub Actions"
3. Subject: "✅ SUCCESS" or "❌ FAILED"
4. Content: Detailed job status

---

## If Email Doesn't Arrive

### Step 1: Check Spam
```
☐ Gmail → Spam folder
☐ Outlook → Junk folder
☐ Yahoo → Spam folder
```

### Step 2: Verify Secrets
```
☐ EMAIL_SERVER correct for provider
☐ EMAIL_PORT is 587
☐ EMAIL_USERNAME is your email
☐ EMAIL_PASSWORD is app password (not regular password if 2FA)
☐ EMAIL_FROM is your email
```

### Step 3: Check GitHub Logs
```
1. Go to: Actions → Latest run
2. Expand: "Send Email Notification"
3. Look for: Error message
```

### Step 4: Re-create Secrets
```
1. Delete old secrets
2. Re-add all 5 secrets carefully
3. Test again
```

---

## What You'll Receive

### Success Email Contains:
- ✓ All steps passed
- ✓ S3 file locations (raw/AAPL/, etc.)
- ✓ Execution metrics
- ✓ Next scheduled run time
- ✓ Link to GitHub Actions logs

### Failure Email Contains:
- ✗ Which step failed
- ✗ Common failure causes
- ✗ Troubleshooting steps
- ✗ How to fix it
- ✗ Link to detailed logs

---

## Summary

**What was done:** Workflow updated with email notifications
**What you do:** Add 5 email secrets to GitHub
**Time needed:** ~5 minutes
**Test method:** Click "Run workflow" and check email

---

**Next:** Follow EMAIL_NOTIFICATION_SETUP.md for detailed instructions!
