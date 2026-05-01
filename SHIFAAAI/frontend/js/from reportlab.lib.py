from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.colors import HexColor, black, white

OUTPUT = "/mnt/user-data/outputs/C1_English_Exam_Vol2_Software_Engineering.pdf"

# ── Colours ─────────────────────────────────────────────────────────────────
DARK_NAVY   = HexColor("#0A1628")
NAVY        = HexColor("#132244")
MID_BLUE    = HexColor("#185FA5")
LIGHT_BLUE  = HexColor("#E6F1FB")
TEAL        = HexColor("#0F6E56")
LIGHT_TEAL  = HexColor("#E1F5EE")
PURPLE      = HexColor("#3C3489")
LIGHT_PURPLE= HexColor("#EEEDFE")
AMBER       = HexColor("#854F0B")
LIGHT_AMBER = HexColor("#FAEEDA")
CORAL       = HexColor("#993C1D")
LIGHT_CORAL = HexColor("#FAECE7")
GREEN       = HexColor("#3B6D11")
LIGHT_GREEN = HexColor("#EAF3DE")
GRAY        = HexColor("#5F5E5A")
LIGHT_GRAY  = HexColor("#F1EFE8")
BORDER      = HexColor("#D3D1C7")

W, H = A4
MARGIN = 2*cm
INNER  = W - 2*MARGIN

# ── Style factory ────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

cover_title = S("CT", fontSize=28, fontName="Helvetica-Bold", textColor=white,
                alignment=TA_CENTER, leading=34, spaceAfter=4)
cover_sub   = S("CS", fontSize=13, fontName="Helvetica", textColor=HexColor("#B5D4F4"),
                alignment=TA_CENTER, spaceAfter=3)
cover_info  = S("CI", fontSize=11, fontName="Helvetica", textColor=white,
                alignment=TA_CENTER, spaceAfter=3)
part_title  = S("PT", fontSize=14, fontName="Helvetica-Bold", textColor=white,
                alignment=TA_LEFT, leading=19, spaceAfter=0)
part_sub    = S("PS", fontSize=9,  fontName="Helvetica", textColor=HexColor("#9FE1CB"),
                alignment=TA_LEFT, spaceAfter=0)
section_hd  = S("SH", fontSize=11, fontName="Helvetica-Bold", textColor=MID_BLUE,
                spaceAfter=4, spaceBefore=10)
q_num_st    = S("QN", fontSize=9,  fontName="Helvetica-Bold", textColor=GRAY,
                spaceAfter=2, spaceBefore=4, leading=12)
q_text_st   = S("QT", fontSize=10, fontName="Helvetica", textColor=black,
                spaceAfter=3, leading=14, alignment=TA_JUSTIFY)
q_ital_st   = S("QI", fontSize=10, fontName="Helvetica-Oblique", textColor=HexColor("#2C2C2A"),
                spaceAfter=3, leading=14, alignment=TA_JUSTIFY)
body_st     = S("BT", fontSize=10, fontName="Helvetica", textColor=black,
                spaceAfter=4, leading=15, alignment=TA_JUSTIFY)
passage_st  = S("PA", fontSize=9.5, fontName="Helvetica", textColor=HexColor("#2C2C2A"),
                spaceAfter=4, leading=15.5, alignment=TA_JUSTIFY)
opt_st      = S("OP", fontSize=10, fontName="Helvetica", textColor=black,
                spaceAfter=2, leading=14)
label_st    = S("LB", fontSize=8,  fontName="Helvetica-Bold", textColor=GRAY,
                spaceAfter=2, spaceBefore=4)
instr_st    = S("IN", fontSize=9,  fontName="Helvetica-Oblique", textColor=GRAY,
                spaceAfter=5, leading=13)
note_st     = S("NT", fontSize=9,  fontName="Helvetica", textColor=TEAL,
                spaceAfter=3, leading=13)
ans_st      = S("AK", fontSize=9,  fontName="Helvetica", textColor=CORAL,
                spaceAfter=2, leading=13)
tip_st      = S("TIP",fontSize=9,  fontName="Helvetica-Bold", textColor=PURPLE,
                spaceAfter=2, leading=13)

# ── Helpers ──────────────────────────────────────────────────────────────────
def blank_line(w=None):
    w = w or INNER
    t = Table([[""]], colWidths=[w])
    t.setStyle(TableStyle([
        ("LINEBELOW",(0,0),(0,0),0.5,BORDER),
        ("BOTTOMPADDING",(0,0),(0,0),2),
        ("TOPPADDING",(0,0),(0,0),10),
    ]))
    return t

def write_lines(n=4, w=None):
    elems = []
    for _ in range(n):
        elems.append(blank_line(w))
        elems.append(Spacer(1,3))
    return elems

def opt_row(letter, text):
    d = [[Paragraph(f"<b>{letter}.</b>", opt_st), Paragraph(text, opt_st)]]
    t = Table(d, colWidths=[0.6*cm, INNER - 0.8*cm])
    t.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),1),
        ("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    return t

def part_banner(title, sub, color=DARK_NAVY):
    d = [[Paragraph(title, part_title), Paragraph(sub, part_sub)]]
    t = Table(d, colWidths=[INNER])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),color),
        ("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(-1,-1),14),
        ("RIGHTPADDING",(0,0),(-1,-1),14),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    return t

def info_box(text, bg=LIGHT_BLUE, border=MID_BLUE):
    d = [[Paragraph(text, instr_st)]]
    t = Table(d, colWidths=[INNER])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg),
        ("BOX",(0,0),(-1,-1),0.5,border),
        ("TOPPADDING",(0,0),(-1,-1),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    return t

def tip_box(text):
    d = [[Paragraph(f"<b>EXAM TIP:</b> {text}", tip_st)]]
    t = Table(d, colWidths=[INNER])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT_PURPLE),
        ("BOX",(0,0),(-1,-1),0.5,PURPLE),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    return t

