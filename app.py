import streamlit as st
from PIL import Image
import io
import base64

# --- 1. 画像の最適化関数（990px対応・画質85%） ---
def optimize_image_to_base64(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    img.thumbnail((990, 3000)) 
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True) 
    
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

# --- アプリの基本設定 ---
st.set_page_config(page_title="DropMail - メルマガビルダー", layout="wide")
st.title("💌 DropMail: メルマガビルダー")

# ==========================================
# ⚙️ セッションの初期化（動的にブロックを追加するため）
# ==========================================
# ユーザーが追加したレイアウトの順番を記憶します
if 'layout_blocks' not in st.session_state:
    st.session_state['layout_blocks'] = []

def add_single_block():
    st.session_state['layout_blocks'].append("single")

def add_double_block():
    st.session_state['layout_blocks'].append("double")
    
def clear_blocks():
    st.session_state['layout_blocks'] = []

# ==========================================
# 🎨 全体デザイン設定（サイドバー）
# ==========================================
st.sidebar.header("🎨 全体デザイン設定")

font_choice = st.sidebar.radio("フォントスタイル", ["ゴシック体 (Gothic)", "明朝体 (Mincho)"])
if font_choice == "ゴシック体 (Gothic)":
    font_family = "'Helvetica Neue', Helvetica, Arial, 'Hiragino Sans', 'Meiryo', sans-serif"
else:
    font_family = "Georgia, 'Times New Roman', 'Hiragino Mincho ProN', 'Yu Mincho', serif"

st.sidebar.subheader("📝 フッター (Copyright) 設定")
footer_text = st.sidebar.text_input("コピーライトテキスト", value="© 2026 DropMail. All rights reserved.")
footer_bg_color = st.sidebar.color_picker("フッターの背景色（帯の色）", value="#333333")
footer_text_color = st.sidebar.color_picker("フッターの文字色", value="#ffffff")

# ==========================================
# 🧩 ブロック構築 UI（好きなタイミングで追加！）
# ==========================================
st.header("🧩 コンテンツを組み立てる")
st.write("下のボタンを押して、必要なレイアウトを追加してください！")

# レイアウト追加ボタン
col1, col2, col3 = st.columns(3)
with col1:
    st.button("➕ 1列（全幅）ブロックを追加", on_click=add_single_block, use_container_width=True)
with col2:
    st.button("➕ 2列（左右分割）ブロックを追加", on_click=add_double_block, use_container_width=True)
with col3:
    st.button("🗑️ ブロックをすべてリセット", on_click=clear_blocks, use_container_width=True)

st.divider()

blocks_data = []

# 追加されたブロックの数だけ入力欄を表示
for i, b_type in enumerate(st.session_state['layout_blocks']):
    st.markdown(f"### 📍 ブロック {i+1} ({'1列' if b_type == 'single' else '2列'})")
    
    if b_type == "single":
        file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"], key=f"file_{i}")
        if file:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(file, use_container_width=True)
            with c2:
                alt = st.text_input("代替テキスト (Alt)", key=f"alt_{i}")
                link = st.text_input("リンクURL", key=f"link_{i}")
                caption = st.text_input("画像下の注釈 (12px)", key=f"cap_{i}")
                text = st.text_area("通常テキスト (オプション)", key=f"text_{i}")
            
            blocks_data.append({
                "type": "single",
                "src": optimize_image_to_base64(file),
                "alt": alt, "link": link, "caption": caption, "text": text
            })
            
    else:
        # 2列（左右分割）の場合
        c_left, c_right = st.columns(2)
        with c_left:
            st.write("◀️ 左側のコンテンツ")
            file_l = st.file_uploader("左側の画像", type=["png", "jpg", "jpeg"], key=f"file_l_{i}")
            if file_l:
                st.image(file_l, use_container_width=True)
                alt_l = st.text_input("左 - 代替テキスト", key=f"alt_l_{i}")
                link_l = st.text_input("左 - リンクURL", key=f"link_l_{i}")
                cap_l = st.text_input("左 - 注釈 (12px)", key=f"cap_l_{i}")
        with c_right:
            st.write("▶️ 右側のコンテンツ")
            file_r = st.file_uploader("右側の画像", type=["png", "jpg", "jpeg"], key=f"file_r_{i}")
            if file_r:
                st.image(file_r, use_container_width=True)
                alt_r = st.text_input("右 - 代替テキスト", key=f"alt_r_{i}")
                link_r = st.text_input("右 - リンクURL", key=f"link_r_{i}")
                cap_r = st.text_input("右 - 注釈 (12px)", key=f"cap_r_{i}")
                
        if file_l and file_r:
            blocks_data.append({
                "type": "double",
                "left": {"src": optimize_image_to_base64(file_l), "alt": alt_l, "link": link_l, "caption": cap_l},
                "right": {"src": optimize_image_to_base64(file_r), "alt": alt_r, "link": link_r, "caption": cap_r}
            })
            
    st.divider()

