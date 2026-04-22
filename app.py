import streamlit as st
from PIL import Image
import io
import base64
import zipfile

# ==========================================
# 🎨 画面幅を広く使うための設定 (Wide Layout)
# ==========================================
# 📌 ここを "wide" に戻したことで、画面いっぱいに広く使えるようになりました！
st.set_page_config(page_title="DropMail Builder", layout="wide")

st.markdown("""
<style>
    hr { margin: 2em 0; border-color: #f0f0f0; }
</style>
""", unsafe_allow_html=True)

# --- 画像最適化（990pxで高画質維持） ---
def get_optimized_image_bytes(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    img.thumbnail((990, 3000)) 
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True) 
    return buffer.getvalue()

# --- 画像のURLパス生成 ---
def get_image_src(img_bytes, filename, is_preview):
    if is_preview:
        b64 = base64.b64encode(img_bytes).decode()
        return f"data:image/jpeg;base64,{b64}"
    else:
        return f"img/{filename}"

st.title("💌 DropMail Builder")
st.write("画面を広く使って、快適にメルマガを作成しましょう！")

# ==========================================
# セッション初期化（ブロックの追加状態を記憶）
# ==========================================
if 'layout_blocks' not in st.session_state:
    st.session_state['layout_blocks'] = []

def add_single_block(): st.session_state['layout_blocks'].append("single")
def add_double_block(): st.session_state['layout_blocks'].append("double")
def add_text_block(): st.session_state['layout_blocks'].append("text")
def clear_blocks(): st.session_state['layout_blocks'] = []

# ==========================================
# 🧩 追従(Sticky)するブロック追加メニュー
# ==========================================
col1, col2, col3, col4 = st.columns(4)
with col1: st.button("➕ 画像 (1列)", on_click=add_single_block, use_container_width=True)
with col2: st.button("➕ 画像 (2列)", on_click=add_double_block, use_container_width=True)
with col3: st.button("📝 テキスト", on_click=add_text_block, use_container_width=True)
with col4: st.button("🗑️ 全てリセット", on_click=clear_blocks, use_container_width=True)

st.components.v1.html("""
<script>
(function() {
    var timer;
    function applySticky() {
        try {
            var doc = window.parent.document;
            var blocks = doc.querySelectorAll('[data-testid="stHorizontalBlock"]');
            if (blocks.length > 0) {
                var btn = blocks[0];
                btn.style.position = 'sticky';
                btn.style.top = '60px';
                btn.style.zIndex = '999';
                btn.style.backgroundColor = 'white';
                btn.style.padding = '12px';
                btn.style.boxShadow = '0 4px 15px rgba(0,0,0,0.08)';
                btn.style.borderRadius = '10px';
                btn.style.border = '1px solid #eeeeee';
                btn.style.marginBottom = '16px';
            }
        } catch(e) {}
    }
    setTimeout(applySticky, 100);
    setTimeout(applySticky, 500);
    try {
        var obs = new MutationObserver(function() {
            clearTimeout(timer);
            timer = setTimeout(applySticky, 80);
        });
        obs.observe(window.parent.document.body, {childList: true, subtree: true});
    } catch(e) {}
})();
</script>
""", height=0)

blocks_data = []
image_counter = 1

