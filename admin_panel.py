import sqlite3
import streamlit as st

DB_NAME = "dictionary.db"


def get_connection():
  conn = sqlite3.connect(DB_NAME)
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
  cursor.execute("SELECT * FROM words WHERE word_romaji = ?", (romaji_target,))
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


def insert_word(
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
        INSERT INTO words (
            word_kanji, word_kana, word_romaji, meaning, pos, 
            example_kanji, example_kana, example_meaning, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
      ),
  )
  conn.commit()
  conn.close()


# --- STREAMLIT ARAYÜZÜ ---
st.set_page_config(
    page_title="Kotobase Kelime Kontrol Paneli", layout="centered"
)

st.title("🔍 Kotobase Kelime Kontrol ve Yönetim Paneli")
st.markdown(
    "Mevcut kelimelerinizi inceleyebilir, güncelleyebilir veya veritabanına"
    " yeni kelimeler ekleyebilirsiniz."
)
st.markdown("---")

if "random_word" not in st.session_state:
  st.session_state.random_word = None

if "search_word" not in st.session_state:
  st.session_state.search_word = None

# --- 3 SEKMELİ YAPI ---
tab_random, tab_search, tab_add = st.tabs(
    ["🎲 Rastgele Kelime", "🔎 Aratarak Getir", "➕ Yeni Kelime Ekle"]
)

# 1. SEKME: RASTGELE KELİME
with tab_random:
  st.subheader("🎲 Rastgele Kelime İncele ve Güncelle")

  if st.button("Rastgele Kelime Çek", use_container_width=True):
    st.session_state.random_word = get_random_word()

  if st.session_state.random_word:
    w = st.session_state.random_word
    old_romaji_val = w["word_romaji"]

    with st.form("random_update_form"):
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
          "💾 Değişiklikleri Kaydet", use_container_width=True
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
        st.session_state.random_word = get_word_by_romaji(f_romaji)
  else:
    st.info("Başlamak için yukarıdaki butona tıklayarak rastgele bir kelime getirin.")

# 2. SEKME: ARATARAK GETİR
with tab_search:
  st.subheader("🔎 Romaji ile Arama Yap ve Düzenle")

  all_words = get_all_romaji()
  word_options = {
      f"{r['word_romaji']} ({r['word_kanji']})": r["word_romaji"]
      for r in all_words
  }

  selected_option = st.selectbox(
      "Kelime Seçin",
      options=list(word_options.keys()),
      index=None,
      placeholder="Aramak için yazın...",
  )

  if selected_option:
    chosen_romaji = word_options[selected_option]
    st.session_state.search_word = get_word_by_romaji(chosen_romaji)

  if st.session_state.search_word:
    w = st.session_state.search_word
    old_romaji_val = w["word_romaji"]

    with st.form("search_update_form"):
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

      submitted_search = st.form_submit_button(
          "💾 Değişiklikleri Kaydet", use_container_width=True
      )

      if submitted_search:
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
        st.session_state.search_word = get_word_by_romaji(f_romaji)

# 3. SEKME: YENİ KELİME EKLE
with tab_add:
  st.subheader("➕ Veritabanına Yeni Kelime Ekle")

  with st.form("insert_form"):
    new_kanji = st.text_input("Kanji (word_kanji)")
    new_kana = st.text_input("Kana (word_kana)")
    new_romaji = st.text_input("Romaji (word_romaji)")
    new_meaning = st.text_input("Anlamı (meaning)")
    new_pos = st.text_input("Kelime Türü (pos)")

    st.markdown("---")
    new_ex_kanji = st.text_area("Örnek Cümle Japonca (example_kanji)")
    new_ex_kana = st.text_area("Örnek Cümle Okunuşu (example_kana)")
    new_ex_meaning = st.text_area("Örnek Cümle Çevirisi (example_meaning)")

    new_tags = st.text_input("Seviye / Etiket (tags)")

    submitted_insert = st.form_submit_button(
        "✨ Yeni Kelimeyi Kaydet", use_container_width=True
    )

    if submitted_insert:
      if new_romaji and new_meaning:
        insert_word(
            new_kanji,
            new_kana,
            new_romaji,
            new_meaning,
            new_pos,
            new_ex_kanji,
            new_ex_kana,
            new_ex_meaning,
            new_tags,
        )
        st.success(
            f"'{new_romaji}' ({new_meaning}) başarıyla veritabanına eklendi!"
        )
      else:
        st.warning("Lütfen en azından Romaji ve Anlam alanlarını doldurun.")