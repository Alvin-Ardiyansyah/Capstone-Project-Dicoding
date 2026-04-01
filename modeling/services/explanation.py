"""
LLM Explanation Module.

Provides integration with the Groq API (LLaMA 3.3 70B) to generate
human-readable, professional career consultation explanations based
on the skill gap analysis results and the user's personal context.
"""

from typing import List, Any, Optional, Dict


# ─── Label Mappings ───────────────────────────────────────────────────────────
_EXPERIENCE_LABELS = {
    "fresh_graduate": "seorang Fresh Graduate dengan kurang dari 1 tahun pengalaman",
    "junior": "seorang Junior profesional dengan 1-2 tahun pengalaman kerja",
    "mid_level": "seorang Mid-Level profesional dengan 3+ tahun pengalaman kerja",
}

_BACKGROUND_LABELS = {
    "self_taught": "belajar secara otodidak",
    "bootcamp": "lulusan bootcamp intensif",
    "formal_degree": "lulusan pendidikan formal IT/CS",
}

_TIMELINE_LABELS = {
    "3_months": "sedang aktif mencari kerja dan butuh siap dalam 3 bulan",
    "1_year": "menargetkan transisi karier dalam 1 tahun",
    "flexible": "sedang mengeksplorasi dan tidak terburu-buru",
}


def _build_context_snippet(user_context: Optional[Dict[str, str]] = None) -> str:
    """Build a human-readable context description from the user's profile data."""
    if not user_context:
        return ""

    exp = _EXPERIENCE_LABELS.get(
        user_context.get("experience_level", ""),
        "seorang profesional",
    )
    
    bg_raw = user_context.get("learning_background", "")
    bg_keys = [k.strip() for k in bg_raw.split(',') if k.strip()]
    if bg_keys:
        bg_texts = [_BACKGROUND_LABELS.get(k, "berlatar belakang umum") for k in bg_keys]
        if len(bg_texts) > 1:
            bg = ", ".join(bg_texts[:-1]) + ", dan " + bg_texts[-1]
        else:
            bg = bg_texts[0]
    else:
        bg = "berlatar belakang umum"

    timeline = _TIMELINE_LABELS.get(
        user_context.get("target_timeline", ""),
        "dengan timeline fleksibel",
    )

    return (
        f"\n\nPROFIL USER:\n"
        f"- User adalah {exp}.\n"
        f"- Latar belakang pembelajaran: {bg}.\n"
        f"- Tujuan: {timeline}."
    )


