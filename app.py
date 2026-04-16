import streamlit as st
from PIL import Image
import io
import base64

# --- 1. 이미지 용량 최적화 함수 (660px 적용) ---
def optimize_image_to_base64(uploaded_file):
    img = Image.open(uploaded_file)
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # 📌 요청하신 대로 가로 660px 기준으로 비율 유지
    img.thumbnail((660, 2000)) 
    
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True) 
    
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

# --- 웹 UI 시작 ---
st.set_page_config(page_title="💌 메일 매거진 빌더", layout="wide")
st.title("💌 초간단 이미지 템플릿 메일 빌더")
st.write("이미지를 순서대로 올리고, 필요한 곳에만 링크와 텍스트를 쏙쏙 넣어보세요.")

uploaded_files = st.file_uploader("이미지들을 순서대로 올려주세요 (드래그 앤 드롭)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    blocks_data = []
    
    st.header("⚙️ 상세 설정")
    for i, file in enumerate(uploaded_files):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(file, use_container_width=True)
            
        with col2:
            st.subheader(f"블록 {i+1}")
            alt_text = st.text_input("대체 텍스트 (Alt Text - 필수)", key=f"alt_{i}", placeholder="예: 메인 배너 이미지")
            
            # 📌 링크 추가 여부를 체크박스로 선택!
            use_link = st.checkbox("🔗 이 이미지에 링크 걸기", key=f"use_link_{i}")
            link_url = ""
            if use_link:
                link_url = st.text_input("클릭 시 이동할 링크 URL", key=f"link_{i}", placeholder="https://...")
            
            # 📌 텍스트 추가 여부도 체크박스로 선택!
            use_text = st.checkbox("📝 이 이미지 아래에 텍스트 블록 추가", key=f"use_text_{i}")
            text_block = ""
            if use_text:
                text_block = st.text_area("추가할 텍스트를 입력하세요", key=f"text_{i}")
            
        base64_img = optimize_image_to_base64(file)
        
        # 이미지 블록 저장
        blocks_data.append({"type": "image", "src": base64_img, "alt": alt_text, "link": link_url})
        
        # 텍스트 블록 저장 (체크하고 내용을 입력했을 때만)
        if use_text and text_block: 
             blocks_data.append({"type": "text", "content": text_block})
             
        st.divider()
        
    # --- 반응형 HTML 생성 버튼 ---
    if st.button("🚀 HTML 메일 생성하기", type="primary"):
        # 📌 템플릿의 컨테이너 가로폭도 660px로 맞춤!
        html_code = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @media only screen and (max-width: 660px) {
                .email-container { width: 100% !important; }
                .fluid-img { width: 100% !important; height: auto !important; }
            }
        </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f4f4f4;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f4f4f4;">
            <tr>
                <td align="center">
                    <table class="email-container" width="660" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; max-width: 660px;">
        """
        
        for block in blocks_data:
            if block["type"] == "image":
                img_tag = f'<img src="{block["src"]}" alt="{block["alt"]}" class="fluid-img" style="display: block; width: 100%; max-width: 100%; height: auto; border: 0;">'
                if block["link"]: 
                    img_tag = f'<a href="{block["link"]}" target="_blank">{img_tag}</a>'
                
                html_code += f"""<tr><td style="padding: 0; margin: 0;">{img_tag}</td></tr>"""
                
            elif block["type"] == "text":
                formatted_text = block["content"].replace('\n', '<br>')
                html_code += f"""<tr><td style="padding: 30px 20px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 16px; color: #333333; line-height: 1.6; text-align: center;">{formatted_text}</td></tr>"""
                
        html_code += """
                    </table>
                </td>
            </tr>
        </table>
        </body>
        </html>
        """
        
        st.success("🎉 성공적으로 660px 맞춤형 HTML 메일이 완성되었습니다!")
        st.download_button("📥 완성된 HTML 파일 다운로드", data=html_code, file_name="newsletter_660.html", mime="text/html")
        
        st.header("👁️ 결과물 미리보기")
        # 미리보기 창도 660px이 잘 보이도록 여유 공간 세팅
        st.components.v1.html(html_code, height=800, scrolling=True)