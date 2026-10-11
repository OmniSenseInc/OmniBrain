"""Bounded conversation rules; no inference of honesty or authority from text."""
import re
from consultation_adaptive import wording
from consultation_voice import ACKS,conversational_lead
import unicodedata

LINK = re.compile(r'(?i)(?:\b[a-z][a-z0-9+.-]*://[^\s<>\"\x27]+|\b(?:javascript|data|vbscript):[^\s<>]+|\bwww\.[^\s<>\"\x27]+|(?<![\w-])(?:[\w-]+\.)+[^\W\d_]{2,63}(?::\d+)?(?:/[^\s<>\"\x27]*)?|(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s<>\"\x27]*)?)')
TRUSTED_PRIVACY='https://omnisense.my.id/privacy.html#konsultasi-v3'

def normalize_outgoing(text):
    return ''.join(c for c in unicodedata.normalize('NFKC',text) if unicodedata.category(c)!='Cf')

def contains_link(text):
    return bool(LINK.search(normalize_outgoing(text)))

def safe_outgoing(text):
    text=normalize_outgoing(text)
    text=re.sub(r'<\s*/?\s*[A-Za-z!][^>]*>','',text)
    def replace(match):
        value=match.group(0)
        punctuation=''
        while value and value[-1] in '.,;!?)':punctuation=value[-1]+punctuation;value=value[:-1]
        return (value if value==TRUSTED_PRIVACY else '[tautan tidak ditampilkan]')+punctuation
    return LINK.sub(replace,text)

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
    return wording(body,cursor,questions) or questions[min(cursor-1,len(questions)-1)][1]


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
    operating_cost=bool(re.search(r'biaya (?:operasional|produksi|pengiriman|bahan|admin)',low))
    if not operating_cost and re.search(r'\b(?:berapa|brp|gimana|bagaimana|apa|apakah)\b.*\b(?:harga|biaya|tarif|budget)\b|\b(?:harga|biaya|tarif)\b.*\?|\bpricing\b|\b(?:konsultasi|konsul)\b.*\bgratis\b|\b(?:berapa|brp)\s+(?:harganya|biayanya)\b',low):return 'pricing'
    if re.match(r'(?:(?:eh|oh|iya|oke|maaf)[,\s]+)*(?:bukan itu|bukan gitu|maksud saya|maksudku|koreksi|ralat\b|yang saya maksud|sebenarnya (?:keluhan|bukan))',low):return 'correction'
    if unclear(text) or low in ACKS|{'hmm','hmmm'}:return 'unclear'
    if re.match(r'(?:kenapa|mengapa|gimana|bagaimana|apakah|apa itu|apa maksud|boleh|bisa(?:kah)? (?:jelas|jelasin|jelaskan|ulang)|tolong (?:jelas|jelasin|jelaskan|ulang)|saya mau tanya)',low) or '?' in text:return 'followup'
    return 'unknown' if UNKNOWN.search(text) else 'answer'


def permission_denied(text):
    # Only a reported lack of permission triggers a hold. A question is never a grant.
    low=re.sub(r'\b(?:nggak|enggak|gak|ga|gk)\b','tidak',text.lower())
    clauses=re.split(r'[.!?;\n]+|,\s*(?=(?:apa|apakah|bagaimana|gimana|boleh|bisa)\b)',low)
    for raw in clauses:
        clause=raw.strip()
        if re.match(r'^(?:bagaimana|gimana|apakah|apa|boleh|bisakah|bisa|misal|misalnya|jika|kalau|jangan)\b',clause):continue
        if re.search(r'\b(?:tidak|belum)\s+(?:punya|memiliki|ada|dapat|mendapat|mendapatkan)\s+(?:izin|persetujuan)\b',clause):return True
        if re.search(r'\b(?:tidak|belum)\s+diizinkan\b|\btanpa (?:izin|persetujuan)\b|\bdiam[- ]diam\b',clause):return True
        if re.search(r'\b(?:pemilik|atasan|manajer|manager)\b.{0,35}\b(?:tidak|belum)\s+(?:mengizinkan|memberi(?:kan)? izin)\b',clause):return True
        if re.search(r'\b(?:dilarang|tidak boleh)\s+(?:(?:saya|kami|anda)\s+)?(?:akses|mengakses|pakai|memakai|gunakan|menggunakan|bagikan|membagikan|ambil|mengambil|kirim|mengirim|lihat|melihat)\b.{0,50}\b(?:data|akun|aplikasi|dokumen|catatan|sistem|informasi|file|database)\b',clause):return True
    return False