# ═════════════════════════════════════════════════════════════════════════════
#  Generate Per-Skill Explanation
# ═════════════════════════════════════════════════════════════════════════════
def generate_explanation(
    client: Any,
    target_role: str,
    user_skills: List[str],
    result_in_text: str,
    user_context: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate a per-skill career explanation using Groq API (LLaMA 3.3 70B).

    Uses strict prompt isolation to prevent the LLM from mixing
    existing user skills into missing skill explanations.

    Args:
        client: The initialized Groq API client.
        target_role: The job role the user is aiming for.
        user_skills: List of skills the user already possesses.
        result_in_text: Formatted string of recommended missing skills.
        user_context: Optional dict with experience_level, learning_background,
                      and target_timeline for personalized output.

    Returns:
        A formatted string containing the AI's per-skill explanation.
    """
    context_snippet = _build_context_snippet(user_context)

    system_prompt = (
        "Anda adalah AI konsultan karier profesional di bidang teknologi yang JUJUR dan KRITIS. "
        "Jika sebuah skill dalam daftar ternyata SANGAT TIDAK RELEVAN untuk role tersebut "
        "(misal: Python/Java/R untuk Frontend), Anda harus secara tegas memberitahu user bahwa "
        "skill ini memiliki prioritas sangat rendah atau mungkin anomali data, dan sarankan "
        "untuk fokus ke skill urut atas yang lebih penting. "
        "Anda HANYA menjelaskan skill yang BELUM dimiliki user. "
        "DILARANG KERAS menyebut atau merujuk skill yang sudah dimiliki user. "
        "Analisis setiap skill secara ATOMIK dan INDEPENDEN satu sama lain."
    )

    user_prompt = f"""Target role: {target_role}
{context_snippet}

Berikut adalah daftar skill gap (skill yang BELUM dimiliki user dan PERLU dipelajari):
{result_in_text}

INSTRUKSI KETAT:
1. Untuk SETIAP skill gap di atas, tulis SATU paragraf utuh (3-5 kalimat) yang mencakup:
   - Mengapa skill ini penting untuk role "{target_role}".
   - Jelaskan secara singkat apa arti persentase skor skill tersebut bagi user dalam bahasa non-teknis. Contoh arah penjelasan: apakah skill ini termasuk kebutuhan inti yang sebaiknya diprioritaskan lebih dulu, kebutuhan pendukung yang tetap berguna, atau pelengkap yang bisa dipelajari setelah fondasi utama lebih kuat.
   - Kritis & Kontekstual (Kondisi Industri Tahun 2026): Jika skill tersebut sudah usang/legacy, sebutkan bahwa skill tersebut sudah mulai digantikan oleh teknologi modern dan sarankan apakah user perlu mempelajarinya dalam-dalam atau hanya sekadar tahu. Jika skill tersebut adalah standar industri modern, tekankan relevansinya.
   - Langkah praktis untuk mulai mempelajarinya SESUAI konteks profil user (pengalaman, latar belakang, dan timeline mereka).
   PENTING: DILARANG menggunakan bullet points (titik/strip). Gabungkan semuanya menjadi satu paragraf yang naratif dan profesional.

2. ATURAN MUTLAK:
   - JANGAN menyebut skill lain yang tidak ada dalam daftar di atas.
   - JANGAN merujuk pada keahlian yang sudah dimiliki user.
   - Fokus 100% pada skill yang sedang dibahas saja.
   - GUNAKAN VARIASI KALIMAT. Dilarang menggunakan template kalimat yang sama berulang-ulang (misal: "[Skill] sangat penting untuk role frontend karena..."). Buatlah setiap penjelasan terdengar unik dan alami seolah dikonsultasikan langsung oleh seorang manusia.

3. FORMAT OUTPUT:
   LANGSUNG berikan daftar bernomor. DILARANG KERAS memberikan kalimat pembuka seperti "Berikut adalah..." atau penutup.
   Tulis persis dengan format ini:
   1. **[Nama Skill]**: [Paragraf Penjelasan Anda]
   2. **[Nama Skill]**: [Paragraf Penjelasan Anda]

Gunakan Bahasa Indonesia yang formal, profesional, dan ringkas."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


# ═════════════════════════════════════════════════════════════════════════════
#  Generate Career Roadmap Conclusion
# ═════════════════════════════════════════════════════════════════════════════
def generate_conclusion(
    client: Any,
    target_role: str,
    result_in_text: str,
    score: int,
    priority_skills: Optional[List[str]] = None,
    user_context: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate a concise, personalized career roadmap conclusion.

    Args:
        client: The initialized Groq API client.
        target_role: The job role the user is aiming for.
        result_in_text: Formatted string of recommended missing skills.
        score: The user's current skill match percentage.
        priority_skills: Ordered top-priority skills from the final backend ranking.
        user_context: Optional dict for personalizing the conclusion.

    Returns:
        A concise roadmap summary (3-5 sentences).
    """
    context_snippet = _build_context_snippet(user_context)

    system_prompt = (
        "Anda adalah AI konsultan karier profesional. "
        "DILARANG memberikan salam, format tulisan tebal, header, atau bullet points. "
        "Langsung tuliskan satu hingga dua paragraf narasi secara natural."
    )

    priority_line = ", ".join(priority_skills or [])

    user_prompt = f"""Berdasarkan analisis skill gap untuk role "{target_role}":
- Skor kesesuaian user saat ini: {score}%
- Skill yang perlu dipelajari:
{result_in_text}
- Tiga prioritas utama hasil ranking final backend: {priority_line}
{context_snippet}

Tuliskan sebuah narasi singkat (3-5 kalimat) seolah-olah Anda berbicara langsung kepada pengguna di industri teknologi tahun 2026.
Rangkum posisi pengguna saat ini, sebutkan 3 skill utama yang perlu difokuskan, dan estimasi waktu realistis untuk menjadi kompeten BERDASARKAN profil user di atas (pengalaman, latar belakang belajar, dan timeline target mereka).
WAJIB gunakan tiga skill prioritas utama hasil ranking final backend di atas sebagai fokus roadmap. Jangan mengganti prioritas itu dengan skill lain.
PENTING: Jangan prioritaskan skill usang/legacy (seperti jQuery) sebagai fokus utama pembelajaran, melainkan arahkan user untuk memprioritaskan skill modern yang lebih relevan untuk masa depan.
JANGAN menggunakan numbering. JANGAN memberikan judul atau header.
Gunakan Bahasa Indonesia yang profesional dan memotivasi."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