# ==========================================
# メインの編集エリア
# ==========================================
for i, b_type in enumerate(st.session_state['layout_blocks']):
    
    if b_type == "single":
        st.markdown(f"### 📍 ブロック {i+1} : 画像 (1列)")
        bg_color = st.color_picker("このセクションの背景色", value="#ffffff", key=f"bg_{i}")
        
        file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"], key=f"file_{i}")
        if file:
            c1, c2 = st.columns([1, 2])
            with c1: st.image(file, use_container_width=True)
            with c2:
                alt = st.text_input("代替テキスト (Alt)", key=f"alt_{i}")
                link = st.text_input("リンクURL (画像クリック時)", key=f"link_{i}")
                # ※不要なボタンテキスト等の入力欄は削除済み！

            img_bytes = get_optimized_image_bytes(file)
            filename = f"image_{image_counter:02d}.jpg"
            image_counter += 1
            blocks_data.append({"type": "single", "bytes": img_bytes, "filename": filename, "alt": alt, "link": link, "bg_color": bg_color})
            
    elif b_type == "double":
        st.markdown(f"### 📍 ブロック {i+1} : 画像 (2列)")
        bg_color = st.color_picker("このセクションの背景色", value="#ffffff", key=f"bg_{i}")

        c_left, c_right = st.columns(2)
        with c_left:
            file_l = st.file_uploader("◀️ 左側の画像", type=["png", "jpg", "jpeg"], key=f"file_l_{i}")
            if file_l:
                alt_l = st.text_input("左 - 代替テキスト", key=f"alt_l_{i}")
                link_l = st.text_input("左 - リンクURL", key=f"link_l_{i}")
        with c_right:
            file_r = st.file_uploader("▶️ 右側の画像", type=["png", "jpg", "jpeg"], key=f"file_r_{i}")
            if file_r:
                alt_r = st.text_input("右 - 代替テキスト", key=f"alt_r_{i}")
                link_r = st.text_input("右 - リンクURL", key=f"link_r_{i}")
                
        if file_l and file_r:
            bytes_l = get_optimized_image_bytes(file_l)
            filename_l = f"image_{image_counter:02d}.jpg"
            image_counter += 1
            bytes_r = get_optimized_image_bytes(file_r)
            filename_r = f"image_{image_counter:02d}.jpg"
            image_counter += 1
            blocks_data.append({"type": "double", "bg_color": bg_color, "left": {"bytes": bytes_l, "filename": filename_l, "alt": alt_l, "link": link_l}, "right": {"bytes": bytes_r, "filename": filename_r, "alt": alt_r, "link": link_r}})
            
    elif b_type == "text":
        st.markdown(f"### 📝 ブロック {i+1} : テキスト")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            # 📌 注釈(Caption)を階層に追加
            text_type = st.radio("テキスト階層", ["見出し", "本文", "注釈"], key=f"t_type_{i}", horizontal=True)
            text_align = st.radio("配置", ["左", "中央", "右"], key=f"t_align_{i}", horizontal=True)
            align_val = "left" if "左" in text_align else "center" if "中央" in text_align else "right"
        with t_col2:
            bg_color = st.color_picker("背景色", value="#ffffff", key=f"t_bg_{i}")
            text_color = st.color_picker("文字色", value="#333333", key=f"t_color_{i}")

        text_content = st.text_area("テキストを入力", key=f"text_only_{i}", height=120)

        if text_content:
            blocks_data.append({"type": "text_only", "content": text_content, "align": align_val, "bg_color": bg_color, "text_color": text_color, "text_type": text_type})
            
    st.divider()

# ==========================================
# 📝 フッター設定 (画面の一番下に配置)
# ==========================================
st.markdown("### 📝 フッター設定")
footer_text = st.text_input("コピーライトテキスト", value="© 2026 DropMail. All rights reserved.")
col_f1, col_f2 = st.columns(2)
with col_f1: footer_bg_color = st.color_picker("フッター背景色", value="#f4f4f4")
with col_f2: footer_text_color = st.color_picker("フッター文字色", value="#999999")
st.divider()

