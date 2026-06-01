from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime


st.set_page_config(page_title="DDoS Honeypot Dashboard", page_icon="🛡️", layout="wide")
st.title("📊 DDoS Honeypot Dashboard")

# 🔁 รีเฟรชทุก 5 วินาที
st_autorefresh(interval=5000, key="data_refresh")


# โหลดและแปลง log จาก honeypot_log.txt
log_file = "log_denfender\logs\honeypot_log.txt"
# Regex ใหม่ที่รองรับรูปแบบ [TIMESTAMP] [LEVEL] IP - METHOD - UA | DATA...
pattern = r"\[(.*?)\]\s+\[.*?\]\s+([\d\.]+).*?\| loss=([\d\.NA]+)% \| delay=([\d\.NA]+)ms \| tx=(\d+)B \| rx=(\d+)B \| tx_rate=(\d+)bps \| rx_rate=(\d+)bps"
# --- เริ่มต้นส่วนการอ่านไฟล์ ---
try:
    data = []
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                # ... (logic การดึงข้อมูลคงเดิม) ...
                timestamp_str = match.group(1)
                ip = match.group(2)
                loss_str = match.group(3)
                delay_str = match.group(4)
                tx = int(match.group(5))
                rx = int(match.group(6))
                tx_rate = int(match.group(7))
                rx_rate = int(match.group(8))

                loss = float(loss_str) if loss_str and loss_str != "NA" else None
                delay = float(delay_str) if delay_str and delay_str != "NA" else None

                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    continue

                data.append({
                    "timestamp": timestamp, "ip": ip, "loss": loss, "delay": delay,
                    "tx": tx, "rx": rx, "tx_rate": tx_rate, "rx_rate": rx_rate, "requests": 1
                })
    
    # สร้าง DataFrame หลังจากอ่านไฟล์เสร็จ
    df = pd.DataFrame(data)

# ปิดบล็อก try ด้วย except เพื่อดักจับ Error การอ่านไฟล์
except Exception as e:
    st.error(f"❌ ไม่สามารถอ่าน log จาก honeypot_log.txt ได้: {e}")
    st.stop()

# ✅ ตรวจสอบความว่างเปล่า (อยู่นอกบล็อก try-except หลักแล้ว)
if df.empty or 'ip' not in df.columns:
    st.warning("⚠️ ยังไม่มีข้อมูลที่วิเคราะห์ได้จาก log หรือรูปแบบ Regex ไม่ถูกต้อง")
    st.info(f"Path ที่ระบุ: {log_file}")
    st.stop() 

# --- หลังจากนี้ค่อยรันส่วนการแสดงผล Dashboard ---
total_ips = df["ip"].nunique()
# ... โค้ดที่เหลือ ...
total_requests = df["requests"].sum()
st.markdown(f"**📌 จำนวน IP ทั้งหมด:** `{total_ips}` | **📈 รวม requests:** `{total_requests}`")

# ⚠️ Flag IP
df["flag"] = df["requests"].apply(lambda x: "⚠️" if x > 100 else "")
with st.expander("📝 ดู log ดิบ"):
    st.dataframe(df.sort_values("timestamp", ascending=False))

# 📊 กราฟจำนวน Requests ต่อ IP
ip_count = df.groupby("ip")["requests"].sum().reset_index()
fig_ip = px.bar(ip_count, x="ip", y="requests", title="จำนวน Requests ต่อ IP", text="requests")
st.plotly_chart(fig_ip, use_container_width=True)

# ⏳ Timeline ของ Requests
time_count = df.groupby("timestamp")["requests"].sum().reset_index()
fig_time = px.line(time_count, x="timestamp", y="requests", title="Requests Timeline")
st.plotly_chart(fig_time, use_container_width=True)

# 📈 Mean Delay Timeline
if df["delay"].notna().any():
    st.subheader("📈 Mean Delay Timeline (10-sec Average)")
    delay_time = (
        df.dropna(subset=["delay"])
        .set_index("timestamp")
        .groupby(pd.Grouper(freq="10S"))["delay"]
        .mean()
        .reset_index()
    )
    fig_delay = px.line(delay_time, x="timestamp", y="delay", title="⏱️ Mean Delay (ms) [Every 10s]")
    fig_delay.update_layout(yaxis_title="Delay (ms)", plot_bgcolor="#fff")
    st.plotly_chart(fig_delay, use_container_width=True)

# 📉 Packet Loss Timeline
if df["loss"].notna().any():
    st.subheader("📉 Packet Loss Timeline (10-sec Average)")
    loss_time = (
        df.dropna(subset=["loss"])
        .set_index("timestamp")
        .groupby(pd.Grouper(freq="10S"))["loss"]
        .mean()
        .reset_index()
    )
    fig_loss = px.line(loss_time, x="timestamp", y="loss", title="📉 Packet Loss (%) [Every 10s]")
    fig_loss.update_layout(yaxis_title="Loss (%)", plot_bgcolor="#fff")
    st.plotly_chart(fig_loss, use_container_width=True)

