def generate_explanation(client, target_role, user_skills, result_in_text):

    prompt = f"""
Anda adalah konsultan karier profesional di bidang teknologi yang melakukan analisis skill gap.

Target role yang ingin dicapai user:
{target_role}

User saat ini memiliki skill:
{', '.join(user_skills)}

Skill yang direkomendasikan untuk mencapai role {target_role} adalah:
{result_in_text}

Skill yang direkomendasikan di atas adalah **skill gap**, yaitu skill yang belum dimiliki user tetapi penting untuk dikuasai agar dapat memenuhi kompetensi yang dibutuhkan pada role tersebut.

Tugas Anda adalah menjelaskan mengapa skill tersebut penting sebagai skill gap yang perlu dipelajari oleh user.

Untuk setiap skill yang direkomendasikan:
1. Jelaskan mengapa skill tersebut penting untuk role {target_role}.
2. Jelaskan mengapa skill tersebut menjadi gap dibandingkan skill yang sudah dimiliki user.
3. Jelaskan bagaimana skill tersebut melengkapi atau memperkuat skill user saat ini.
4. Berikan contoh penggunaan skill tersebut dalam pekerjaan nyata.
5. Berikan saran singkat dan praktis bagaimana user dapat mulai mempelajarinya.

Gunakan Bahasa Indonesia yang formal, jelas, dan ringkas.

Format jawaban:
- Gunakan daftar bernomor sesuai urutan skill yang diberikan.
- Tulis satu paragraf penjelasan yang informatif untuk setiap skill.
- Fokus pada hubungan antara skill yang dimiliki user dan skill gap yang direkomendasikan.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Anda adalah AI konsultan karier profesional di bidang teknologi."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content