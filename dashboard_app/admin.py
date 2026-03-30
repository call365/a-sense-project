import os
from typing import List, Dict, Any

import pandas as pd
import streamlit as st
from supabase import create_client, Client

# --- 1. Supabase 연동 세팅 ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "사장님의_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "사장님의_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SUPABASE_URL / SUPABASE_KEY 설정이 필요합니다.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def _get_payout_table_name() -> str:
    """withdrawals 우선 사용, 없으면 payout_requests 폴백"""
    try:
        supabase.table("withdrawals").select("id").limit(1).execute()
        return "withdrawals"
    except Exception:
        return "payout_requests"


def _normalize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []
    for row in rows:
        normalized.append(
            {
                "id": row.get("id"),
                "publisher_id": row.get("publisher_id", "-"),
                "paypal_email": row.get("paypal_email", "(없음)"),
                "amount": int(row.get("amount", 0) or 0),
                "status": row.get("status", "pending"),
                "requested_at": row.get("requested_at") or row.get("created_at") or "-",
            }
        )
    return normalized


# --- 2. 화면 기본 설정 ---
st.set_page_config(page_title="A-Sense Admin", page_icon="👑", layout="wide")
st.title("👑 A-Sense 최고 관리자 센터")
st.markdown("전 세계 파트너들의 정산 요청을 승인하고 수익금을 관리하는 중앙 통제실입니다.")

table_name = _get_payout_table_name()
st.caption(f"연동 테이블: {table_name}")

# 탭(Tab)으로 메뉴 나누기
tab1, tab2 = st.tabs(["🚨 정산 대기열 (Pending)", "✅ 송금 완료 내역 (Completed)"])


# --- 3. 정산 대기열 탭 (승인 처리) ---
with tab1:
    st.subheader("처리 대기 중인 정산 요청")

    try:
        pending_res = (
            supabase.table(table_name)
            .select("*")
            .eq("status", "pending")
            .order("requested_at", desc=False)
            .execute()
        )
        pending_data = _normalize_rows(pending_res.data or [])
    except Exception as e:
        st.error(f"대기열 조회 실패: {e}")
        pending_data = []

    if not pending_data:
        st.success("🎉 현재 밀린 정산 요청이 없습니다. 훌륭합니다!")
    else:
        st.warning(f"현재 {len(pending_data)}건의 정산 요청이 대기 중입니다.")

        for req in pending_data:
            with st.container():
                st.markdown("---")
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

                with col1:
                    st.caption("요청 일시")
                    st.write(str(req["requested_at"])[:10])

                with col2:
                    st.caption("송금할 PayPal 계정")
                    st.code(req["paypal_email"])

                with col3:
                    st.caption("요청 금액")
                    st.write(f"**₩ {req['amount']:,}**")

                with col4:
                    st.caption("승인 액션")
                    if st.button("✅ 입금 완료", key=f"btn_{req['id']}", use_container_width=True):
                        try:
                            (
                                supabase.table(table_name)
                                .update({"status": "completed"})
                                .eq("id", req["id"])
                                .execute()
                            )
                            st.success("승인 완료! 내역이 이동되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"처리 중 오류 발생: {e}")


# --- 4. 송금 완료 내역 탭 (과거 기록) ---
with tab2:
    st.subheader("과거 정산 완료 내역")

    try:
        completed_res = (
            supabase.table(table_name)
            .select("*")
            .eq("status", "completed")
            .order("requested_at", desc=True)
            .limit(50)
            .execute()
        )
        completed_data = _normalize_rows(completed_res.data or [])
    except Exception as e:
        st.error(f"완료 내역 조회 실패: {e}")
        completed_data = []

    if not completed_data:
        st.info("아직 완료된 정산 내역이 없습니다.")
    else:
        df = pd.DataFrame(completed_data)
        df = df[["requested_at", "paypal_email", "amount", "publisher_id"]]
        df.columns = ["요청 일시", "페이팔 계정", "송금액(₩)", "매체사 ID"]
        st.dataframe(df, use_container_width=True, hide_index=True)
