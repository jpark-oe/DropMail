import streamlit as st
from PIL import Image
import io
import base64
import zipfile

# --- 1. 画像最適化 ---
def get_optimized_image_bytes(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    img.thumbnail((990, 3000)) 
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True) 
    return buffer.getvalue()

def get_image_src(img_bytes, filename, is_preview):
    if is_preview:
        b64 = base64.b64encode(img_bytes).decode()
        return f"data:image/jpeg;base64,{b64}"
    else:
        return f"img/{filename}"

# --- アプリ基本設定 ---
st.set_page_config(page_title="DropMail - メルマガビルダー", layout="wide")
st.title("DropMail: プレミアム・メルマガビルダー")
st.write("Appleスタイルの洗練されたデザインシステムに基づき、コンテンツを構築します。")

# ==========================================
# ⚙️ セッション初期化
# ==========================================
if 'layout_blocks' not in st.session_state:
    st.session_state['layout_blocks'] = []

def add_single_block(): st.session_state['layout_blocks'].append("single")
def add_double_block(): st.session_state['layout_blocks'].append("double")
def add_text_block(): st.session_state['layout_blocks'].append("text")
def clear_blocks(): st.session_state['layout_blocks'] = []

# ==========================================
# ⚙️ 全体設定（サイドバーからメイン画面上部へ移動）
# ==========================================
with st.expander("共通設定 (フッター情報など)", expanded=False):
    footer_text = st.text_input("コピーライトテキスト", value="© 2026 DropMail. All rights reserved.")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        # Appleのガイドラインに基づくダークグレー
        footer_bg_color = st.color_picker("フッター背景色", value="#1d1d1f")
    with col_f2:
        footer_text_color = st.color_picker("フッター文字色", value="#f5f5f7")

st.divider()

# ==========================================
# 🧩 ブロック構築 UI
# ==========================================
col1, col2, col3, col4 = st.columns(4)
with col1: st.button("＋ 画像 (1列)", on_click=add_single_block, use_container_width=True)
with col2: st.button("＋ 画像 (2列)", on_click=add_double_block, use_container_width=True)
with col3: st.button("＋ テキスト", on_click=add_text_block, use_container_width=True)
with col4: st.button("リセット", on_click=clear_blocks, use_container_width=True)

st.divider()

blocks_data = []
image_counter = 1

