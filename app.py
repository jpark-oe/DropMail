import streamlit as st
from PIL import Image
import io
import base64
import zipfile

# --- 1. 画像の最適化関数（画像データ「bytes」を返すように変更） ---
def get_optimized_image_bytes(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    img.thumbnail((990, 3000)) 
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True) 
    
    return buffer.getvalue() # 保存用のバイナリデータを返す

# --- 画像のURLパスを生成する関数（プレビュー用とダウンロード用を分ける） ---
def get_image_src(img_bytes, filename, is_preview):
    if is_preview:
        # プレビュー時はBase64エンコードして表示
        b64 = base64.b64encode(img_bytes).decode()
        return f"data:image/jpeg;base64,{b64}"
    else:
        # ダウンロード用HTMLでは img/フォルダ への相対パスを使用
        return f"img/{filename}"

# --- アプリの基本設定 ---
st.set_page_config(page_title="DropMail - メルマガビルダー", layout="wide")
st.title("💌 DropMail: メルマガビルダー")

# ==========================================
# ⚙️ セッションの初期化
# ==========================================
if 'layout_blocks' not in st.session_state:
    st.session_state['layout_blocks'] = []

def add_single_block(): st.session_state['layout_blocks'].append("single")
def add_double_block(): st.session_state['layout_blocks'].append("double")
def add_text_block(): st.session_state['layout_blocks'].append("text")
def clear_blocks(): st.session_state['layout_blocks'] = []

# ==========================================
# 🎨 全体デザイン設定（サイドバー）
# ==========================================
st.sidebar.header("🎨 全体デザイン設定")

font_choice = st.sidebar.radio("フォントスタイル", ["ゴシック体 (Gothic)", "明朝体 (Mincho)"])
if font_choice == "ゴシック体 (Gothic)":
    font_family = "'Helvetica Neue', Helvetica, Arial, 'Hiragino Sans', 'Meiryo', sans-serif"
else:
    font_family = "Georgia, 'Times New Roman', 'Hiragino Mincho ProN', 'Yu Mincho', serif"

st.sidebar.subheader("📝 フッター設定")
footer_text = st.sidebar.text_input("コピーライトテキスト", value="© 2026 DropMail. All rights reserved.")
footer_bg_color = st.sidebar.color_picker("フッターの背景色", value="#333333")
footer_text_color = st.sidebar.color_picker("フッターの文字色", value="#ffffff")

# ==========================================
# 🧩 ブロック構築 UI
# ==========================================
st.header("🧩 コンテンツを組み立てる")

col1, col2, col3, col4 = st.columns(4)
with col1: st.button("➕ 1列（画像）", on_click=add_single_block, use_container_width=True)
with col2: st.button("➕ 2列（画像）", on_click=add_double_block, use_container_width=True)
with col3: st.button("➕ テキストのみ", on_click=add_text_block, use_container_width=True)
with col4: st.button("🗑️ リセット", on_click=clear_blocks, use_container_width=True)

st.divider()

blocks_data = []
image_counter = 1 # 保存する画像ファイル名の連番カウンター