def ans_box(text, bg=LIGHT_TEAL, border=TEAL):
    d = [[Paragraph(f"<b>Answer / Key:</b> {text}", ans_st)]]
    t = Table(d, colWidths=[INNER])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg),
        ("BOX",(0,0),(-1,-1),0.5,border),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    return t

def q_hdr(num, text, marks=2):
    mk = S("mk", fontSize=9, fontName="Helvetica-Bold", textColor=MID_BLUE, alignment=TA_RIGHT)
    d = [[Paragraph(f"Q{num}", q_num_st), Paragraph(text, q_text_st),
          Paragraph(f"[{marks}]", mk)]]
    t = Table(d, colWidths=[0.9*cm, INNER - 1.5*cm, 0.6*cm])
    t.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    return t

def q_hdr_ital(num, text, marks=2):
    mk = S("mk2", fontSize=9, fontName="Helvetica-Bold", textColor=MID_BLUE, alignment=TA_RIGHT)
    d = [[Paragraph(f"Q{num}", q_num_st), Paragraph(text, q_ital_st),
          Paragraph(f"[{marks}]", mk)]]
    t = Table(d, colWidths=[0.9*cm, INNER - 1.5*cm, 0.6*cm])
    t.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    return t

def grammar_ref_box(title, rows, color=LIGHT_PURPLE, border=PURPLE):
    """Small reference box showing grammar pattern"""
    data = [[Paragraph(f"<b>{title}</b>", S("gr",fontSize=9,fontName="Helvetica-Bold",textColor=PURPLE))]]
    for r in rows:
        data.append([Paragraph(r, S("grr",fontSize=9,fontName="Helvetica",textColor=HexColor("#3C3489"),leading=13))])
    t = Table(data, colWidths=[INNER])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),color),
        ("BOX",(0,0),(-1,-1),0.5,border),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    return t

# ── Page callbacks ───────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, H-1.4*cm, W-MARGIN, H-1.4*cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(MARGIN, H-1.2*cm, "C1 English Proficiency — Vol. 2 | Inversion · Probability · Adj+Prep · Wishes · It's Time · Preferences")
    canvas.drawRightString(W-MARGIN, H-1.2*cm, f"Page {doc.page}")
    canvas.line(MARGIN, 1.4*cm, W-MARGIN, 1.4*cm)
    canvas.drawCentredString(W/2, 1.0*cm, "Duration: 2 hours 30 minutes  |  Total: 120 marks  |  Candidate: ___________________________")
    canvas.restoreState()

# ── Document ─────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=2.2*cm, bottomMargin=2.0*cm,
)
story = []

# ════════════════════════════════════════════════════════════════════════════
# COVER
# ════════════════════════════════════════════════════════════════════════════
cover = Table([
    [Paragraph("C1 ENGLISH PROFICIENCY EXAMINATION", cover_title)],
    [Paragraph("Volume II — Advanced Grammar Structures", cover_sub)],
    [Spacer(1,0.2*cm)],
    [Paragraph("Inversion  ·  Probability  ·  Adjective + Preposition", cover_sub)],
    [Paragraph("Wishes  ·  It's Time  ·  Preferences  ·  Reported Speech", cover_sub)],
    [Paragraph("Tenses  ·  Error Correction  ·  Academic Writing", cover_sub)],
    [Spacer(1,0.5*cm)],
    [Paragraph("Software Engineering — University Level", cover_info)],
    [Paragraph("British Council · IELTS · TOEFL Academic Standard", cover_info)],
    [Spacer(1,0.5*cm)],
    [Paragraph("Duration: 2 hours 30 minutes  |  Total: 120 marks", cover_info)],
    [Spacer(1,0.3*cm)],
    [Paragraph("Candidate Name: _____________________________________", cover_info)],
    [Paragraph("Student ID: __________________   Date: __________________", cover_info)],
    [Spacer(1,0.3*cm)],
    [Paragraph("Examiner: _______________   Module: ENG-C1-SE-VOL2", cover_info)],
], colWidths=[INNER])
cover.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),DARK_NAVY),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),24),
    ("RIGHTPADDING",(0,0),(-1,-1),24),
]))
story.append(cover)
story.append(Spacer(1,0.4*cm))

inst_data = [
    [Paragraph("<b>GENERAL INSTRUCTIONS — READ CAREFULLY</b>",
               S("ih",fontSize=10,fontName="Helvetica-Bold",textColor=DARK_NAVY))],
    [Paragraph("• This examination has <b>8 Parts</b> covering all question types at C1 level.", body_st)],
    [Paragraph("• Write legibly. Marks may be deducted for illegible answers.", body_st)],
    [Paragraph("• Marks for each question appear in brackets [ ].", body_st)],
    [Paragraph("• Grammar reference boxes (purple) are provided before each new topic — read them.", body_st)],
    [Paragraph("• Answer ALL questions. No electronic devices permitted.", body_st)],
]
inst_t = Table(inst_data, colWidths=[INNER])
inst_t.setStyle(TableStyle([
    ("BOX",(0,0),(-1,-1),0.5,DARK_NAVY),
    ("BACKGROUND",(0,0),(-1,-1),LIGHT_BLUE),
    ("TOPPADDING",(0,0),(-1,-1),3),
    ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("LEFTPADDING",(0,0),(-1,-1),12),
    ("RIGHTPADDING",(0,0),(-1,-1),12),
]))
story.append(inst_t)
story.append(Spacer(1,0.3*cm))

