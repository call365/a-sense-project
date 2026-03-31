import React from 'react';

export default function GlobalLandingPage() {
  // 버튼 클릭 시 이동할 타겟 URL
  const targetUrl = "https://sales.nextfintechai.com/";

  // 구조화된 데이터 (JSON-LD)
  const schemaData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "SoftwareApplication",
        "name": "Sale AI",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web, Cloud-based",
        "description": "AI-powered sales solution for e-commerce and shopping malls. Boost conversion rates with 24/7 AI sales agents that see what your customers see.",
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "USD",
          "description": "Free tier available for first 100 interactions"
        },
        "aggregateRating": {
          "@type": "AggregateRating",
          "ratingValue": "4.8",
          "ratingCount": "120"
        }
      },
      {
        "@type": "Organization",
        "name": "Sale AI",
        "url": "https://sales.nextfintechai.com/",
        "sameAs": [
          "https://www.linkedin.com/company/nextfintechai"
        ],
        "contactPoint": {
          "@type": "ContactPoint",
          "contactType": "customer support",
          "email": "support@nextfintechai.com"
        }
      }
    ]
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-200">
      {/* Schema Markup */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }} />

      {/* 1. Hero Section (Hook) */}
      <section className="relative pt-32 pb-20 px-6 max-w-5xl mx-auto text-center">
        {/* Background Blur Effect */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-gradient-to-b from-blue-100 to-transparent opacity-50 -z-10 blur-3xl"></div>
         
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6 leading-tight">
          Stop Wasting Ad Spend on <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
            Traffic That Doesn't Convert.
          </span>
        </h1>
        <p className="text-lg md:text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
          Physical stores have sales reps to close the deal. Why are you leaving your online store customers completely unattended?
        </p>
        <a 
          href={targetUrl}
          className="inline-block bg-slate-900 hover:bg-slate-800 text-white font-bold py-4 px-8 rounded-full text-lg shadow-xl transition-transform hover:-translate-y-1"
        >
          Install AI Sales Agent for Free
        </a>
      </section>

      {/* 2. Pain Points Section */}
      <section className="py-24 bg-white px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            High Traffic, Zero Sales? <br /> You're just feeding the ad platforms.
          </h2>
          <p className="text-slate-600 text-lg mb-12">
            A 90% bounce rate is killing your ROI. You can't afford 24/7 human customer service.
          </p>
          <div className="grid md:grid-cols-3 gap-8 text-left">
            <div className="p-6 bg-red-50 rounded-2xl border border-red-100">
              <div className="text-red-500 text-2xl mb-2">💸</div>
              <h3 className="font-bold mb-2">Skyrocketing CPC</h3>
              <p className="text-slate-600 text-sm">You pay $1 per click, only for the customer to leave your product page in 3 seconds.</p>
            </div>
            <div className="p-6 bg-red-50 rounded-2xl border border-red-100">
              <div className="text-red-500 text-2xl mb-2">😴</div>
              <h3 className="font-bold mb-2">Midnight Sales Drop</h3>
              <p className="text-slate-600 text-sm">When customers shop the most at 11 PM, there is no one there to push the sale.</p>
            </div>
            <div className="p-6 bg-red-50 rounded-2xl border border-red-100">
              <div className="text-red-500 text-2xl mb-2">🤖</div>
              <h3 className="font-bold mb-2">Dumb Chatbots</h3>
              <p className="text-slate-600 text-sm">Generic "How can I help you?" automated bots do not drive purchasing decisions.</p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Solution & Demo Section */}
      <section className="py-24 px-6 max-w-5xl mx-auto">
        <div className="bg-slate-900 rounded-3xl p-10 md:p-16 text-white text-center md:text-left flex flex-col md:flex-row items-center gap-12 shadow-2xl">
          <div className="flex-1">
            <h2 className="text-3xl md:text-4xl font-bold mb-6 leading-snug">
              Hire a relentless <br />
              <span className="text-blue-400">24/7 Sales Rep</span> for your store.
            </h2>
            <ul className="space-y-4 mb-8">
              <li className="flex items-center gap-3">
                <span className="bg-blue-500/20 text-blue-400 p-1 rounded-full text-sm">✓</span>
                Auto-detects product images and pricing
              </li>
              <li className="flex items-center gap-3">
                <span className="bg-blue-500/20 text-blue-400 p-1 rounded-full text-sm">✓</span>
                1-minute Shopify / Cafe24 installation
              </li>
              <li className="flex items-center gap-3">
                <span className="bg-blue-500/20 text-blue-400 p-1 rounded-full text-sm">✓</span>
                First 100 interactions are 100% Free
              </li>
            </ul>
          </div>
          {/* Virtual UI Demo */}
          <div className="flex-1 w-full bg-white rounded-xl p-4 shadow-lg text-slate-900 transform rotate-1 hover:rotate-0 transition-transform">
            <div className="flex items-center gap-2 mb-4 border-b pb-2">
              <div className="w-3 h-3 rounded-full bg-red-400"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
              <div className="w-3 h-3 rounded-full bg-green-400"></div>
              <span className="text-xs text-slate-400 font-mono ml-2">yourstore.com</span>
            </div>
            <div className="h-48 bg-slate-100 rounded-lg mb-4 flex items-center justify-center text-slate-400 text-sm font-medium">
              [Product Image: Linen Dress]
            </div>
            {/* AI Popup Simulation */}
            <div className="ml-auto w-4/5 bg-blue-50 border border-blue-100 rounded-2xl rounded-br-none p-4 shadow-sm relative">
              <p className="text-sm font-bold text-blue-900 mb-1">🤖 AI Sales Rep</p>
              <p className="text-sm text-slate-700 leading-snug">"Wow, this linen dress is perfect for a summer wedding! 👗 Order today, and it ships tomorrow. Should I add it to your cart?"</p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Case Study Section (Social Proof & Context) */}
      <section className="py-24 bg-slate-50 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Proven Results in <span className="text-blue-600">B2B & Wholesale</span>
          </h2>
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col md:flex-row">
            <div className="bg-slate-900 p-10 md:w-1/3 flex flex-col justify-center text-white">
              <h3 className="text-2xl font-bold mb-4">Automotive Parts Wholesaler</h3>
              <p className="text-slate-300 mb-6">B2B Wholesale Mall Case Study</p>
              <div className="space-y-6">
                <div>
                  <div className="text-4xl font-extrabold text-blue-400">98%</div>
                  <div className="text-sm text-slate-400">Response Rate (vs 20% human)</div>
                </div>
                <div>
                  <div className="text-4xl font-extrabold text-green-400">+15%</div>
                  <div className="text-sm text-slate-400">Sales Conversion Increase</div>
                </div>
              </div>
            </div>
            <div className="p-10 md:w-2/3 flex flex-col justify-center">
              <h4 className="text-xl font-bold mb-4 text-slate-800">"We couldn't handle the midnight inquiries."</h4>
              <p className="text-slate-600 mb-6 leading-relaxed">
                Before Sale AI, this automotive wholesaler missed 80% of inquiries coming in after hours. 
                With our <strong>Shopping Mall Revenue Increase AI</strong>, they now handle 100% of customer questions instantly, 
                turning night-time traffic into morning orders.
              </p>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center text-xl">🏢</div>
                <div>
                  <div className="font-bold text-slate-900">CEO, AutoParts Global</div>
                  <div className="text-sm text-slate-500">B2B SaaS Sales Solution User</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. FAQ Section (SEO Keywords) */}
      <section className="py-24 bg-white px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div className="border-b border-slate-200 pb-6">
              <h3 className="text-lg font-bold text-slate-900 mb-2">Is this a B2B SaaS sales solution?</h3>
              <p className="text-slate-600">
                Yes. Sale AI is a specialized <strong>B2B SaaS sales solution</strong> designed to automate lead qualification and customer engagement for both B2B and B2C e-commerce platforms.
              </p>
            </div>
            <div className="border-b border-slate-200 pb-6">
              <h3 className="text-lg font-bold text-slate-900 mb-2">How does it help with shopping mall revenue increase?</h3>
              <p className="text-slate-600">
                Our <strong>Shopping Mall Revenue Increase AI</strong> engages customers proactively, recovering abandoned carts and recommending products based on visual analysis, which directly boosts conversion rates (CVR).
              </p>
            </div>
            <div className="border-b border-slate-200 pb-6">
              <h3 className="text-lg font-bold text-slate-900 mb-2">Can I customize the AI sales agent?</h3>
              <p className="text-slate-600">
                Absolutely. You can train the agent on your specific catalog and sales scripts to ensure it acts as your best sales representative.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Sticky CTA (Bottom Bar) */}
      <div className="fixed bottom-0 left-0 w-full bg-white/80 backdrop-blur-md border-t border-slate-200 p-4 z-50">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-slate-800 font-medium hidden md:block">
            Stop losing customers. Start converting today. (No credit card required)
          </p>
          <a
            href={targetUrl}
            className="w-full sm:w-auto text-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-xl shadow-lg transition-colors"
          >
            Claim Your 100 Free Uses
          </a>
        </div>
      </div>
    </div>
  );
}