for i, b_type in enumerate(st.session_state['layout_blocks']):
    
    if b_type == "single":
        st.markdown(f"### 📍 ブロック {i+1} (1列・画像)")
        file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"], key=f"file_{i}")
        if file:
            c1, c2 = st.columns([1, 2])
            with c1: st.image(file, use_container_width=True)
            with c2:
                alt = st.text_input("代替テキスト (Alt)", key=f"alt_{i}")
                link = st.text_input("リンクURL", key=f"link_{i}")
                caption = st.text_input("画像下の注釈 (12px)", key=f"cap_{i}")
            
            img_bytes = get_optimized_image_bytes(file)
            filename = f"image_{image_counter:02d}.jpg" # image_01.jpg のように命名
            image_counter += 1
            
            blocks_data.append({
                "type": "single", "bytes": img_bytes, "filename": filename,
                "alt": alt, "link": link, "caption": caption
            })
            
    elif b_type == "double":
        st.markdown(f"### 📍 ブロック {i+1} (2列・左右分割画像)")
        c_left, c_right = st.columns(2)
        with c_left:
            file_l = st.file_uploader("左側の画像", type=["png", "jpg", "jpeg"], key=f"file_l_{i}")
            if file_l:
                st.image(file_l, use_container_width=True)
                alt_l = st.text_input("左 - 代替テキスト", key=f"alt_l_{i}")
                link_l = st.text_input("左 - リンクURL", key=f"link_l_{i}")
                cap_l = st.text_input("左 - 注釈", key=f"cap_l_{i}")
        with c_right:
            file_r = st.file_uploader("右側の画像", type=["png", "jpg", "jpeg"], key=f"file_r_{i}")
            if file_r:
                st.image(file_r, use_container_width=True)
                alt_r = st.text_input("右 - 代替テキスト", key=f"alt_r_{i}")
                link_r = st.text_input("右 - リンクURL", key=f"link_r_{i}")
                cap_r = st.text_input("右 - 注釈", key=f"cap_r_{i}")
                
        if file_l and file_r:
            bytes_l = get_optimized_image_bytes(file_l)
            filename_l = f"image_{image_counter:02d}.jpg"
            image_counter += 1
            
            bytes_r = get_optimized_image_bytes(file_r)
            filename_r = f"image_{image_counter:02d}.jpg"
            image_counter += 1
            
            blocks_data.append({
                "type": "double",
                "left": {"bytes": bytes_l, "filename": filename_l, "alt": alt_l, "link": link_l, "caption": cap_l},
                "right": {"bytes": bytes_r, "filename": filename_r, "alt": alt_r, "link": link_r, "caption": cap_r}
            })
            
    elif b_type == "text":
        st.markdown(f"### 📍 ブロック {i+1} (テキストエリア)")
        text_content = st.text_area("テキストを入力", key=f"text_only_{i}", height=100)
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            text_align = st.radio("配置", ["左揃え (left)", "中央揃え (center)", "右揃え (right)"], key=f"t_align_{i}", horizontal=True)
            align_val = "left" if "左" in text_align else "center" if "中央" in text_align else "right"
        with t_col2:
            bg_color = st.color_picker("背景色", value="#ffffff", key=f"t_bg_{i}")

        if text_content:
            blocks_data.append({"type": "text_only", "content": text_content, "align": align_val, "bg_color": bg_color})
            
    st.divider()

# ==========================================
# 🚀 HTML生成エンジン（プレビュー / 本番用 を動的に出力）
# ==========================================
def generate_html_code(blocks, is_preview=False):
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @media only screen and (max-width: 660px) {{
        .email-container {{ width: 100% !important; }}
        .fluid-img {{ width: 100% !important; height: auto !important; }}
        .stack-column {{ display: block !important; width: 100% !important; padding-bottom: 15px !important; }}
    }}
</style>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: {font_family};">
<table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f4f4f4;">
    <tr><td align="center">
        <table class="email-container" width="660" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; max-width: 660px;">