mk_data = [
    [Paragraph("<b>PART</b>",label_st), Paragraph("<b>TOPIC</b>",label_st),
     Paragraph("<b>MARKS</b>",label_st), Paragraph("<b>TIME</b>",label_st)],
    ["Part 1","Reading — Scientific Text (Distributed AI Systems)","30","35 min"],
    ["Part 2","Inversion — Multiple Types","15","15 min"],
    ["Part 3","Probability (Bound to / Unlikely to) & Adjective + Preposition","12","12 min"],
    ["Part 4","Wishes, If Only & It's Time","13","13 min"],
    ["Part 5","Preferences (Would Rather / Would Prefer)","8","8 min"],
    ["Part 6","Tenses + Reported Speech + Indirect Questions","20","22 min"],
    ["Part 7","Error Correction — Full Paragraph","12","10 min"],
    ["Part 8","Extended Writing — Academic Essay","10","25 min"],
    ["","<b>TOTAL</b>","<b>120</b>","<b>2h 30m</b>"],
]
mk_t = Table(mk_data, colWidths=[1.4*cm, 8.5*cm, 1.8*cm, 1.8*cm])
mk_t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_NAVY),
    ("TEXTCOLOR",(0,0),(-1,0),white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),9),
    ("BACKGROUND",(0,-1),(-1,-1),LIGHT_BLUE),
    ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
    ("ROWBACKGROUNDS",(0,1),(-1,-2),[white,LIGHT_GRAY]),
    ("GRID",(0,0),(-1,-1),0.5,BORDER),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),8),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
]))
story.append(mk_t)
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 1 — READING COMPREHENSION
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("PART 1 — READING COMPREHENSION", "30 marks | Suggested time: 35 minutes", DARK_NAVY))
story.append(Spacer(1,0.25*cm))
story.append(info_box(
    "Read the following academic article carefully (~600 words, C1 level). "
    "Answer ALL questions. Use evidence from the text to support your answers."
))
story.append(Spacer(1,0.15*cm))

story.append(Paragraph("<b>Federated Learning: Privacy-Preserving Machine Intelligence at Scale</b>",
    S("pth",fontSize=11,fontName="Helvetica-Bold",textColor=DARK_NAVY,spaceAfter=6)))

passage = (
    "The proliferation of internet-connected devices — from smartphones and wearables to industrial "
    "sensors and autonomous vehicles — has generated unprecedented volumes of data, much of it highly "
    "sensitive in nature. Conventional machine learning paradigms aggregate this data in centralised "
    "repositories, exposing individuals to substantial privacy risks and creating regulatory liabilities "
    "for the organisations responsible for safeguarding it. Federated learning has emerged as a compelling "
    "alternative, enabling models to be trained collaboratively across distributed devices without the raw "
    "data ever leaving its point of origin.\n\n"
    "The architecture of a federated learning system is conceptually straightforward, though technically "
    "demanding to implement robustly. A central coordination server distributes a global model to a "
    "selected cohort of client devices — often thousands or millions of endpoints simultaneously. Each "
    "client trains a local copy of the model on its private data, computing the resulting gradient "
    "updates without transmitting the underlying training samples. These gradient updates, which encode "
    "the statistical patterns learned from local data without revealing the data itself, are then "
    "aggregated by the server using algorithms such as Federated Averaging (FedAvg). The global model "
    "is iteratively refined through successive rounds of this process until convergence criteria are met.\n\n"
    "Despite its theoretical elegance, federated learning introduces engineering challenges that remain "
    "subjects of active research. Foremost among these is the problem of statistical heterogeneity: "
    "data distributions across client devices are seldom independent and identically distributed (IID), "
    "meaning that local models may diverge significantly from one another. This phenomenon, known as "
    "client drift, can substantially degrade global model performance when naive aggregation strategies "
    "are employed. Researchers have proposed numerous mitigation techniques, including personalised "
    "federated learning, which allows individual clients to retain model parameters tailored to their "
    "local data distribution whilst still benefiting from global knowledge.\n\n"
    "A second critical challenge concerns communication efficiency. Gradient updates, particularly for "
    "large neural network architectures, can be orders of magnitude larger than the original training "
    "data in serialised form. Transmitting such updates across bandwidth-constrained or intermittently "
    "connected networks introduces prohibitive overhead. Gradient compression techniques — including "
    "sparsification, quantisation, and low-rank approximation — have been shown to reduce communication "
    "costs by several orders of magnitude whilst preserving model fidelity to a satisfactory degree.\n\n"
    "Perhaps the most philosophically nuanced challenge, however, is the tension between privacy and "
    "utility. Whilst federated learning inherently reduces the surface area of data exposure, it does "
    "not render systems immune to inference attacks. Gradient inversion attacks, for instance, have "
    "demonstrated that it is possible — under certain conditions — to reconstruct recognisable facsimiles "
    "of training images from gradient updates alone. Differential privacy mechanisms, which inject "
    "calibrated statistical noise into the gradient updates, offer a principled defence against such "
    "attacks, though at the cost of some model accuracy. The calibration of this privacy-utility "
    "trade-off remains one of the defining open problems in the field.\n\n"
    "The practical deployment of federated learning is already well underway in industry. Mobile keyboard "
    "prediction systems, fraud detection pipelines, and personalised health monitoring applications have "
    "all adopted federated approaches to varying degrees of sophistication. As regulatory frameworks such "
    "as the GDPR and the forthcoming EU AI Act continue to tighten restrictions on cross-border data "
    "flows, the strategic imperative for privacy-preserving machine learning will only intensify. Software "
    "engineers entering the field would be well-advised to develop fluency not only in the mathematical "
    "foundations of distributed optimisation, but also in the legal and ethical dimensions of responsible "
    "AI deployment."
)
story.append(Paragraph(passage.replace("\n\n","<br/><br/>"), passage_st))
story.append(Spacer(1,0.2*cm))
story.append(HRFlowable(width="100%",thickness=0.5,color=BORDER))
story.append(Spacer(1,0.15*cm))