# ==========================================
# 🚀 HTML生成 & プレビュー機能
# ==========================================
if st.button("🚀 メルマガ用HTMLを生成する", type="primary", use_container_width=True):
    if not blocks_data:
        st.warning("画像がアップロードされていません。")
    else:
        html_code = f"""
        <!DOCTYPE html>
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
            <tr>
                <td align="center">
                    <table class="email-container" width="660" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; max-width: 660px;">
        """
        
        for block in blocks_data:
            if block["type"] == "single":
                img_tag = f'<img src="{block["src"]}" alt="{block["alt"]}" class="fluid-img" style="display: block; width: 100%; max-width: 100%; height: auto; border: 0;">'
                if block["link"]: 
                    img_tag = f'<a href="{block["link"]}" target="_blank">{img_tag}</a>'
                
                html_code += f"""<tr><td style="padding: 0; margin: 0;">{img_tag}</td></tr>"""
                
                if block["caption"]:
                    html_code += f"""<tr><td style="padding: 5px 15px; font-size: 12px; color: #666666; text-align: left;">{block["caption"]}</td></tr>"""
                
                if block["text"]:
                    formatted_text = block["text"].replace('\n', '<br>')
                    html_code += f"""<tr><td style="padding: 20px 15px; font-size: 16px; color: #333333; line-height: 1.6; text-align: left;">{formatted_text}</td></tr>"""

            elif block["type"] == "double":
                img_l = f'<img src="{block["left"]["src"]}" alt="{block["left"]["alt"]}" class="fluid-img" style="display: block; width: 100%; height: auto; border: 0;">'
                if block["left"]["link"]: img_l = f'<a href="{block["left"]["link"]}" target="_blank">{img_l}</a>'
                cap_html_l = f'<div style="padding: 5px 0; font-size: 12px; color: #666666;">{block["left"]["caption"]}</div>' if block["left"]["caption"] else ""

                img_r = f'<img src="{block["right"]["src"]}" alt="{block["right"]["alt"]}" class="fluid-img" style="display: block; width: 100%; height: auto; border: 0;">'
                if block["right"]["link"]: img_r = f'<a href="{block["right"]["link"]}" target="_blank">{img_r}</a>'
                cap_html_r = f'<div style="padding: 5px 0; font-size: 12px; color: #666666;">{block["right"]["caption"]}</div>' if block["right"]["caption"] else ""

                html_code += f"""
                <tr>
                    <td style="padding: 10px 15px;">
                        <table width="100%" border="0" cellspacing="0" cellpadding="0">
                            <tr>
                                <th class="stack-column" width="48%" align="center" valign="top" style="font-weight: normal; padding-right: 2%;">
                                    {img_l}
                                    {cap_html_l}
                                </th>
                                <th class="stack-column" width="48%" align="center" valign="top" style="font-weight: normal; padding-left: 2%;">
                                    {img_r}
                                    {cap_html_r}
                                </th>
                            </tr>
                        </table>
                    </td>
                </tr>
                """

        html_code += """
                    </table>
                </td>
            </tr>
        """
        
        html_code += f"""
            <tr>
                <td align="center" style="background-color: {footer_bg_color}; padding: 20px 10px;">
                    <table width="660" border="0" cellspacing="0" cellpadding="0" style="max-width: 660px;">
                        <tr>
                            <td align="center" style="font-size: 12px; color: {footer_text_color}; line-height: 1.5;">
                                {footer_text}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        </body>
        </html>
        """
        
        st.success("🎉 HTMLが正常に生成されました！")
        st.download_button("📥 HTMLファイルをダウンロード", data=html_code, file_name="dropmail_newsletter.html", mime="text/html")
        
        st.header("👁️ プレビュー")
        st.components.v1.html(html_code, height=800, scrolling=True)