def fallback(kind,current_question,latest_message='',body=None):
    lead={
        'pricing':'Konsultasi ini gratis. Untuk pengerjaan sistem, biaya mengikuti kebutuhan dan ruang lingkup yang disepakati; nominalnya belum bisa ditentukan dari kuis saja.',
        'privacy':'Cukup jelaskan jenis data dan aplikasinya; jangan kirim data pelanggan, password atau token. Pemakaian data harus mendapat izin yang sesuai, dan chat ini tidak memberi izin akses sistem.',
        'offtopic':'Saya bantu konsultasi proses bisnis yang sedang kita bahas dulu. Jika kebutuhannya berubah, jelaskan hubungannya dengan masalah bisnis Anda.',
        'unclear':'Saya belum menangkap informasi yang cukup dari jawaban tadi. Tidak perlu angka atau istilah teknis; ceritakan kondisi yang Anda alami.',
        'unknown':'Tidak apa-apa kalau belum tahu atau belum punya angka. Kita bisa mulai dari contoh kejadian, lalu menandai informasi yang masih perlu diperiksa.',
        'followup':'Boleh, kita perjelas dulu sebelum lanjut. Jawaban kuis belum menjadi diagnosis; contoh proses dan kejadian membantu kita menilai kebutuhan yang sebenarnya.',
        'correction':'Terima kasih sudah meluruskan. Koreksi Anda dicatat sebagai penjelasan tambahan untuk ditinjau; kesimpulan sebelumnya belum dianggap pasti.',
        'partial':'Informasi itu saya catat. Kita lengkapi alurnya sebelum menentukan solusi.',
        'answer':'Saya catat penjelasan Anda sebagai gambaran awal; penyebab dan dampaknya masih perlu diperiksa bersama bukti.'}[kind]
    clean=re.sub(r'[\n*_~`<>]',' ',latest_message).strip()[:220].rstrip('. ')
    if kind=='answer' and clean:
        lead='Saya catat penjelasan Anda: “'+clean+'”. Ini gambaran awal; penyebab dan solusi masih perlu diperiksa.'
    if kind=='followup' and re.search(r'angka dasar|baseline|pembanding',latest_message,re.I):
        lead='Angka dasar adalah catatan kondisi sekarang, supaya nanti kita bisa membandingkan hasil perbaikan. Kalau belum punya angka, kita mulai dari contoh kejadian dan catat waktunya; tidak perlu menebak nilainya.'
    if kind=='followup' and re.search(r'(?:harus|wajib|perlu).*ai',latest_message,re.I):
        lead='AI tidak otomatis diperlukan. Kita bandingkan perbaikan proses, software atau otomasi aturan, lalu pertimbangkan AI jika kebutuhan dan bukti mendukungnya.'
    natural=conversational_lead(kind,latest_message,body)
    if natural:lead=natural
    if kind=='followup' and not re.search(r'angka dasar|baseline|pembanding|(?:harus|wajib|perlu).*ai',latest_message,re.I):
        lead='Boleh, kita bahas pertanyaan Anda dulu. Penyebabnya perlu dicocokkan dengan contoh kejadian dan catatan proses.'
    return lead+('\n\n'+current_question if current_question else '')