"""
    
    for block in blocks:
        if block["type"] == "single":
            # 📌 プレビューか本番(ZIP)かで画像のパスを切り替える
            src = get_image_src(block["bytes"], block["filename"], is_preview)
            img_tag = f'<img src="{src}" alt="{block["alt"]}" class="fluid-img" style="display: block; width: 100%; max-width: 100%; height: auto; border: 0;">'
            if block["link"]: img_tag = f'<a href="{block["link"]}" target="_blank">{img_tag}</a>'
            
            html += f"""<tr><td style="padding: 0; margin: 0;">{img_tag}</td></tr>"""
            if block["caption"]:
                html += f"""<tr><td style="padding: 5px 15px; font-size: 12px; color: #666666; text-align: left;">{block["caption"]}</td></tr>"""
        
        elif block["type"] == "double":
            src_l = get_image_src(block["left"]["bytes"], block["left"]["filename"], is_preview)
            img_l = f'<img src="{src_l}" alt="{block["left"]["alt"]}" class="fluid-img" style="display: block; width: 100%; height: auto; border: 0;">'
            if block["left"]["link"]: img_l = f'<a href="{block["left"]["link"]}" target="_blank">{img_l}</a>'
            cap_l = f'<div style="padding: 5px 0; font-size: 12px; color: #666666;">{block["left"]["caption"]}</div>' if block["left"]["caption"] else ""

            src_r = get_image_src(block["right"]["bytes"], block["right"]["filename"], is_preview)
            img_r = f'<img src="{src_r}" alt="{block["right"]["alt"]}" class="fluid-img" style="display: block; width: 100%; height: auto; border: 0;">'
            if block["right"]["link"]: img_r = f'<a href="{block["right"]["link"]}" target="_blank">{img_r}</a>'
            cap_r = f'<div style="padding: 5px 0; font-size: 12px; color: #666666;">{block["right"]["caption"]}</div>' if block["right"]["caption"] else ""

            html += f"""
            <tr><td style="padding: 10px 15px;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0"><tr>
                    <th class="stack-column" width="48%" align="center" valign="top" style="font-weight: normal; padding-right: 2%;">{img_l}{cap_l}</th>
                    <th class="stack-column" width="48%" align="center" valign="top" style="font-weight: normal; padding-left: 2%;">{img_r}{cap_r}</th>
                </tr></table>
            </td></tr>
            """
        
        elif block["type"] == "text_only":
            formatted_text = block["content"].replace('\n', '<br>')
            html += f"""
            <tr><td style="background-color: {block["bg_color"]}; padding: 30px 20px;">
                <div style="font-size: 16px; color: #333333; line-height: 1.6; text-align: {block["align"]};">{formatted_text}</div>
            </td></tr>
            """

    html += f"""
        </table>
    </td></tr>
    <tr><td align="center" style="background-color: {footer_bg_color}; padding: 20px 10px;">
        <table width="660" border="0" cellspacing="0" cellpadding="0" style="max-width: 660px;">
            <tr><td align="center" style="font-size: 12px; color: {footer_text_color}; line-height: 1.5;">{footer_text}</td></tr>
        </table>
    </td></tr>
</table></body></html>
"""
    return html

# ==========================================
# 📦 ZIP作成 & プレビュー表示
# ==========================================
if st.button("🚀 メルマガ一式（ZIP）を生成する", type="primary", use_container_width=True):
    if not blocks_data:
        st.warning("コンテンツがありません。")
    else:
        # 1. ダウンロード用（相対パス）のHTMLを生成
        download_html = generate_html_code(blocks_data, is_preview=False)
        
        # 2. メモリ上でZIPファイルを作成
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # 📄 index.html を追加
            zip_file.writestr("index.html", download_html)
            
            # 🖼️ img/ フォルダの中に画像を追加
            for block in blocks_data:
                if block["type"] == "single":
                    zip_file.writestr(f"img/{block['filename']}", block["bytes"])
                elif block["type"] == "double":
                    zip_file.writestr(f"img/{block['left']['filename']}", block["left"]["bytes"])
                    zip_file.writestr(f"img/{block['right']['filename']}", block["right"]["bytes"])
        
        st.success("🎉 ZIPファイルの準備ができました！")
        
        # 📌 ZIPダウンロードボタン
        st.download_button(
            label="📥 ZIPファイル (index.html + imgフォルダ) をダウンロード",
            data=zip_buffer.getvalue(),
            file_name="dropmail_package.zip",
            mime="application/zip"
        )
        
        # 3. プレビュー用（Base64）のHTMLを生成して画面に表示
        st.header("👁️ プレビュー")
        preview_html = generate_html_code(blocks_data, is_preview=True)
        st.components.v1.html(preview_html, height=800, scrolling=True)