story.append(Paragraph("SECTION A — Multiple Choice Questions (2 marks each)", section_hd))
mcqs = [
    ("1","What is the primary privacy advantage of federated learning over conventional machine learning?",2,
     ["A. It uses smaller neural networks that consume less memory.",
      "B. Raw training data never leaves the client device.",
      "C. It eliminates the need for a central coordination server.",
      "D. It automatically encrypts all data at rest."], "B"),
    ("2","The term 'client drift' (paragraph 3) refers to:",2,
     ["A. Devices losing their internet connection during training.",
      "B. The tendency of gradient updates to become corrupted over time.",
      "C. Divergence between local models due to non-IID data distributions.",
      "D. The migration of model parameters from client to server."],"C"),
    ("3","According to the passage, which technique helps reduce communication overhead in federated systems?",2,
     ["A. Differential privacy mechanisms.",
      "B. Federated Averaging (FedAvg) algorithm.",
      "C. Gradient compression techniques such as quantisation.",
      "D. Personalised federated learning with local model parameters."],"C"),
    ("4","Gradient inversion attacks are described as a threat because they can:",2,
     ["A. Intercept model parameters as they travel across the network.",
      "B. Reconstruct training images from gradient updates.",
      "C. Prevent the global model from converging.",
      "D. Force client devices to transmit raw data to the server."],"B"),
    ("5","The author's overall attitude towards federated learning is best described as:",2,
     ["A. Sceptical — the technology has too many unresolved flaws.",
      "B. Neutral — no opinion is expressed.",
      "C. Unconditionally optimistic — all problems have been solved.",
      "D. Cautiously optimistic — promising but with acknowledged challenges."],"D"),
]
for num,text,marks,opts,key in mcqs:
    story.append(q_hdr(num,text,marks))
    for o in opts:
        story.append(opt_row(o[0], o[2:].strip()))
    story.append(ans_box(f"({key}) {[o for o in opts if o.startswith(key)][0][3:]}"))
    story.append(Spacer(1,0.12*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION B — True / False / Not Given (2 marks each)", section_hd))
story.append(info_box("Write TRUE, FALSE, or NOT GIVEN. Base your answer solely on the passage."))
tfng = [
    ("6","Federated learning requires all client devices to be continuously connected throughout training.",2,"FALSE"),
    ("7","The FedAvg algorithm was originally developed by researchers at a European university.",2,"NOT GIVEN"),
    ("8","Differential privacy improves model accuracy compared to standard federated learning.",2,"FALSE"),
    ("9","Mobile keyboard prediction is cited as a real-world application of federated learning.",2,"TRUE"),
    ("10","The GDPR is mentioned as a regulatory factor influencing the adoption of privacy-preserving AI.",2,"TRUE"),
]
for num,text,marks,key in tfng:
    story.append(q_hdr(num,text,marks))
    story.append(blank_line(4*cm))
    story.append(ans_box(key))
    story.append(Spacer(1,0.1*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION C — Vocabulary: Word Meaning in Context (2 marks each)", section_hd))
vocab = [
    ("11","The word <b>proliferation</b> (paragraph 1) is closest in meaning to:",2,
     ["A. decline", "B. rapid spread", "C. regulation", "D. restriction"],"B"),
    ("12","The phrase <b>orders of magnitude</b> (paragraph 4) means:",2,
     ["A. military commands", "B. sequential instructions", "C. very large differences in scale", "D. precise measurements"],"C"),
]
for num,text,marks,opts,key in vocab:
    story.append(q_hdr(num,text,marks))
    for o in opts:
        story.append(opt_row(o[0],o[2:].strip()))
    story.append(ans_box(f"({key})"))
    story.append(Spacer(1,0.1*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION D — Short Answer (3 marks each)", section_hd))
short = [
    ("13","In your own words, explain the 'privacy-utility trade-off' described in paragraph 5. (2–3 sentences)", 3,
     "Differential privacy adds statistical noise to gradient updates to prevent inference attacks, but this noise reduces model accuracy. "
     "Engineers must therefore balance how much privacy protection they apply against how much performance they are willing to sacrifice."),
    ("14","Why does the author recommend that software engineers study both mathematics and legal/ethical dimensions of AI? Refer to the text.", 3,
     "The passage notes that regulatory frameworks like GDPR and the EU AI Act are tightening data restrictions, "
     "so engineers need legal fluency alongside technical skills in distributed optimisation to deploy AI responsibly and compliantly."),
]
for num,text,marks,key in short:
    story.append(q_hdr(num,text,marks))
    for e in write_lines(3):
        story.append(e)
    story.append(ans_box(key))
    story.append(Spacer(1,0.1*cm))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 2 — INVERSION
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("PART 2 — INVERSION", "15 marks | Suggested time: 15 minutes", NAVY))
story.append(Spacer(1,0.2*cm))
story.append(grammar_ref_box(
    "GRAMMAR REFERENCE — Inversion",
    ["Structure: Negative/Limiting Adverb + Auxiliary + Subject + Main Verb",
     "Triggers: Never, Rarely, Seldom, Hardly, Little, Only (after/when/then), Not only",
     "Example: Never have I encountered such a complex algorithm.",
     "Example: Only after the sprint review did the team understand the full scope.",
     "Example: Not only did the server crash, but it also corrupted the database."]
))
story.append(Spacer(1,0.2*cm))

story.append(Paragraph("SECTION A — Multiple Choice: Identify the Correct Inversion (2 marks each)", section_hd))
inv_mcqs = [
    ("15","Choose the correctly inverted sentence:",2,
     ["A. Rarely the system does crash during peak hours.",
      "B. Rarely does the system crash during peak hours.",
      "C. Rarely the system crashes during peak hours.",
      "D. Does rarely the system crash during peak hours."],"B"),
    ("16","Which sentence uses inversion correctly?",2,
     ["A. Only after the deployment we realised the bug was critical.",
      "B. Only after the deployment did we realise the bug was critical.",
      "C. Only after the deployment we did realise the bug was critical.",
      "D. Only after the deployment realised we the bug was critical."],"B"),
    ("17","Select the sentence with correct inversion after 'Not only':",2,
     ["A. Not only the new feature failed, but it also broke existing functionality.",
      "B. Not only did the new feature fail, but it also broke existing functionality.",
      "C. Not only failed the new feature, but it also broke existing functionality.",
      "D. Not only the new feature did fail, but it also broke existing functionality."],"B"),
]
for num,text,marks,opts,key in inv_mcqs:
    story.append(q_hdr(num,text,marks))
    for o in opts:
        story.append(opt_row(o[0],o[2:].strip()))
    story.append(ans_box(f"({key})"))
    story.append(Spacer(1,0.12*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION B — Sentence Transformation (2 marks each)", section_hd))
story.append(info_box("Rewrite each sentence beginning with the word(s) given, so that it has the same meaning. Do not change the meaning."))
inv_trans = [
    ("18","The team had rarely encountered such a severe security vulnerability before.\n→ <b>Rarely…</b>",2,
     "Rarely had the team encountered such a severe security vulnerability before."),
    ("19","We only understood the full impact of the data breach after the audit was completed.\n→ <b>Only after…</b>",2,
     "Only after the audit was completed did we understand the full impact of the data breach."),
    ("20","She not only fixed the critical bug but also refactored the entire authentication module.\n→ <b>Not only…</b>",2,
     "Not only did she fix the critical bug, but she also refactored the entire authentication module."),
    ("21","I have seldom read a more thorough technical specification.\n→ <b>Seldom…</b>",2,
     "Seldom have I read a more thorough technical specification."),
    ("22","He had hardly started the code review when the client called an emergency meeting.\n→ <b>Hardly…</b>",2,
     "Hardly had he started the code review when the client called an emergency meeting."),
]
for num,text,marks,key in inv_trans:
    story.append(q_hdr_ital(num,text,marks))
    for e in write_lines(2):
        story.append(e)
    story.append(ans_box(key))
    story.append(Spacer(1,0.1*cm))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 3 — PROBABILITY & ADJECTIVE + PREPOSITION
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("PART 3 — PROBABILITY & ADJECTIVE + PREPOSITION", "12 marks | Suggested time: 12 minutes", HexColor("#185FA5")))
story.append(Spacer(1,0.2*cm))
story.append(grammar_ref_box(
    "GRAMMAR REFERENCE — Probability & Adjective + Preposition",
    ["Bound to + verb = almost certain to happen  →  'The app is bound to crash under heavy load.'",
     "Unlikely to + verb = low probability  →  'The patch is unlikely to resolve all issues.'",
     "Common Adj+Prep: good AT / bad AT / interested IN / afraid OF / proud OF / responsible FOR / famous FOR / different FROM / capable OF"]
))
story.append(Spacer(1,0.2*cm))

story.append(Paragraph("SECTION A — Probability: Choose the Correct Form (2 marks each)", section_hd))
prob_mcqs = [
    ("23","With such poor test coverage, this deployment ________ to introduce new bugs.",2,
     ["A. is unlikely", "B. is bound", "C. was bound", "D. are bound"],"B"),
    ("24","Given the team's track record, they ________ to deliver the sprint on time.",2,
     ["A. is bound", "B. are unlikely", "C. are bound", "D. will unlikely"],"C"),
    ("25","The legacy system ________ to support the new authentication protocol without significant refactoring.",2,
     ["A. is bound", "B. is unlikely", "C. are unlikely", "D. bounds"],"B"),
]
for num,text,marks,opts,key in prob_mcqs:
    story.append(q_hdr(num,text,marks))
    for o in opts:
        story.append(opt_row(o[0],o[2:].strip()))
    story.append(ans_box(f"({key})"))
    story.append(Spacer(1,0.12*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION B — Adjective + Preposition: Fill in the Correct Preposition (1 mark each)", section_hd))
story.append(info_box("Write the correct preposition in each gap."))
adj_prep = [
    ("26","She is highly skilled and particularly good ________ designing scalable microservices architectures.",1,"at"),
    ("27","The junior developer was afraid ________ presenting the system design to the client for the first time.",1,"of"),
    ("28","Our framework is fundamentally different ________ the one described in the original paper.",1,"from"),
    ("29","The CTO is responsible ________ all technical decisions made during the product lifecycle.",1,"for"),
    ("30","Many graduates are not aware ________ the ethical implications of the AI systems they build.",1,"of"),
    ("31","Python is famous ________ its readability and the strength of its open-source ecosystem.",1,"for"),
]
for num,text,marks,key in adj_prep:
    story.append(q_hdr(num,text,marks))
    story.append(blank_line(2*cm))
    story.append(ans_box(key))
    story.append(Spacer(1,0.08*cm))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 4 — WISHES, IF ONLY & IT'S TIME
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("PART 4 — WISHES, IF ONLY & IT'S TIME", "13 marks | Suggested time: 13 minutes", HexColor("#3C3489")))
story.append(Spacer(1,0.2*cm))
story.append(grammar_ref_box(
    "GRAMMAR REFERENCE — Wish / If Only / It's Time",
    ["I wish / If only + PAST SIMPLE = unreal present  →  'I wish I knew how to fix this bug.'",
     "I wish / If only + PAST PERFECT = past regret  →  'I wish I had written better unit tests.'",
     "It's (high) time + subject + PAST SIMPLE = something should happen now",
     "  →  'It's high time the team adopted a proper version control strategy.'",
     "NOTE: Even though the situation is present, the PAST SIMPLE is used after 'It's time'."]
))
story.append(Spacer(1,0.2*cm))

story.append(Paragraph("SECTION A — Multiple Choice (2 marks each)", section_hd))
wish_mcqs = [
    ("32","Choose the grammatically correct sentence expressing a present regret:",2,
     ["A. I wish I know more about cryptography.",
      "B. I wish I had known more about cryptography right now.",
      "C. I wish I knew more about cryptography.",
      "D. I wish I have known more about cryptography."],"C"),
    ("33","Which sentence correctly expresses regret about a past event?",2,
     ["A. If only I tested the API endpoints before the launch.",
      "B. If only I had tested the API endpoints before the launch.",
      "C. If only I would test the API endpoints before the launch.",
      "D. If only I have tested the API endpoints before the launch."],"B"),
    ("34","Select the correct 'It's time' sentence:",2,
     ["A. It's high time the team updates its security protocols.",
      "B. It's high time the team updated its security protocols.",
      "C. It's high time the team will update its security protocols.",
      "D. It's high time the team had updated its security protocols."],"B"),
]
for num,text,marks,opts,key in wish_mcqs:
    story.append(q_hdr(num,text,marks))
    for o in opts:
        story.append(opt_row(o[0],o[2:].strip()))
    story.append(ans_box(f"({key})"))
    story.append(Spacer(1,0.12*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION B — Fill in the Blank (1 mark each)", section_hd))
story.append(info_box("Complete each sentence using the correct form of the verb in brackets. Do not add extra words."))
wish_fill = [
    ("35","I wish our CI/CD pipeline ________ (run) faster — the build times are unacceptable.",1,"ran"),
    ("36","If only the team ________ (implement) input validation before the SQL injection attack occurred.",1,"had implemented"),
    ("37","It's high time the organisation ________ (adopt) a formal data governance policy.",1,"adopted"),
    ("38","She wishes she ________ (attend) the zero-trust architecture conference last year.",1,"had attended"),
    ("39","If only we ________ (have) access to more computational resources right now.",1,"had"),
    ("40","It's time the developers ________ (write) proper documentation for the API endpoints.",1,"wrote"),
    ("41","I wish I ________ (understand) the mathematics behind transformer attention mechanisms.",1,"understood"),
]
for num,text,marks,key in wish_fill:
    story.append(q_hdr(num,text,marks))
    story.append(blank_line(3*cm))
    story.append(ans_box(key))
    story.append(Spacer(1,0.08*cm))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 5 — PREFERENCES
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("PART 5 — PREFERENCES: WOULD RATHER / WOULD PREFER", "8 marks | Suggested time: 8 minutes", HexColor("#0F6E56")))
story.append(Spacer(1,0.2*cm))
story.append(grammar_ref_box(
    "GRAMMAR REFERENCE — Preferences",
    ["Would rather + subject + PAST SIMPLE (about others' actions):",
     "  →  'I would rather you submitted the code before the deadline.'",
     "Would rather + BASE VERB (about own actions):",
     "  →  'I would rather work remotely than commute three hours daily.'",
     "Would prefer + TO + INFINITIVE:",
     "  →  'She would prefer to conduct the code review asynchronously.'",
     "Would prefer + noun/gerund + to + noun/gerund:",
     "  →  'I would prefer using Git Flow to working directly on main.'"]
))
story.append(Spacer(1,0.2*cm))

story.append(Paragraph("SECTION A — Choose the Correct Form (2 marks each)", section_hd))
pref_mcqs = [
    ("42","Select the grammatically correct preference sentence:",2,
     ["A. I would rather you pushed your changes before the standup.",
      "B. I would rather you push your changes before the standup.",
      "C. I would rather you will push your changes before the standup.",
      "D. I would rather you had pushed your changes before the standup."],"A"),
    ("43","Which sentence uses 'would prefer' correctly?",2,
     ["A. She would prefer review the pull request herself.",
      "B. She would prefer to review the pull request herself.",
      "C. She would prefer reviewing rather than to review.",
      "D. She would prefer that review the pull request."],"B"),
]
for num,text,marks,opts,key in pref_mcqs:
    story.append(q_hdr(num,text,marks))
    for o in opts:
        story.append(opt_row(o[0],o[2:].strip()))
    story.append(ans_box(f"({key})"))
    story.append(Spacer(1,0.12*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION B — Sentence Transformation (2 marks each)", section_hd))
story.append(info_box("Rewrite each sentence using the prompt given, keeping the same meaning."))
pref_trans = [
    ("44","I prefer to use TypeScript rather than plain JavaScript for large projects.\n→ <b>I would rather…</b>",2,
     "I would rather use TypeScript than plain JavaScript for large projects."),
    ("45","The manager wants us to write unit tests before pushing to main.\n→ <b>The manager would rather we…</b>",2,
     "The manager would rather we wrote unit tests before pushing to main."),
    ("46","Working in an Agile team suits her better than working in a waterfall environment.\n→ <b>She would prefer…</b>",2,
     "She would prefer to work in an Agile team than in a waterfall environment."),
]
for num,text,marks,key in pref_trans:
    story.append(q_hdr_ital(num,text,marks))
    for e in write_lines(2):
        story.append(e)
    story.append(ans_box(key))
    story.append(Spacer(1,0.1*cm))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 6 — TENSES + REPORTED SPEECH + INDIRECT QUESTIONS
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("PART 6 — TENSES · REPORTED SPEECH · INDIRECT QUESTIONS", "20 marks | Suggested time: 22 minutes", HexColor("#993C1D")))
story.append(Spacer(1,0.2*cm))
story.append(grammar_ref_box(
    "GRAMMAR REFERENCE — Tense Backshift in Reported Speech",
    ["Present Simple → Past Simple:  'I work' → she said she worked",
     "Present Perfect → Past Perfect:  'I have finished' → he said he had finished",
     "Past Simple → Past Perfect:  'It crashed' → they said it had crashed",
     "Future (will) → Conditional (would):  'I will deploy' → she said she would deploy",
     "Can → Could  |  May → Might  |  Must → Had to",
     "Time changes:  now→then | today→that day | tomorrow→the next day | yesterday→the day before",
     "Indirect Question: NO inversion — 'Where do you store it?' → Could you tell me where you store it?"]
))
story.append(Spacer(1,0.2*cm))

story.append(Paragraph("SECTION A — Tense: Fill in the Blank (2 marks each)", section_hd))
tense_qs = [
    ("47","The architecture review ________ (complete) before the board meeting. <i>Use Past Perfect.</i>",2,
     "had been completed"),
    ("48","Our team ________ (migrate) microservices to the new Kubernetes cluster for two months and the process is ongoing. <i>Use Present Perfect Continuous.</i>",2,
     "has been migrating"),
    ("49","If the engineers ________ (document) the API properly, the integration team ________ (not struggle). <i>Use Third Conditional.</i>",2,
     "had documented / would not have struggled"),
    ("50","Federated learning ________ (gain) significant traction in industry since 2020. <i>Use Present Perfect.</i>",2,
     "has gained"),
]
for num,text,marks,key in tense_qs:
    story.append(q_hdr(num,text,marks))
    story.append(blank_line())
    story.append(ans_box(key))
    story.append(Spacer(1,0.1*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION B — Reported Speech Transformation (2 marks each)", section_hd))
story.append(info_box("Rewrite each direct speech sentence as reported speech. Apply all necessary changes."))
reported = [
    ("51",'"We have been optimising the gradient compression algorithm all week," said the ML engineer.',2,
     "The ML engineer said (that) they had been optimising the gradient compression algorithm all week."),
    ("52",'"You must implement differential privacy before the product launches," the CTO told the team.',2,
     "The CTO told the team (that) they had to implement differential privacy before the product launched."),
    ("53",'"I will present the federated learning results at the conference tomorrow," said Dr Yasmine.',2,
     "Dr Yasmine said (that) she would present the federated learning results at the conference the next day / the following day."),
    ("54",'"Can you explain why the global model failed to converge?" the research lead asked the intern.',2,
     "The research lead asked the intern if/whether they could explain why the global model had failed to converge."),
]
for num,text,marks,key in reported:
    story.append(q_hdr_ital(num,text,marks))
    for e in write_lines(2):
        story.append(e)
    story.append(ans_box(key))
    story.append(Spacer(1,0.1*cm))

story.append(Spacer(1,0.15*cm))
story.append(Paragraph("SECTION C — Indirect Questions (2 marks each)", section_hd))
story.append(info_box("Convert each direct question to an indirect question using the starter provided."))
indirect = [
    ("55",'"Why does client drift degrade model performance?" → <b>I was wondering…</b>',2,
     "I was wondering why client drift degrades model performance."),
    ("56",'"Has the privacy budget been calibrated correctly?" → <b>Do you know if…</b>',2,
     "Do you know if / whether the privacy budget has been calibrated correctly?"),
    ("57",'"Where does the gradient aggregation happen in the architecture?" → <b>Could you tell me…</b>',2,
     "Could you tell me where the gradient aggregation happens in the architecture?"),
]
for num,text,marks,key in indirect:
    story.append(q_hdr_ital(num,text,marks))
    for e in write_lines(2):
        story.append(e)
    story.append(ans_box(key))
    story.append(Spacer(1,0.1*cm))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 7 — ERROR CORRECTION
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("PART 7 — ERROR CORRECTION: PARAGRAPH EDITING", "12 marks | Suggested time: 10 minutes", HexColor("#854F0B")))
story.append(Spacer(1,0.2*cm))
story.append(info_box(
    "The paragraph below contains exactly 12 errors covering ALL grammar topics in this examination: "
    "inversion, probability, adjective+preposition, wish/if only, it's time, preferences, "
    "reported speech, indirect questions, and tense. Each error is worth 1 mark. "
    "Underline the error and write the correction in the table below."
))
story.append(Spacer(1,0.15*cm))

err_para = (
    "The lead architect rarely has acknowledged that the federated learning model was bound of failure "
    "without proper gradient compression. During the retrospective, she told the team that they will need "
    "to reconsider their approach immediately. She also asked where did the gradient updates go after "
    "aggregation — a question that exposed a fundamental gap in documentation. Only after a thorough audit "
    "the engineering team realised the extent of the problem. It is high time the organisation takes "
    "privacy seriously. I wish we have adopted differential privacy from the outset; if only the team had "
    "tested the system under adversarial conditions. Many engineers are now afraid from inference attacks "
    "and proud for their growing awareness of this threat. The CTO, who is responsible of all technical "
    "decisions, would rather the team spend more time on security testing. She said she would prefer "
    "conduct a red team exercise before the next deployment cycle begins."
)
story.append(Paragraph(f"<i>{err_para}</i>",
    S("ep2",fontSize=10,fontName="Helvetica-Oblique",textColor=black,
      leading=17,alignment=TA_JUSTIFY,spaceAfter=8)))

err_table_data = [
    [Paragraph("<b>#</b>",label_st), Paragraph("<b>Error in text</b>",label_st),
     Paragraph("<b>Grammar topic</b>",label_st), Paragraph("<b>Correction</b>",label_st)],
    ["1","rarely has acknowledged","Inversion","rarely has the lead architect acknowledged / Rarely did the lead architect acknowledge"],
    ["2","bound of failure","Probability + Preposition","bound to fail"],
    ["3","will need","Reported speech (future→conditional)","would need"],
    ["4","where did the gradient updates go","Indirect question (no inversion)","where the gradient updates went"],
    ["5","Only after a thorough audit the engineering team realised","Inversion after Only","Only after a thorough audit did the engineering team realise"],
    ["6","It is high time the organisation takes","It's time + past simple","It is high time the organisation took"],
    ["7","I wish we have adopted","Wish + past perfect (past regret)","I wish we had adopted"],
    ["8","afraid from","Adjective + preposition","afraid of"],
    ["9","proud for","Adjective + preposition","proud of"],
    ["10","responsible of","Adjective + preposition","responsible for"],
    ["11","would rather the team spend","Would rather + subject + past simple","would rather the team spent"],
    ["12","would prefer conduct","Would prefer + to + infinitive","would prefer to conduct"],
]
err_t = Table(err_table_data, colWidths=[0.6*cm, 4.2*cm, 3.8*cm, 5.4*cm])
err_t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_NAVY),
    ("TEXTCOLOR",(0,0),(-1,0),white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),8),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_AMBER]),
    ("GRID",(0,0),(-1,-1),0.5,BORDER),
    ("TOPPADDING",(0,0),(-1,-1),4),
    ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("LEFTPADDING",(0,0),(-1,-1),5),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("WORDWRAP",(0,0),(-1,-1),True),
]))
story.append(err_t)
story.append(Spacer(1,0.25*cm))
story.append(Paragraph("Student Answer Grid:", label_st))
for i in range(1,13):
    d = [[Paragraph(f"Error {i}:", label_st), ""]]
    t = Table(d, colWidths=[2*cm, INNER-2.2*cm])
    t.setStyle(TableStyle([
        ("LINEBELOW",(1,0),(1,0),0.5,BORDER),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("LEFTPADDING",(0,0),(-1,-1),0),
    ]))
    story.append(t)

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 8 — EXTENDED WRITING
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("PART 8 — EXTENDED WRITING: ACADEMIC ESSAY", "10 marks | Suggested time: 25 minutes", DARK_NAVY))
story.append(Spacer(1,0.2*cm))
story.append(info_box(
    "Choose ONE task. Write 200–250 words. Use a range of C1 structures from across this examination: "
    "inversion, wishes, it's time, preferences, probability expressions, adjective+preposition, "
    "reported speech, and complex tenses. Task Achievement (4) + Lexical Range (3) + Grammar Accuracy (3)."
))
story.append(Spacer(1,0.2*cm))

for task_title, task_body, bg, border in [
    ("<b>TASK A — Argumentative Essay</b>",
     "Some engineers argue that data privacy and machine learning performance are irreconcilably "
     "opposed — that any meaningful privacy guarantee will unacceptably degrade model accuracy. "
     "Others contend that techniques such as federated learning and differential privacy "
     "can reconcile these two objectives without significant sacrifice.<br/><br/>"
     "Present both perspectives. Refer where appropriate to the passage in Part 1. "
     "Give your own position with clear justification.",
     LIGHT_BLUE, MID_BLUE),
    ("<b>TASK B — Problem–Solution Essay</b>",
     "The rapid expansion of distributed AI systems has created new challenges for software "
     "engineers who must balance innovation with security, privacy, and regulatory compliance.<br/><br/>"
     "Identify the three most significant challenges facing software engineers in this context "
     "and propose specific, practical solutions for each. Use technical vocabulary accurately "
     "and support your argument with examples from your knowledge of the field.",
     LIGHT_AMBER, AMBER),
]:
    d = [[Paragraph(task_title, S("tth",fontSize=10,fontName="Helvetica-Bold",textColor=DARK_NAVY))],
         [Paragraph(task_body, body_st)]]
    t = Table(d, colWidths=[INNER])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg),
        ("BOX",(0,0),(-1,-1),0.5,border),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),12),
        ("RIGHTPADDING",(0,0),(-1,-1),12),
    ]))
    story.append(t)
    story.append(Spacer(1,0.15*cm))