for i, b_type in enumerate(st.session_state['layout_blocks']):
    
    # -------------------------
    # 📸 1列画像ブロック
    # -------------------------
    if b_type == "single":
        st.markdown(f"**ブロック {i+1} : 画像 (1列)**")
        
        # 背景色の選択（Appleのガイドラインに基づく）
        bg_color = st.radio("セクション背景", ["ライト (#f5f5f7)", "ダーク (#000000)", "ホワイト (#ffffff)"], key=f"bg_{i}", horizontal=True)
        bg_val = "#f5f5f7" if "ライト" in bg_color else "#000000" if "ダーク" in bg_color else "#ffffff"
        text_color = "#ffffff" if bg_val == "#000000" else "#1d1d1f"
        
        file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"], key=f"file_{i}")
        if file:
            c1, c2 = st.columns([1, 2])
            with c1: st.image(file, use_container_width=True)
            with c2:
                alt = st.text_input("代替テキスト (Alt)", key=f"alt_{i}")
                link = st.text_input("リンクURL (画像クリック時)", key=f"link_{i}")
                
                c2_1, c2_2 = st.columns(2)
                with c2_1:
                    # Apple特有のピル型ボタン設定
                    btn_text = st.text_input("ボタンテキスト (オプション)", key=f"btn_{i}", placeholder="例: Learn more")
                with c2_2:
                    btn_link = st.text_input("ボタンリンクURL", key=f"btn_link_{i}")

            img_bytes = get_optimized_image_bytes(file)
            filename = f"image_{image_counter:02d}.jpg"
            image_counter += 1
            
            blocks_data.append({
                "type": "single", "bytes": img_bytes, "filename": filename,
                "alt": alt, "link": link, "bg_color": bg_val, "text_color": text_color,
                "btn_text": btn_text, "btn_link": btn_link
            })
            
    # -------------------------
    # 📸 2列画像ブロック
    # -------------------------
    elif b_type == "double":
        st.markdown(f"**ブロック {i+1} : 画像 (2列)**")
        bg_color = st.radio("セクション背景", ["ライト (#f5f5f7)", "ダーク (#000000)", "ホワイト (#ffffff)"], key=f"bg_{i}", horizontal=True)
        bg_val = "#f5f5f7" if "ライト" in bg_color else "#000000" if "ダーク" in bg_color else "#ffffff"

        c_left, c_right = st.columns(2)
        with c_left:
            file_l = st.file_uploader("左側の画像", type=["png", "jpg", "jpeg"], key=f"file_l_{i}")
            if file_l:
                alt_l = st.text_input("左 - Alt", key=f"alt_l_{i}")
                link_l = st.text_input("左 - リンク", key=f"link_l_{i}")
        with c_right:
            file_r = st.file_uploader("右側の画像", type=["png", "jpg", "jpeg"], key=f"file_r_{i}")
            if file_r:
                alt_r = st.text_input("右 - Alt", key=f"alt_r_{i}")
                link_r = st.text_input("右 - リンク", key=f"link_r_{i}")
                
        if file_l and file_r:
            bytes_l = get_optimized_image_bytes(file_l)
            filename_l = f"image_{image_counter:02d}.jpg"
            image_counter += 1
            bytes_r = get_optimized_image_bytes(file_r)
            filename_r = f"image_{image_counter:02d}.jpg"
            image_counter += 1
            
            blocks_data.append({
                "type": "double", "bg_color": bg_val,
                "left": {"bytes": bytes_l, "filename": filename_l, "alt": alt_l, "link": link_l},
                "right": {"bytes": bytes_r, "filename": filename_r, "alt": alt_r, "link": link_r}
            })
            
    # -------------------------
    # 📝 テキストブロック（サイドバーから設定を移動）
    # -------------------------
    elif b_type == "text":
        st.markdown(f"**ブロック {i+1} : テキスト**")
        
        # 📌 全ての設定をテキスト追加枠の「中」に集約しました
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            text_type = st.radio("テキスト階層", ["見出し (Display)", "本文 (Body)"], key=f"t_type_{i}", horizontal=True)
            text_align = st.radio("配置", ["左", "中央", "右"], key=f"t_align_{i}", horizontal=True)
            align_val = "left" if "左" in text_align else "center" if "中央" in text_align else "right"
        with t_col2:
            bg_color = st.radio("背景色", ["ライト (#f5f5f7)", "ダーク (#000000)", "ホワイト (#ffffff)"], key=f"t_bg_{i}")
            bg_val = "#f5f5f7" if "ライト" in bg_color else "#000000" if "ダーク" in bg_color else "#ffffff"
            text_color = "#ffffff" if bg_val == "#000000" else "#1d1d1f"

        text_content = st.text_area("テキストを入力", key=f"text_only_{i}", height=120)

        if text_content:
            blocks_data.append({
                "type": "text_only", "content": text_content, "align": align_val, 
                "bg_color": bg_val, "text_color": text_color, "text_type": text_type
            })
            
    st.divider()

# ==========================================
# 🚀 HTML生成エンジン (Apple Design System 適用)
# ==========================================
def generate_html_code(blocks, is_preview=False):
    # Appleのタイポグラフィ設定 (SF Proフォントファミリ)
    font_stack = "SF Pro Icons, Helvetica Neue, Helvetica, Arial, sans-serif"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    /* Appleベースのスタイルリセットと基本設定 */
    body {{
        margin: 0; padding: 0;
        background-color: #f5f5f7;
        -webkit-font-smoothing: antialiased;
    }}
    .email-container {{
        width: 100%; max-width: 660px; margin: 0 auto;
        background-color: #ffffff;
    }}
    .fluid-img {{ width: 100% !important; height: auto !important; display: block; border: 0; }}
    
    /* レスポンシブ対応 */
    @media only screen and (max-width: 660px) {{
        .stack-column {{ display: block !important; width: 100% !important; padding: 0 0 15px 0 !important; }}
    }}
</style>
</head>
<body>
<table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f5f5f7;">
    <tr><td align="center">
        <table class="email-container" border="0" cellspacing="0" cellpadding="0">
