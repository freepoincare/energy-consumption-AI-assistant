# Environment variables for Vercel 
  
  For Vercel, because your frontend is a pure static client (plain HTML, CSS, and vanilla JavaScript without a Node.js SSR build step like Next.js):
 
  ## 1. Does Vercel Need Any Sensitive Environment Variables?

  No.

  * Do NOT put OPENAI_API_KEY into Vercel.
  * Do NOT put FIREBASE_SERVICE_ACCOUNT_JSON into Vercel.

  All secrets must stay strictly on Render (the backend).

  ## 2. How the Frontend Connects to Render

  In vanilla client-side JavaScript, browser code cannot read server-side Vercel environment variables directly at runtime unless injected by a build tool.

  Instead, the frontend gets the backend URL in one of two clean ways:

  ### Option A (Recommended & Direct): Edit frontend/config.js

  Simply open config.js and set your Render URL:

    // frontend/config.js
    window.API_BASE_URL = 'https://<your-backend-name>.onrender.com';

  (When empty or running locally on port 8000, it automatically defaults to window.location.origin).

  ### Option B (If you want to define it in Vercel)

  If you prefer setting it in the Vercel Dashboard under Settings → Environment Variables:

  * Key: API_BASE_URL (or NEXT_PUBLIC_API_BASE_URL / RENDER_BACKEND_URL)
  * Value: https://<your-backend-name>.onrender.com

  Note:
  - If you set it in Vercel without a bundler (Webpack/Vite), static HTML/JS files won't automatically read process environment variables. Therefore, Option A (setting window.API_BASE_URL in config.js) is the simplest and most reliable pattern for vanilla static sites on Vercel.

  ## 3. Summary of Where Variables Belong

   Variable                                                                          | Where to save it?
  -----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------
   OPENAI_API_KEY                                                                    | Render only (Backend)
   FIREBASE_SERVICE_ACCOUNT_JSON                                                     | Render only (Backend)
   ALLOWED_ORIGINS                                                                   | Render only (Set to your Vercel URL, e.g. https://your-app.vercel.app)
   ENVIRONMENT                                                                       | Render only (production)
   Backend URL                                                                       | In config.js (window.API_BASE_URL = "https://your-backend.onrender.com")
