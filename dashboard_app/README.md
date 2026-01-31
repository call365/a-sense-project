# A-Sense Admin Dashboard

This is the admin dashboard for A-Sense Ad Network, built with Streamlit.

## Deployment Instructions (Streamlit Cloud)

Since Vercel has a size limit for serverless functions, we recommend deploying this dashboard on **Streamlit Cloud** (free and optimized for Streamlit).

1.  **Push code to GitHub**: Ensure your `a-sense-project` repository is up to date on GitHub.
2.  **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io/).
3.  **New App**: Click "New app" -> "Use existing repo".
4.  **Select Repository**: Choose `call365/a-sense-project`.
5.  **Main File Path**: Enter `dashboard_app/dashboard.py` (Important!).
6.  **Deploy**: Click "Deploy!".

## Environment Variables (Secrets)

In the Streamlit Cloud dashboard for your app, go to **Settings** -> **Secrets** and add:

```toml
[secrets]
ADMIN_PASSWORD = "admin1234"
API_BASE_URL = "https://a-sense-project.vercel.app"
SUPABASE_URL = "your-supabase-url-here"
SUPABASE_KEY = "your-supabase-key-here"
TOSS_CLIENT_KEY = "test_ck_..."
PAYPAL_CLIENT_ID = "test"
```

*Note: If you don't set Supabase keys, it will run in Local/Mock mode.*