# 📶 Bitrate Timeline (จาก honeypot_log)
if "tx_rate" in df.columns and df["tx_rate"].notna().any():
    st.subheader("📶 Bitrate Timeline")
    fig_bitrate = px.line(
        df,
        x="timestamp",
        y=["tx_rate", "rx_rate"],
        labels={"value": "Bitrate (bps)", "variable": "Type"},
        title="📶 Tx/Rx Bitrate Over Time"
    )
    fig_bitrate.update_layout(plot_bgcolor="#fff")
    st.plotly_chart(fig_bitrate, use_container_width=True)

# 📦 ปริมาณข้อมูลสะสม Tx/Rx
if "tx" in df.columns and df["tx"].notna().any():
    st.subheader("📦 Total Transferred Bytes")
    fig_bytes = px.line(
        df,
        x="timestamp",
        y=["tx", "rx"],
        labels={"value": "Bytes", "variable": "Type"},
        title="📦 Tx/Rx Bytes Over Time"
    )
    fig_bytes.update_layout(plot_bgcolor="#fff")
    st.plotly_chart(fig_bytes, use_container_width=True)

# 🔍 Log ราย IP
unique_ips = df["ip"].unique()
if len(unique_ips) > 0:
    selected_ip = st.selectbox("🔍 เลือก IP ดูรายละเอียด", unique_ips)
    df_filtered = df[df["ip"] == selected_ip].sort_values("timestamp", ascending=False)
    st.write(f"📄 Log ของ IP: `{selected_ip}`")
    st.dataframe(df_filtered)
else:
    st.info("ยังไม่มีข้อมูล IP ในระบบ")

# ==========================================
# 🛑 เพิ่มใหม่: ส่วนวิเคราะห์ข้อมูล TCP Dump (tcp.txt)
# ==========================================
st.markdown("---")
st.title("🛡️ TCP Packet Analysis (จาก tcpdump)")

tcp_log_file = r"log_denfender\logs\tcp.txt" # ปรับ path ให้ตรงกับโฟลเดอร์ของนาย
tcp_pattern = r"^(\d{2}:\d{2}:\d{2}\.\d+)\s+IP\s+([\d\.]+)\.\d+\s+>\s+([\d\.]+)\.\d+:\s+Flags\s+\[(.*?)\]"

try:
    tcp_data = []
    with open(tcp_log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = re.search(tcp_pattern, line)
            if match:
                time_str = match.group(1)
                src_ip = match.group(2)
                dst_ip = match.group(3)
                flags = match.group(4)
                
                # แปลง Flag ให้ดูง่ายขึ้น
                flag_name = "SYN (เชื่อมต่อ)" if "S" in flags else "ACK (ตอบรับ)" if "." in flags else "PUSH" if "P" in flags else "FIN/RST" if "F" in flags or "R" in flags else flags

                tcp_data.append({
                    "time_str": time_str,
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "flags": flag_name,
                    "count": 1
                })
                
    if tcp_data:
        df_tcp = pd.DataFrame(tcp_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # กราฟแสดงสัดส่วนของ TCP Flags (ถ้า SYN เยอะๆ คือโดน Flood แน่ๆ)
            st.subheader("🚩 TCP Flags Distribution")
            flag_count = df_tcp.groupby("flags")["count"].sum().reset_index()
            fig_flags = px.pie(flag_count, values="count", names="flags", hole=0.4, title="สัดส่วน TCP Flags (SYN vs ACK)")
            st.plotly_chart(fig_flags, use_container_width=True)
            
        with col2:
            # กราฟแสดง IP ที่ยิง Packet เข้ามามากที่สุดในระดับ TCP
            st.subheader("🎯 Top Source IPs (TCP Level)")
            tcp_ip_count = df_tcp.groupby("src_ip")["count"].sum().reset_index().sort_values(by="count", ascending=False).head(10)
            fig_tcp_ip = px.bar(tcp_ip_count, x="src_ip", y="count", title="IP ที่ส่ง Packet มากที่สุด (Top 10)")
            st.plotly_chart(fig_tcp_ip, use_container_width=True)

        with st.expander("📝 ดู Log ดิบจาก tcpdump"):
            st.dataframe(df_tcp)
    else:
        st.info("ยังไม่มีข้อมูลใน tcp.txt หรือรูปแบบ Log ไม่ตรง")

except FileNotFoundError:
    st.warning("⚠️ ไม่พบไฟล์ tcp.txt โปรดตรวจสอบให้แน่ใจว่า tcpdump ทำงานอยู่")
except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาดในการอ่าน tcp.txt: {e}")