"""
    
    for block in blocks:
        bg = block.get("bg_color", "#ffffff")
        
        if block["type"] == "single":
            src = get_image_src(block["bytes"], block["filename"], is_preview)
            img_tag = f'<img src="{src}" alt="{block["alt"]}" class="fluid-img">'
            if block["link"]: img_tag = f'<a href="{block["link"]}" target="_blank">{img_tag}</a>'
            
            html += f'<tr><td style="background-color: {bg}; padding: 0; margin: 0;">{img_tag}'
            
            # 📌 Apple Blue (#0071e3) のピル型(980px) CTAボタン
            if block.get("btn_text") and block.get("btn_link"):
                html += f"""
                <div style="text-align: center; padding: 24px 0 40px 0;">
                    <a href="{block["btn_link"]}" target="_blank" style="display: inline-block; background-color: #0071e3; color: #ffffff; padding: 8px 15px; border-radius: 980px; text-decoration: none; font-family: {font_stack}; font-size: 17px; font-weight: 400;">
                        {block["btn_text"]}
                    </a>
                </div>
                """
            html += '</td></tr>'
        
        elif block["type"] == "double":
            src_l = get_image_src(block["left"]["bytes"], block["left"]["filename"], is_preview)
            img_l = f'<img src="{src_l}" alt="{block["left"]["alt"]}" class="fluid-img">'
            if block["left"]["link"]: img_l = f'<a href="{block["left"]["link"]}" target="_blank">{img_l}</a>'

            src_r = get_image_src(block["right"]["bytes"], block["right"]["filename"], is_preview)
            img_r = f'<img src="{src_r}" alt="{block["right"]["alt"]}" class="fluid-img">'
            if block["right"]["link"]: img_r = f'<a href="{block["right"]["link"]}" target="_blank">{img_r}</a>'

            html += f"""
            <tr><td style="background-color: {bg}; padding: 20px 15px;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0"><tr>
                    <th class="stack-column" width="48%" align="center" valign="top" style="font-weight: normal; padding-right: 2%;">{img_l}</th>
                    <th class="stack-column" width="48%" align="center" valign="top" style="font-weight: normal; padding-left: 2%;">{img_r}</th>
                </tr></table>
            </td></tr>
            """
        
        elif block["type"] == "text_only":
            formatted_text = block["content"].replace('\n', '<br>')
            
            # 📌 Appleのタイポグラフィ階層設定
            if "見出し" in block["text_type"]:
                # Display: 28px, タイトな行間(1.14), マイナスの字送り
                font_style = f"font-size: 28px; font-weight: 600; line-height: 1.14; letter-spacing: -0.28px;"
            else:
                # Body: 17px, ゆとりのある行間(1.47), わずかなマイナス字送り
                font_style = f"font-size: 17px; font-weight: 400; line-height: 1.47; letter-spacing: -0.374px;"

            html += f"""
            <tr><td style="background-color: {bg}; padding: 40px 30px;">
                <div style="font-family: {font_stack}; color: {block["text_color"]}; text-align: {block["align"]}; {font_style}">
                    {formatted_text}
                </div>
            </td></tr>
            """

    # フッター (Apple風のマイクロテキスト)
    html += f"""
        </table>
    </td></tr>
    <tr><td align="center" style="background-color: {footer_bg_color}; padding: 30px 15px;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 660px;">
            <tr><td align="center" style="font-family: {font_stack}; font-size: 12px; font-weight: 400; letter-spacing: -0.12px; color: {footer_text_color}; line-height: 1.33;">
                {footer_text}
            </td></tr>
        </table>
    </td></tr>
</table></body></html>
"""
    return html

# ==========================================
# 📦 ダウンロード & プレビュー
# ==========================================
if st.button("生成 & ダウンロード準備", type="primary", use_container_width=True):
    if not blocks_data:
        st.warning("コンテンツを追加してください。")
    else:
        download_html = generate_html_code(blocks_data, is_preview=False)
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("index.html", download_html)
            for block in blocks_data:
                if block["type"] == "single":
                    zip_file.writestr(f"img/{block['filename']}", block["bytes"])
                elif block["type"] == "double":
                    zip_file.writestr(f"img/{block['left']['filename']}", block["left"]["bytes"])
                    zip_file.writestr(f"img/{block['right']['filename']}", block["right"]["bytes"])
        
        st.success("ZIPファイルの準備が完了しました。")
        st.download_button(
            label="ZIPファイルをダウンロード (index.html + imgフォルダ)",
            data=zip_buffer.getvalue(),
            file_name="apple_style_mail.zip",
            mime="application/zip"
        )
        
        st.markdown("### プレビュー")
        preview_html = generate_html_code(blocks_data, is_preview=True)
        st.components.v1.html(preview_html, height=800, scrolling=True)