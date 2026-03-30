'use client';

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Copy, Wallet, ShieldCheck, Globe, CheckCircle, AlertCircle, Loader2, Send } from 'lucide-react';

export default function DashboardHome() {
  // DB에서 가져올 매체사 데이터 (MVP 목업)
  const stats = {
    todayImpressions: '820',
    todayClicks: '45',
  };

  const [balance, setBalance] = useState(65000);
  const [paypalEmail, setPaypalEmail] = useState('');
  const [isRequesting, setIsRequesting] = useState(false);
  const [payoutStatus, setPayoutStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const MINIMUM_PAYOUT = 50000;

  const myApiKey = 'sk_live_9a8b7c6d5e4f3g2h1i0j';
  const [copied, setCopied] = useState(false);
  const [domain, setDomain] = useState('https://my-ai-tarot.com');
  const [isSaved, setIsSaved] = useState(false);

  const handlePayoutRequest = async (e: FormEvent) => {
    e.preventDefault();
    if (balance < MINIMUM_PAYOUT || isRequesting || payoutStatus === 'success') return;
    if (!paypalEmail.trim()) return;

    setIsRequesting(true);
    setPayoutStatus('idle');

    try {
      const sessionToken = localStorage.getItem('asense_session_token') || myApiKey;
      const response = await fetch('/api/v1/withdrawals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${sessionToken}`,
        },
        body: JSON.stringify({ amount: balance, paypal_email: paypalEmail.trim() }),
      });

      if (response.ok) {
        setBalance(0);
        setPayoutStatus('success');
      } else {
        const errorData = await response.json();
        alert(`정산 요청 실패: ${errorData?.detail || '알 수 없는 오류'}`);
        setPayoutStatus('error');
      }
    } catch (error) {
      console.error(error);
      setPayoutStatus('error');
    } finally {
      setIsRequesting(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(myApiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveDomain = async (e: FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch('/api/v1/publisher/domain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${myApiKey}`,
        },
        body: JSON.stringify({ domain }),
      });

      if (!response.ok) {
        throw new Error('도메인 저장 실패');
      }

      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (error) {
      console.error(error);
      alert('도메인 저장 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <header>
        <h2 className="text-3xl font-bold text-slate-900">대시보드</h2>
        <p className="text-slate-500 mt-2">정당한 트래픽으로 안전하게 수익을 창출하세요.</p>
      </header>

      <section className="bg-slate-900 p-8 rounded-3xl shadow-sm text-white flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600 rounded-full blur-3xl opacity-20 -mr-10 -mt-10 pointer-events-none" />

        <div>
          <div className="flex items-center gap-3 mb-2 opacity-80">
            <Wallet size={20} /> 출금 가능 잔액
          </div>
          <div className="text-4xl font-extrabold mb-2">₩ {balance.toLocaleString()}</div>
          <p className="text-sm text-slate-400">최소 정산 금액: ₩ {MINIMUM_PAYOUT.toLocaleString()}</p>
        </div>

        <form onSubmit={handlePayoutRequest} className="w-full md:w-auto flex flex-col gap-3 z-10 md:min-w-[360px]">
          {payoutStatus !== 'success' && (
            <input
              type="email"
              placeholder="PayPal 이메일 주소 입력"
              value={paypalEmail}
              onChange={(e) => setPaypalEmail(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
            />
          )}

          <button
            type="submit"
            disabled={balance < MINIMUM_PAYOUT || isRequesting || payoutStatus === 'success' || !paypalEmail.trim()}
            className={`px-8 py-3 rounded-xl font-bold transition flex items-center justify-center gap-2 ${
              balance >= MINIMUM_PAYOUT && paypalEmail.trim() && payoutStatus !== 'success'
                ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            }`}
          >
            {isRequesting && <Loader2 size={18} className="animate-spin" />}
            {payoutStatus === 'success' && <CheckCircle size={18} />}
            {payoutStatus === 'idle' && !isRequesting && <Send size={18} />}
            {payoutStatus === 'success' ? '신청 완료' : '페이팔로 정산 받기'}
          </button>

          {payoutStatus === 'success' && (
            <p className="text-green-400 text-sm mt-2 text-right">월말에 검수 후 페이팔로 송금됩니다.</p>
          )}
          {payoutStatus === 'error' && (
            <p className="text-red-400 text-sm mt-2 text-right flex items-center justify-end gap-1">
              <AlertCircle size={14} /> 요청 처리 중 문제가 발생했습니다.
            </p>
          )}
        </form>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center gap-3 mb-2 opacity-80">
            <Wallet size={18} /> 남은 잔액
          </div>
          <div className="text-2xl font-bold text-slate-900">₩ {balance.toLocaleString()}</div>
          <p className="text-xs text-slate-400 mt-2">※ 50,000원 이상부터 정산 신청 가능</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 mb-2">오늘 노출수</div>
          <div className="text-2xl font-bold text-slate-900">{stats.todayImpressions}</div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="text-slate-500 mb-2">오늘 클릭수</div>
          <div className="text-2xl font-bold text-slate-900">{stats.todayClicks}</div>
        </div>
      </div>

      <section className="bg-white p-8 rounded-3xl border border-blue-100 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 left-0 w-2 h-full bg-blue-500" />

        <div className="flex items-center gap-2 mb-6">
          <ShieldCheck className="text-blue-600" size={24} />
          <h3 className="text-xl font-bold text-slate-900">API 보안 및 연동 설정</h3>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">보호받을 챗봇 URL (화이트리스트)</label>
              <p className="text-xs text-slate-500 mb-3">
                등록된 도메인에서 발생한 트래픽만 수익으로 인정됩니다. 해킹으로 인한 API 키 도용을 막아줍니다.
              </p>
            </div>
            <form onSubmit={handleSaveDomain} className="flex gap-2">
              <div className="relative flex-1">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="url"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  placeholder="https://your-bot-domain.com"
                  className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none"
                  required
                />
              </div>
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold transition flex items-center gap-2"
              >
                {isSaved ? <CheckCircle size={18} /> : '저장'}
              </button>
            </form>
          </div>

          <div className="space-y-4">
            <label className="block text-sm font-bold text-slate-700 mb-2">내 API Key</label>
            <p className="text-xs text-slate-500 mb-3">서버 간 통신(S2S) 시 헤더에 포함해주세요. 절대 외부에 노출하지 마세요.</p>
            <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200">
              <code className="flex-1 text-slate-700 font-mono text-sm">{myApiKey}</code>
              <button
                onClick={copyToClipboard}
                className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2"
              >
                <Copy size={16} /> {copied ? '복사됨' : '복사'}
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
