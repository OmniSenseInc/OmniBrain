"""Bounded conversation rules; no inference of honesty or authority from text."""
import re

UNKNOWN = re.compile(r'\b(belum tahu|tidak tahu|gak tahu|ga tahu|nggak tahu|belum diukur|belum ada angka|tidak punya angka|nggak ngerti|ga ngerti)\b',re.I)
JUNK = {'asdf','asdfgh','qwerty','qwertyuiop','asdasd','asdsad','abc','xyz','haha','hehe','wkwk','tes','test','testing','awur','asal','lol'}
FIRST_QUESTION = 'Bisa ceritakan satu kejadian terakhir yang paling mengganggu proses bisnis Anda?'
CONTEXT_QUESTION = 'Proses bisnis apa yang ingin Anda perbaiki, dan apa kendala utamanya?'


def unclear(text):
    words=re.findall(r'[a-zA-Z]+',text.lower())
    if UNKNOWN.search(text):return False
    if not words:return True
    if all(w in JUNK or re.fullmatch(r'(.)\1{2,}',w) for w in words):return True
    if re.search(r'\b(?:isi(?:nya)? (?:asal|awur)|cuma (?:tes|test|coba)|hanya (?:tes|test))\b',text,re.I):return True
    if all(len(w)>5 and sum(c in 'aiueo' for c in w)/len(w)<0.12 for w in words):return True
    return False


def unsafe_context(text):
    return bool(re.search(r'abaikan.*(?:aturan|instruksi)|ignore.*instructions|system prompt|sudo |rm -rf|api[_ -]?key|<script',text,re.I))


def question(body,cursor,status='discovery',questions=None):
    if status=='awaiting_confirmation':return 'Boleh ringkasan ini masuk antrean review tim? Balas “ya”, atau /stop.'
    if status=='ready_for_team':return 'Jika ada koreksi pada ringkasan, sampaikan agar tim meninjaunya; belum ada jadwal yang dikonfirmasi.'
    if cursor==0:
        return body.get('opening_question') or (body['result']['next_questions'][0]['probe'] if body['result']['next_questions'] else FIRST_QUESTION)
    return questions[min(cursor-1,len(questions)-1)][1]


def opening(body,current_question):
    ctx=body['payload']['context']
    bad=any(unclear(ctx[k]) or unsafe_context(ctx[k]) for k in ['process','problem'])
    if bad:
        return 'Halo, saya OmniSense. Hasil kuisnya sudah terhubung. Agar saya tidak salah memahami kebutuhan Anda, kita perjelas dulu situasi bisnisnya.\n\n'+current_question
    process=re.sub(r'[*_~`<>]','',ctx['process'])[:120]
    problem=re.sub(r'[*_~`<>]','',ctx['problem'])[:260]
    return 'Halo, saya OmniSense. Saya menangkap Anda ingin membahas '+process+', dengan kendala: '+problem+'. Jawaban kuis jadi gambaran awal; kita cocokkan dengan kondisi yang Anda alami.\n\n'+current_question


def intent(text):
    low=text.lower().strip()
    if unsafe_context(text):return 'unclear'
    if re.search(r'(?:boleh|bisa|apakah|apa perlu).*(?:kirim|unggah|upload|bagikan|kasih).*(?:data pelanggan|password|token|nomor kartu|data rahasia)|(?:boleh|bisa|apakah).*tanpa izin',low):return 'privacy'
    if re.search(r'(?:bikinin|buatkan|tulis(?:kan)?).*puisi romantis|main tebak[- ]tebakan',low):return 'offtopic'
    if re.search(r'\b(?:berapa|brp|gimana|bagaimana|apa|apakah)\b.*\b(?:harga|biaya|tarif|budget)\b|\b(?:harga|biaya|tarif)\b.*\?|\bpricing\b|\b(?:konsultasi|konsul)\b.*\bgratis\b|\b(?:berapa|brp)\s+(?:harganya|biayanya)\b',low):return 'pricing'
    if re.match(r'(?:bukan itu|maksud saya|maksudku|koreksi|ralat\b|yang saya maksud|sebenarnya (?:keluhan|bukan))',low):return 'correction'
    if unclear(text) or low in {'ya','iya','ok','oke','hmm','hmmm'}:return 'unclear'
    if re.match(r'(?:kenapa|mengapa|gimana|bagaimana|apakah|apa itu|apa maksud|boleh|bisa(?:kah)? (?:jelas|jelasin|jelaskan|ulang)|tolong (?:jelas|jelasin|jelaskan|ulang)|saya mau tanya)',low) or '?' in text:return 'followup'
    return 'unknown' if UNKNOWN.search(text) else 'answer'