story.append(Paragraph("Circle your chosen task:     TASK A     /     TASK B", q_text_st))
story.append(Spacer(1,0.15*cm))
story.append(Paragraph("Your response:", label_st))
for _ in range(20):
    story.append(blank_line())
    story.append(Spacer(1,3))
story.append(Paragraph("Word count: __________", label_st))
story.append(Spacer(1,0.3*cm))

story.append(tip_box(
    "For maximum marks, try to use: inversion ('Rarely have I encountered...'), "
    "wishes ('I wish the field had developed...'), preferences ('I would rather engineers focused...'), "
    "probability ('This approach is bound to...'), and complex conditionals."
))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# RUBRIC & BAND EQUIVALENCE
# ════════════════════════════════════════════════════════════════════════════
story.append(part_banner("WRITING RUBRIC & CEFR BAND EQUIVALENCE — EXAMINER USE ONLY", "", HexColor("#444441")))
story.append(Spacer(1,0.25*cm))

rub = [
    [Paragraph("<b>Criterion</b>",label_st), Paragraph("<b>Full marks</b>",label_st),
     Paragraph("<b>Partial</b>",label_st), Paragraph("<b>Minimal</b>",label_st),
     Paragraph("<b>Score</b>",label_st)],
    ["Task Achievement (4)","All points addressed; well-argued, specific","Most points; some underdevelopment","Vague or off-task","  /4"],
    ["Lexical Range (3)","C1 vocabulary; accurate collocations; paraphrasing","B2 vocabulary; some errors","Limited range; frequent errors","  /3"],
    ["Grammar Accuracy (3)","Complex structures (inversion, wishes, etc.) used correctly","Mix of simple/complex; some errors","Predominantly simple; many errors","  /3"],
]
rub_t = Table(rub, colWidths=[3.5*cm,4.2*cm,3.8*cm,2.8*cm,1.2*cm])
rub_t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_NAVY),
    ("TEXTCOLOR",(0,0),(-1,0),white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),8),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_GRAY]),
    ("GRID",(0,0),(-1,-1),0.5,BORDER),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),5),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("WORDWRAP",(0,0),(-1,-1),True),
]))
story.append(rub_t)
story.append(Spacer(1,0.35*cm))