# ==========================================
# 🚀 HTML生成エンジン（メルマガの幅は660px固定！）
# ==========================================
def generate_html_code(blocks, is_preview=False):
    font_stack = "'Helvetica Neue', Helvetica, Arial, 'Hiragino Sans', 'Meiryo', sans-serif"
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{ margin: 0; padding: 0; background-color: #f4f4f4; -webkit-font-smoothing: antialiased; }}
    /* メルマガの幅はここで660pxに制限しています */
    .email-container {{ width: 100%; max-width: 660px; margin: 0 auto; background-color: #ffffff; }}
    .fluid-img {{ width: 100% !important; height: auto !important; display: block; border: 0; }}
    @media only screen and (max-width: 660px) {{ .stack-column {{ display: block !important; width: 100% !important; padding: 0 0 15px 0 !important; }} }}
</style>
</head>
<body>
<table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f4f4f4;">
    <tr><td align="center">
        <table class="email-container" border="0" cellspacing="0" cellpadding="0">
"""
    
    for block in blocks:
        bg = block.get("bg_color", "#ffffff")
        
        if block["type"] == "single":
            src = get_image_src(block["bytes"], block["filename"], is_preview)
            img_tag = f'<img src="{src}" alt="{block["alt"]}" class="fluid-img">'
            if block["link"]: img_tag = f'<a href="{block["link"]}" target="_blank">{img_tag}</a>'
            
            html += f'<tr><td style="background-color: {bg}; padding: 0; margin: 0;">{img_tag}</td></tr>'
        
        elif block["type"] == "double":
            src_l = get_image_src(block["left"]["bytes"], block["left"]["filename"], is_preview)
            img_l = f'<img src="{src_l}" alt="{block["left"]["alt"]}" class="fluid-img">'
            if block["left"]["link"]: img_l = f'<a href="{block["left"]["link"]}" target="_blank">{img_l}</a>'
            src_r = get_image_src(block["right"]["bytes"], block["right"]["filename"], is_preview)
            img_r = f'<img src="{src_r}" alt="{block["right"]["alt"]}" class="fluid-img">'
            if block["right"]["link"]: img_r = f'<a href="{block["right"]["link"]}" target="_blank">{img_r}</a>'

            html += f"""
            <tr><td style="background-color: {bg}; padding: 10px 15px;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0"><tr>
                    <th class="stack-column" width="48%" align="center" valign="top" style="font-weight: normal; padding-right: 2%;">{img_l}</th>
                    <th class="stack-column" width="48%" align="center" valign="top" style="font-weight: normal; padding-left: 2%;">{img_r}</th>
                </tr></table>
            </td></tr>
            """
        
        elif block["type"] == "text_only":
            formatted_text = block["content"].replace('\n', '<br>')
            
            # 📌 注釈は12pxで表示
            if "見出し" in block["text_type"]:
                font_style = f"font-size: 24px; font-weight: bold; line-height: 1.4;"
            elif "注釈" in block["text_type"]:
                font_style = f"font-size: 12px; font-weight: normal; line-height: 1.5;"
            else:
                font_style = f"font-size: 16px; font-weight: normal; line-height: 1.6;"

            html += f"""
            <tr><td style="background-color: {bg}; padding: 30px 20px;">
                <div style="font-family: {font_stack}; color: {block["text_color"]}; text-align: {block["align"]}; {font_style}">
                    {formatted_text}
                </div>
            </td></tr>
            """

    # フッター生成
    html += f"""
        </table>
    </td></tr>
    <tr><td align="center" style="background-color: {footer_bg_color}; padding: 30px 15px;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 660px;">
            <tr><td align="center" style="font-family: {font_stack}; font-size: 12px; color: {footer_text_color}; line-height: 1.5;">
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
if st.button("🚀 HTML・ZIP を生成する", type="primary", use_container_width=True):
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
        
        st.success("🎉 ZIPファイルの準備が完了しました！")
        st.download_button(
            label="📥 ZIPファイルをダウンロード (index.html + imgフォルダ)",
            data=zip_buffer.getvalue(),
            file_name="dropmail_package.zip",
            mime="application/zip"
        )
        
        st.markdown("### 👁️ プレビュー (幅660px固定)")
        preview_html = generate_html_code(blocks_data, is_preview=True)
        # プレビュー枠が小さくならないように横幅を広く確保
        st.components.v1.html(preview_html, height=800, width=800, scrolling=True)