def permission_denied(text):
    # Explicit negative statements only. Questions about permission are clarification,
    # never a grant; neither a positive answer nor this matcher gives tools/access.
    if '?' in text:return False
    return bool(re.search(r'tidak ada izin|tidak diizinkan|belum diizinkan|dilarang|tanpa izin|tidak boleh|(?:nggak|gak|ga) ada izin|(?:nggak|gak|ga) diizinkan|belum (?:punya|ada|dapat) izin|tanpa persetujuan|diam[- ]diam',text,re.I))


def fallback(kind,current_question,latest_message=''):
    lead={
        'pricing':'Konsultasi ini gratis. Untuk pengerjaan sistem, biaya mengikuti kebutuhan dan ruang lingkup yang disepakati; nominalnya belum bisa ditentukan dari kuis saja.',
        'privacy':'Cukup jelaskan jenis data dan aplikasinya; jangan kirim data pelanggan, password atau token. Pemakaian data harus mendapat izin yang sesuai, dan chat ini tidak memberi izin akses sistem.',
        'offtopic':'Saya bantu konsultasi proses bisnis yang sedang kita bahas dulu. Jika kebutuhannya berubah, jelaskan hubungannya dengan masalah bisnis Anda.',
        'unclear':'Saya belum menangkap informasi yang cukup dari jawaban tadi. Tidak perlu angka atau istilah teknis; ceritakan kondisi yang Anda alami.',
        'unknown':'Tidak apa-apa kalau belum tahu atau belum punya angka. Kita bisa mulai dari contoh kejadian, lalu menandai informasi yang masih perlu diperiksa.',
        'followup':'Boleh, kita perjelas dulu sebelum lanjut. Jawaban kuis belum menjadi diagnosis; contoh proses dan kejadian membantu kita menilai kebutuhan yang sebenarnya.',
        'correction':'Terima kasih sudah meluruskan. Koreksi Anda dicatat sebagai penjelasan tambahan untuk ditinjau; kesimpulan sebelumnya belum dianggap pasti.',
        'answer':'Saya catat penjelasan Anda sebagai gambaran awal; penyebab dan dampaknya masih perlu diperiksa bersama bukti.'}[kind]
    clean=re.sub(r'[\n*_~`<>]',' ',latest_message).strip()[:220].rstrip('. ')
    if kind=='answer' and clean:
        lead='Saya catat penjelasan Anda: “'+clean+'”. Ini gambaran awal; penyebab dan solusi masih perlu diperiksa.'
    if kind=='followup' and re.search(r'angka dasar|baseline|pembanding',latest_message,re.I):
        lead='Angka dasar adalah catatan kondisi sekarang, supaya nanti kita bisa membandingkan hasil perbaikan. Kalau belum punya angka, kita mulai dari contoh kejadian dan catat waktunya; tidak perlu menebak nilainya.'
    if kind=='followup' and re.search(r'(?:harus|wajib|perlu).*ai',latest_message,re.I):
        lead='AI tidak otomatis diperlukan. Kita bandingkan perbaikan proses, software atau otomasi aturan, lalu pertimbangkan AI jika kebutuhan dan bukti mendukungnya.'
    return lead+'\n\n'+current_question