story.append(Paragraph("CEFR BAND & IELTS EQUIVALENCE", section_hd))
band_data = [
    [Paragraph("<b>Score</b>",label_st), Paragraph("<b>CEFR</b>",label_st),
     Paragraph("<b>IELTS</b>",label_st), Paragraph("<b>Descriptor</b>",label_st)],
    ["108–120","C2 Mastery","8.5–9.0","Near-native proficiency; mastery of all advanced structures"],
    ["96–107","C1 Advanced","7.5–8.0","Effective operational command; sophisticated language use"],
    ["80–95","B2 Upper","6.5–7.0","Generally effective; some inaccuracies in complex structures"],
    ["60–79","B2 Lower","5.5–6.0","Limited command of complex grammar; basic communication adequate"],
    ["Below 60","B1","4.0–5.0","Partial command; frequent errors in advanced structures"],
]
band_t = Table(band_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 8.0*cm])
band_t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),DARK_NAVY),
    ("TEXTCOLOR",(0,0),(-1,0),white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),9),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_GRAY]),
    ("GRID",(0,0),(-1,-1),0.5,BORDER),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),7),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
]))
story.append(band_t)
story.append(Spacer(1,0.4*cm))
story.append(HRFlowable(width="100%",thickness=0.5,color=BORDER))
story.append(Spacer(1,0.2*cm))
story.append(Paragraph(
    "Examiner signature: _______________________   Part 8 score: _______ / 10   TOTAL: _______ / 120",
    S("fin",fontSize=10,fontName="Helvetica",textColor=GRAY,alignment=TA_CENTER)
))

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("Done:", OUTPUT)