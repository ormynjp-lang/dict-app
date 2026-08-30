import sqlite3
import streamlit as st

DB_NAME = "dictionary.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    # Sütun isimleriyle sözlük gibi (row['word_kanji']) erişebilmek için
    conn.row_factory = sqlite3.Row
    return conn


def get_all_romaji():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word_romaji, word_kanji FROM words")
    results = cursor.fetchall()
    conn.close()
    return results


def get_word_by_romaji(romaji_target):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM words WHERE word_romaji = ?", (romaji_target,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_random_word():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row


def update_word(
    old_romaji,
    word_kanji,
    word_kana,
    word_romaji,
    meaning,
    pos,
    example_kanji,
    example_kana,
    example_meaning,
    tags,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE words SET 
            word_kanji = ?, 
            word_kana = ?, 
            word_romaji = ?, 
            meaning = ?, 
            pos = ?, 
            example_kanji = ?, 
            example_kana = ?, 
            example_meaning = ?, 
            tags = ?
        WHERE word_romaji = ?
    """,
        (
            word_kanji,
            word_kana,
            word_romaji,
            meaning,
            pos,
            example_kanji,
            example_kana,
            example_meaning,
            tags,
            old_romaji,
        ),
    )
    conn.commit()
    conn.close()


# --- STREAMLIT ARAYÜZÜ ---
st.set_page_config(
    page_title="Kotobase Kelime Kontrol Paneli", layout="centered"
)

st.title("🔍 Kotobase Kelime Kontrol ve Zenginleştirme Paneli")
st.markdown(
    "Mevcut kelimelerinizi rastgele çekerek veya aratarak inceleyebilir, örnek"
    " cümleleri zenginleştirip güncelleyebilirsiniz."
)
st.markdown("---")

if "selected_word" not in st.session_state:
    st.session_state.selected_word = None

# --- ÜST KISIM: SEÇENEKLER ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🎲 Rastgele Kelime Getir", use_container_width=True):
        rand_word = get_random_word()
        if rand_word:
            st.session_state.selected_word = rand_word
            st.success("Rastgele kelime getirildi!")
        else:
            st.warning("Veritabanında hiç kelime bulunamadı.")

with col2:
    all_words = get_all_romaji()
    word_options = {
        f"{r['word_romaji']} ({r['word_kanji']})": r["word_romaji"]
        for r in all_words
    }

    selected_option = st.selectbox(
        "🔎 Romaji ile Ara / Seç",
        options=list(word_options.keys()),
        index=None,
        placeholder="Aramak için yazın...",
    )

    if selected_option:
        chosen_romaji = word_options[selected_option]
        st.session_state.selected_word = get_word_by_romaji(chosen_romaji)

st.markdown("---")

# --- KUTUCUKLU FORM YAPISI ---
if st.session_state.selected_word:
    w = st.session_state.selected_word
    old_romaji_val = w["word_romaji"]

    with st.form("update_form"):
        st.subheader("📝 Kelime Bilgileri ve Düzenleme Alanı")

        f_kanji = st.text_input("Kanji (word_kanji)", value=w["word_kanji"])
        f_kana = st.text_input("Kana (word_kana)", value=w["word_kana"])
        f_romaji = st.text_input("Romaji (word_romaji)", value=w["word_romaji"])
        f_meaning = st.text_input("Anlamı (meaning)", value=w["meaning"])
        f_pos = st.text_input("Kelime Türü (pos)", value=w["pos"])

        st.markdown("---")
        f_ex_kanji = st.text_area(
            "Örnek Cümle Japonca (example_kanji)", value=w["example_kanji"]
        )
        f_ex_kana = st.text_area(
            "Örnek Cümle Okunuşu (example_kana)", value=w["example_kana"]
        )
        f_ex_meaning = st.text_area(
            "Örnek Cümle Çevirisi (example_meaning)", value=w["example_meaning"]
        )

        f_tags = st.text_input("Seviye / Etiket (tags)", value=w["tags"])

        submitted = st.form_submit_button(
            "💾 Değişiklikleri Kaydet (Güncelle)", use_container_width=True
        )

        if submitted:
            update_word(
                old_romaji_val,
                f_kanji,
                f_kana,
                f_romaji,
                f_meaning,
                f_pos,
                f_ex_kanji,
                f_ex_kana,
                f_ex_meaning,
                f_tags,
            )
            st.success(f"'{f_romaji}' başarıyla güncellendi!")
            # Güncel hali forma tekrar yansıt
            st.session_state.selected_word = get_word_by_romaji(f_romaji)
else:
    st.info(
        "👆 Devam etmek için yukarıdan **Rastgele Kelime Getir** butonuna"
        " basın veya arama çubuğundan bir kelime seçin."
    )